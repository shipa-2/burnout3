import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.program.model.address.Address;

public class CheckAddr extends GhidraScript {
    @Override
    public void run() throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager();
        println("TOTAL_FUNCTIONS=" + fm.getFunctionCount());

        Address addr = currentProgram.getAddressFactory().getAddress("0x0003c8a0");
        Function func = fm.getFunctionAt(addr);
        if (func == null) {
            func = fm.getFunctionContaining(addr);
        }
        if (func != null) {
            println("FUNC_AT_0x3c8a0=" + func.getName() + " @ " + func.getEntryPoint());
        } else {
            println("FUNC_AT_0x3c8a0=NONE");
        }

        SymbolTable st = currentProgram.getSymbolTable();
        for (Symbol s : st.getSymbols(addr)) {
            println("SYMBOL: " + s.getName() + " source=" + s.getSource());
        }

        int named = 0;
        int defaultNamed = 0;
        for (Function f : fm.getFunctions(true)) {
            if (f.getName().startsWith("FUN_")) {
                defaultNamed++;
            } else {
                named++;
            }
        }
        println("NAMED_FUNCTIONS=" + named);
        println("DEFAULT_FUN_NAMES=" + defaultNamed);
    }
}
