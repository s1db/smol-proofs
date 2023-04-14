import os
from proof import Proof
from stack_proof import Proof as StackProof
from smol_proof import make_smol
import subprocess
import time
from visualizer import core, create_graph
# get the names of all files in the smart_table_proofs directory
# OPB_LOCATION = "magic_series_proofs/"
# OPB_LOCATION = "smart_table_proofs/"
OPB_LOCATION = "sip_proofs/"
files = os.listdir(OPB_LOCATION)


files = sorted(files,key=lambda x: os.stat(os.path.join(OPB_LOCATION, x)).st_size)
files = [f for f in files if f.endswith(".opb") and not f.startswith("smol_")]

LOUD = False

for file in files:
    file = file[:-4]
    print(file)
    start = time.process_time()
    proof = Proof(OPB_LOCATION+file, loud=LOUD)
    print("    1️⃣  normal rup file created", time.process_time() - start)
    start = time.process_time()
    stack_proof = StackProof(OPB_LOCATION+file, backwards=True, loud=LOUD)
    print("    1️⃣  stack rup file created", time.process_time() - start)
    SMOL_PROOF_LOCATION = OPB_LOCATION
    i = make_smol(file,OPB_LOCATION, OPB_LOCATION)
    j = make_smol("stack_"+file,OPB_LOCATION, OPB_LOCATION)    
    print("    2️⃣  smol files created")

    print("    3️⃣  normal kept:", str(i[0])+" clauses in original proof "+str(i[1])+" clauses in smol proof")
    print("    3️⃣  stack kept :", str(j[0])+" clauses in original proof "+str(j[1])+" clauses in smol proof")
    output1 = subprocess.check_output(f"veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}{file}.veripb", shell=True)
    output2 = subprocess.check_output(f"veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}smol_{file}.veripb", shell=True)
    output3 = subprocess.check_output(f"veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}smol_stack_{file}.veripb", shell=True)
    if "succeeded" not in str(output1) and "succeeded" not in str(output2) and "succeeded" not in str(output3):
        print("    🔴", str(output1, "utf-8"), str(output2, "utf-8"), str(output3, "utf-8"))
    normal = 0
    forward = 0
    backward = 0
    for i in range(5):
        output1 = subprocess.check_output(f"/usr/bin/time -f \"%e\" sh -c 'veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}{file}.veripb' 2>&1", shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip().split("\n")[-1]
        output2 = subprocess.check_output(f"/usr/bin/time -f \"%e\" sh -c 'veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}smol_{file}.veripb' 2>&1", shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip().split("\n")[-1]
        output3 = subprocess.check_output(f"/usr/bin/time -f \"%e\" sh -c 'veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}smol_stack_{file}.veripb' 2>&1", shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip().split("\n")[-1]
        cmd = f"/usr/bin/time -f \"%e\" sh -c 'veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}{file}.veripb' 2>&1"
        normal += float(output1)
        forward += float(output2)
        backward += float(output3)
    print("    4️⃣  normal time:", normal/5)
    print("    4️⃣  forward time:", forward/5)
    print("    4️⃣  backward time:", backward/5)
    graph_core = core(file)
    create_graph(graph_core, file, "images_"+OPB_LOCATION)
    graph_core = core("stack_"+file)
    create_graph(graph_core, "stack_"+file, "images_"+OPB_LOCATION)
    # else:
    #     print("    🟢", str(output1, "utf-8"), str(output2, "utf-8"), str(output3, "utf-8"))
    #     raise Exception("proof failed")