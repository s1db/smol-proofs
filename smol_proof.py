import pprint as pp

def make_smol(file_name, read_dir, save_dir):
    graph_dict = {}
    with open("rup/"+file_name+".rup", "r") as f:
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
    PROOF_FILE = f"{read_dir}{file_name}.veripb"
    with open(PROOF_FILE, "r") as f:
        with open(f"{save_dir}/smol_{file_name}.veripb", "w") as g:
            model_step = 0
            proof_step = 0
            short_proof_step = 0
            new_numbering = {}
            for line in f.readlines():
                if "pseudo" in line:
                    g.write(line[:-1])
                elif line[0] == "f":
                    model_step = int(line.split()[1])
                    short_proof_step = model_step
                    proof_step = model_step
                    g.write("\n"+line[:-1])
                elif line[0] == "u":
                    proof_step += 1
                    if proof_step in steps_to_keep:
                        short_proof_step += 1
                        new_numbering[proof_step] = short_proof_step
                        g.write("\n"+line[:-1])
                elif line[0] == "j":
                    proof_step += 1
                    if proof_step in steps_to_keep:
                        reformulated_line = line.split(" ")
                        reformulated_line[1] = str(new_numbering[int(reformulated_line[1])])
                        line = " ".join(reformulated_line)
                        short_proof_step += 1
                        new_numbering[proof_step] = short_proof_step
                        g.write("\n"+line[:-1])
                elif line[0] == "p":
                    proof_step += 1
                    if proof_step in steps_to_keep:
                        reformulated_line = line.split(" ")
                        for i in range(0, len(reformulated_line)):
                            entry = reformulated_line[i]
                            if entry.isdigit():
                                if int(entry) > model_step:
                                    reformulated_line[i] = str(new_numbering[int(entry)])
                        short_proof_step += 1
                        new_numbering[proof_step] = short_proof_step
                        line = " ".join(reformulated_line)
                        g.write("\n"+line[:-1])
                elif line[0] == "c":
                    reformulated_line = line.split(" ")
                    reformulated_line[1] = str(new_numbering[int(reformulated_line[1])])
                    line = " ".join(reformulated_line)
                    g.write("\n"+line)
                elif line[0] == "v":
                    g.write("\n"+line[:-1])
            g.write("\n* no of proof steps: "+ str(proof_step-model_step))
            g.write("\n* no of short proof steps: "+str(short_proof_step-model_step))
            g.write("\n* % of proof steps kept: "+ str((short_proof_step-model_step)/(proof_step-model_step)))
            return (proof_step-model_step, short_proof_step-model_step)