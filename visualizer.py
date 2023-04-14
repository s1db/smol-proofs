import matplotlib.pyplot as plt

def create_graph(numbers, ml, filename='output.png', directory=''):
    max_number = max(numbers)
    x = list(range(1, max_number + 1))
    y = []
    colors = []

    for i in x:
        if i in numbers:
            if i < ml:
                y.append(1)
                colors.append('#ff0000')
            else:
                y.append(1)
                colors.append('#0066ff')
        else:
            y.append(1)
            colors.append('#f7f5f5')

    fig = plt.figure()
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.bar(x, y, color=colors, width=1)
    ax.set_xlim(0, max_number + 1)
    ax.set_ylim(0, 0.1)
    ax.set_axis_off()
    fig.add_axes(ax)
    fig.set_size_inches(2, 0.4)
    print(directory+filename)
    fig.savefig(directory+filename)
    fig.show()
    plt.close()

def core(file_name):
    graph_dict = {}
    with open("rup/"+file_name+".rup", "r") as f:
        for line in f.readlines():
            proof_step_id, antecedent = line.split(":")
            proof_step_id = int(proof_step_id)
            antecedent = [int(x) for x in antecedent.split()]
            graph_dict[proof_step_id] = antecedent
    small_graph = {}

    queue = [max(graph_dict.keys())]
    model_lines = min(graph_dict.keys())-1
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
    return (model_lines, sorted(list(steps_to_keep)))


if __name__ == "__main__":
    # files = ["random_table_4vars_222", "random_table_5vars_84", "random_table_5vars_114", "random_table_4vars_204", "random_table_4vars_40", "random_table_4vars_93", "random_table_4vars_8", "random_table_4vars_55", "random_table_3vars_137", "random_table_4vars_158"]
    # DIR = "images2_smart_table_proofs/"
    # files = ["g5-g6", "g3-g6", "g2-g5", "g10-g25", "g17-g25", "g2-g3", "g24-g28", "g7-g23", "g11-g28", "g10-g14",]
    # DIR = "images2_sip_proofs/"
    files = ["magic_series_2", "magic_series_4", "magic_series_6", "magic_series_8", "magic_series_10", "magic_series_12", "magic_series_14", "magic_series_16", "magic_series_18", "magic_series_20"]
    DIR = "images2_magic_series_proofs/"
    for file in files:
        print(file)
        ml, c = core(file)
        _, c2 = core("stack_"+file)
        print(len(c), len(c2))
        create_graph(c, ml, file+".png", DIR)
        create_graph(c2, ml, "stack_"+file+".png", DIR)