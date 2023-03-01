import pydot

FILE_NAME = "proof2.rup"
graph = []
with open(FILE_NAME, "r") as f:
    for line in f.readlines():
        proof_step_id, antecedent = line.split(":")
        proof_step_id = int(proof_step_id)
        antecedent = [int(x) for x in antecedent.split()]
        graph.append((proof_step_id, antecedent))
    
# create graph with pydot
g = pydot.Dot(graph_type='digraph')
for proof_step_id, antecedent in graph:
    for antecedent_id in antecedent:
        g.add_edge(pydot.Edge(antecedent_id, proof_step_id))
g.write_png("proof2.png")