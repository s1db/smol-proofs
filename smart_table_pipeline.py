import os
from proof import Proof
from smol_proof import make_smol
import subprocess
# get the names of all files in the smart_table_proofs directory
files = os.listdir("smart_table_proofs/")
failing_files = []
# failing_files = ["random_table_3vars_301.opb", "random_table_4vars_93.opb", "random_table_3vars_244.opb", "random_table_3vars_199.opb", "random_table_4vars_55.opb"]
files = [f for f in files if f.endswith(".opb") and not f.startswith("smol_")]
files = [f for f in files if f not in failing_files]

t= {}
for file in files:
    file = file[:-4]
    # print(file)
    # proof = Proof("smart_table_proofs/"+file)
    i = make_smol(file)
    t[file] = i
    # print(file, "kept:", str(round(i[1]/i[0],4)*100)+"%")
    
for i in t:
    # print(i)
    print(i, "kept:", str(round((t[i][1]/t[i][0])*100,3))+"%")

for i in files:
    i = i[:-4]
    output = subprocess.check_output(f"veripb smart_table_proofs/{i}.opb smart_table_proofs/smol_{i}.veripb", shell=True)
    print(output)