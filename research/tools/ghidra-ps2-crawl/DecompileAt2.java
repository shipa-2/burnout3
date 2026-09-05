import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.symbol.SourceType;
import java.io.FileWriter;

public class DecompileAt2 extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String addrStr = args[0];
        String outPath = args[1];
        Address addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(addrStr);
        Function f = getFunctionAt(addr);
        if (f == null) {
            f = currentProgram.getFunctionManager().getFunctionContaining(addr);
        }
        if (f == null) {
            // force disassembly + function creation
            if (getInstructionAt(addr) == null) {
                disassemble(addr);
            }
            f = createFunction(addr, null);
        }
        FileWriter out = new FileWriter(outPath);
        if (f == null) {
            out.write("STILL NO FUNCTION AT " + addrStr + "\n");
            out.close();
            return;
        }
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        DecompileResults res = decomp.decompileFunction(f, 60, monitor);
        if (res != null && res.decompileCompleted()) {
            out.write("// " + f.getName() + " @ " + f.getEntryPoint() + " bodySize=" + f.getBody().getNumAddresses() + "\n");
            out.write(res.getDecompiledFunction().getC());
        } else {
            out.write("DECOMPILE FAILED for " + f.getName() + "\n");
        }
        out.close();
        println("wrote " + outPath);
    }
}
