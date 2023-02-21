import pprint as pp

# read proof.rup lines and store in a dict

FILE_NAME = "proof"+".rup"
graph_dict = {}
with open(FILE_NAME, "r") as f:
    for line in f.readlines():
        proof_step_id, antecedent = line.split(":")
        proof_step_id = int(proof_step_id)
        antecedent = [int(x) for x in antecedent.split()]
        graph_dict[proof_step_id] = antecedent


small_graph = {}

queue = [max(graph_dict.keys())]
steps_to_keep = set()
while queue:
    node = queue.pop()
    steps_to_keep.add(node)
    if node not in small_graph:
        if node in graph_dict:
            small_graph[node] = graph_dict[node]
            queue.extend(graph_dict[node])
        else:
            small_graph[node] = []
PROOF_FILE = "proofs/"+FILE_NAME[:-4]+".pbp"
with open(PROOF_FILE, "r") as f:
    model_step = 0
    proof_step = 0
    short_proof_step = 0
    new_numbering = {}
    for line in f.readlines():
        if line[0] == "pseudo":
            print(line[:-1])
        elif line[0] == "f":
            model_step = int(line.split()[1])
            short_proof_step = model_step
            proof_step = model_step
            print(line[:-1])
        elif line[0] == "u":
            proof_step += 1
            if proof_step in steps_to_keep:
                short_proof_step += 1
                new_numbering[proof_step] = short_proof_step
                print(line[:-1])
        elif line[0] == "j":
            proof_step += 1
            if proof_step in steps_to_keep:
                reformulated_line = line.split(" ")
                reformulated_line[1] = str(new_numbering[int(reformulated_line[1])])
                line = " ".join(reformulated_line)
                short_proof_step += 1
                new_numbering[proof_step] = short_proof_step
                print(line[:-1])
        elif line[0] == "p":
            proof_step += 1
            if proof_step in steps_to_keep:
                reformulated_line = line.split(" ")
                for i in range(0, len(reformulated_line)):
                    entry = reformulated_line[i]
                    if entry.isdigit():
                        if int(entry) > model_step:
                            reformulated_line[i] = str(new_numbering[int(entry)])
                            # print(entry, "to", reformulated_line[i])
                short_proof_step += 1
                new_numbering[proof_step] = short_proof_step
                line = " ".join(reformulated_line)
                print(line[:-1])
        elif line[0] == "c":
            reformulated_line = line.split(" ")
            reformulated_line[1] = str(new_numbering[int(reformulated_line[1])])
            line = " ".join(reformulated_line)
            print(line)
    print("* no of proof steps:", proof_step)
    print("* no of short proof steps:", short_proof_step)
    print("* % of proof steps kept:", short_proof_step/proof_step)