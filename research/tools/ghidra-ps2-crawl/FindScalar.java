import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import java.io.*;
import java.util.*;

public class FindScalar extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath = args[args.length - 1];
        Set<Long> targets = new HashSet<>();
        for (int i = 0; i < args.length - 1; i++) {
            targets.add(Long.parseLong(args[i], 16));
        }
        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        for (Function f : fm.getFunctions(true)) {
            AddressSetView body = f.getBody();
            InstructionIterator it = listing.getInstructions(body, true);
            Set<Long> hits = new HashSet<>();
            while (it.hasNext()) {
                Instruction insn = it.next();
                for (int i = 0; i < insn.getNumOperands(); i++) {
                    Object[] objs = insn.getOpObjects(i);
                    for (Object o : objs) {
                        if (o instanceof Scalar) {
                            long v = ((Scalar) o).getUnsignedValue();
                            if (targets.contains(v)) hits.add(v);
                        }
                    }
                }
            }
            if (!hits.isEmpty()) {
                out.println(f.getEntryPoint() + "\t" + f.getName() + "\t" + f.getBody().getNumAddresses() + "\t" + hits);
            }
        }
        out.close();
        println("done");
    }
}
