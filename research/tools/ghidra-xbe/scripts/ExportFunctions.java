import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import java.io.FileWriter;
import java.io.PrintWriter;

public class ExportFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter pw = new PrintWriter(new FileWriter("/tmp/burnout3_functions.csv"));
        pw.println("address,name,size,named");
        for (Function f : fm.getFunctions(true)) {
            long size = f.getBody().getNumAddresses();
            boolean named = !f.getName().startsWith("FUN_");
            pw.println(f.getEntryPoint() + "," + f.getName().replace(",", ";") + "," + size + "," + named);
        }
        pw.close();
        println("EXPORTED");
    }
}
