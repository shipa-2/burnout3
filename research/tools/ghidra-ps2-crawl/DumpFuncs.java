import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import java.io.FileWriter;

public class DumpFuncs extends GhidraScript {
    @Override
    public void run() throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager();
        FileWriter out = new FileWriter("/tmp/claude_ghidra_funcs.tsv");
        int count = 0;
        for (Function f : fm.getFunctions(true)) {
            long size = f.getBody().getNumAddresses();
            out.write(f.getEntryPoint().toString() + "\t" + f.getName() + "\t" + size + "\n");
            count++;
        }
        out.close();
        println("Dumped " + count + " functions");
    }
}
