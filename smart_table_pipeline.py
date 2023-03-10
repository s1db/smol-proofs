import os
from proof import Proof
from smol_proof import make_smol
import subprocess
# get the names of all files in the smart_table_proofs directory
OPB_LOCATION = "smart_table_proofs/"
files = os.listdir(OPB_LOCATION)
# failing_files = ["random_table_3vars_301.opb", "random_table_4vars_93.opb", "random_table_3vars_244.opb", "random_table_3vars_199.opb", "random_table_4vars_55.opb"]

files = sorted(files,key=lambda x: os.stat(os.path.join(OPB_LOCATION, x)).st_size)
files = [f for f in files if f.endswith(".opb") and not f.startswith("smol_")]



t= {}
for file in files:
    file = file[:-4]
    print(file)
    proof = Proof(OPB_LOCATION+file)
    print("    1️⃣  rup file created")
    SMOL_PROOF_LOCATION = "20230301-sip-proof-logs/"
    i = make_smol(file,OPB_LOCATION, "20230301-sip-proof-logs/")
    print("    2️⃣  smol file created")
    t[file] = i
    print("    3️⃣  kept:", str(round(i[1]/i[0],4)*100)+"%")
    output = subprocess.check_output(f"veripb {OPB_LOCATION}{file}.opb {SMOL_PROOF_LOCATION}smol_{file}.veripb", shell=True)
    if "succeeded":
        print("    🟢", str(output, "utf-8"))
    else:
        print("    🔴", str(output, "utf-8"))