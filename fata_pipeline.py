import os
from proof import Proof
from smol_proof import make_smol
import subprocess
from stack_proof import Proof as StackProof
# get the names of all files in the smart_table_proofs directory
OPB_LOCATION = "../../ciaran/20230301-sip-proof-logs/"
files = os.listdir(OPB_LOCATION)


all_file_sizes = {}
for file in files:
    all_file_sizes[file] = os.stat(OPB_LOCATION+file).st_size



# Sort the file names by size
files = sorted(all_file_sizes, key=all_file_sizes.get)
files = [f for f in files if f.endswith(".veripb")]
files = [f[:-7] for f in files]
avg_file_size = {f:((all_file_sizes[f+".opb"]+all_file_sizes[f+".veripb"])/2) for f in files}
files = sorted(avg_file_size, key=avg_file_size.get)
files = [f+".opb" for f in files]
files = [f for f in files if not f.startswith("all-meshes")]

SMOL_PROOF_LOCATION = "20230301-sip-proof-logs/"


for file in files:
    file = file[:-4]
    print(file)
    if not os.path.exists("rup/"+file+".rup"):
        proof = Proof(OPB_LOCATION+file)
        print("    1️⃣  rup file created")
    else:
        print("    1️⃣  rup file already exists")
    try:
        i = make_smol(file,OPB_LOCATION, "20230301-sip-proof-logs/")
        print("    2️⃣  smol file created")
        print("    3️⃣  kept:", str(round(i[1]/i[0],4)*100)+"%")
    except Exception as e: 
        print("    🔴  failed, retrying")
        proof = Proof(OPB_LOCATION+file)
        print("    1️⃣  rup file created")
        i = make_smol(file,OPB_LOCATION, "20230301-sip-proof-logs/")
        print("    2️⃣  smol file created")
        print("    3️⃣  kept:", str(round(i[1]/i[0],4)*100)+"%")
    file = "stack_"+file
    print(file)
    if not os.path.exists("rup/"+file+".rup"):
        proof = StackProof(OPB_LOCATION+file[6:])
        print("    1️⃣  rup file created")
    else:
        print("    1️⃣  rup file already exists")
    try:
        i = make_smol(file,OPB_LOCATION, "20230301-sip-proof-logs/")
        print("    2️⃣  smol file created")
        print("    3️⃣  kept:", str(round(i[1]/i[0],4)*100)+"%")
    except Exception as e: 
        print("    🔴  failed, retrying")
        proof = Proof(OPB_LOCATION+file)
        print("    1️⃣  rup file created")
        i = make_smol(file,OPB_LOCATION, "20230301-sip-proof-logs/")
        print("    2️⃣  smol file created")
        print("    3️⃣  kept:", str(round(i[1]/i[0],4)*100)+"%")
