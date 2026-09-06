import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

// For GTASSERT-bearing Xbox debug builds: map each embedded source-file string to
// the containing function of every direct reference to that string.
public class BatchSourceFileXrefs extends GhidraScript {
    private static String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException("usage: <source-file-list> <output.csv>");
        }

        Memory memory = currentProgram.getMemory();
        BufferedReader in = new BufferedReader(new FileReader(args[0]));
        PrintWriter out = new PrintWriter(new FileWriter(args[1]));
        out.println("source_file,string_address,function_address");
        Set<String> emitted = new TreeSet<>();
        String sourceFile;
        while ((sourceFile = in.readLine()) != null) {
            sourceFile = sourceFile.trim();
            if (sourceFile.isEmpty()) continue;
            int separator = Math.max(sourceFile.lastIndexOf('\\'), sourceFile.lastIndexOf('/'));
            String basename = separator >= 0 ? sourceFile.substring(separator + 1) : sourceFile;
            byte[] needle = basename.getBytes(StandardCharsets.US_ASCII);
            for (MemoryBlock block : memory.getBlocks()) {
                Address cursor = block.getStart();
                Address end = block.getEnd();
                while (cursor != null && cursor.compareTo(end) <= 0) {
                    Address hit = memory.findBytes(cursor, end, needle, null, true, monitor);
                    if (hit == null) break;
                    // References point at the beginning of the complete path, while
                    // the search hit begins at its basename. Walk back to that path.
                    Address stringStart = hit;
                    for (int back = 1; back <= 512; back++) {
                        Address candidate = hit.subtract(back);
                        if (candidate == null || !memory.contains(candidate)) break;
                        if (memory.getByte(candidate) == 0) break;
                        stringStart = candidate;
                    }
                    Reference[] refs = getReferencesTo(stringStart);
                    for (Reference ref : refs) {
                        Function function = getFunctionContaining(ref.getFromAddress());
                        if (function == null) continue;
                        String key = sourceFile + "," + stringStart + "," + function.getEntryPoint();
                        if (emitted.add(key)) {
                            out.println(csv(sourceFile) + "," + stringStart + "," + function.getEntryPoint());
                        }
                    }
                    cursor = hit.next();
                }
            }
        }
        in.close();
        out.close();
        println("wrote " + emitted.size() + " source xref rows");
    }
}
