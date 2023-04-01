import os
from proof import Proof
from stack_proof import Proof as StackProof
from smol_proof import make_smol
import subprocess
import time

# get the names of all files in the smart_table_proofs directory
OPB_LOCATION = "magic_series_proofs/"
files = os.listdir(OPB_LOCATION)


files = sorted(files,key=lambda x: os.stat(os.path.join(OPB_LOCATION, x)).st_size)
files = [f for f in files if f.endswith(".opb") and not f.startswith("smol_")]



for file in files:
    file = file[:-4]
    print(file)
    start = time.process_time()
    proof = Proof(OPB_LOCATION+file, loud=False)
    print("    1️⃣  normal rup file created", time.process_time() - start)
    start = time.process_time()
    stack_proof = StackProof(OPB_LOCATION+file, backwards=True, loud=False)
    print("    1️⃣  stack rup file created", time.process_time() - start)
    SMOL_PROOF_LOCATION = OPB_LOCATION
    i = make_smol(file,OPB_LOCATION, OPB_LOCATION)
    j = make_smol("stack_"+file,OPB_LOCATION, OPB_LOCATION)    
    print("    2️⃣  smol file created")

    print("    3️⃣  normal kept:", str(round(i[1]/i[0],4)*100)+"% : "+str(i[0])+" clauses in original proof "+str(i[1])+" clauses in smol proof")
    print("    4️⃣  stack kept :", str(round(j[1]/j[0],4)*100)+"% : "+str(i[0])+" clauses in original proof "+str(i[1])+" clauses in smol proof")
    start = time.process_time_ns()
    output1 = subprocess.check_output(f"veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}{file}.veripb", shell=True)
    print("    TIME TAKEN TO CHECK:", time.process_time_ns() - start)
    start = time.process_time_ns()
    output1 = subprocess.check_output(f"veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}smol_{file}.veripb", shell=True)
    print("    TIME TAKEN TO CHECK:", time.process_time_ns() - start)
    start = time.process_time_ns()
    output2 = subprocess.check_output(f"veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}smol_stack_{file}.veripb", shell=True)
    print("    TIME TAKEN TO CHECK:", time.process_time_ns() - start)
    if "failed" not in str(output1) and "failed" not in str(output2):
        print("    🟢", str(output1, "utf-8"), str(output2, "utf-8"))
    else:
        print("    🔴", str(output1, "utf-8"), str(output2, "utf-8"))