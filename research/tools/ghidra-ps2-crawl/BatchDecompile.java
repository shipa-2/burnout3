import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import java.io.*;
import java.util.*;

public class BatchDecompile extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String inPath = args[0];
        String outPath = args[1];
        BufferedReader in = new BufferedReader(new FileReader(inPath));
        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        String line;
        while ((line = in.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) continue;
            Address addr;
            try {
                addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(line);
            } catch (Exception e) {
                continue;
            }
            Function f = getFunctionAt(addr);
            if (f == null) {
                f = currentProgram.getFunctionManager().getFunctionContaining(addr);
            }
            if (f == null) {
                if (getInstructionAt(addr) == null) {
                    try { disassemble(addr); } catch (Exception e) {}
                }
                try { f = createFunction(addr, null); } catch (Exception e) {}
            }
            out.println("===FUNC:" + line + "===");
            if (f == null) {
                out.println("NOFUNC");
                continue;
            }
            out.println("REALADDR:" + f.getEntryPoint());
            DecompileResults res = decomp.decompileFunction(f, 30, monitor);
            if (res != null && res.decompileCompleted()) {
                out.println(res.getDecompiledFunction().getC());
            } else {
                out.println("DECOMPFAIL");
            }
        }
        in.close();
        out.close();
        println("done");
    }
}
