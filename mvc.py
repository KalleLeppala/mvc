###### THE FUNCTION FOR DECIDING WHICH SAMPLES TO REMOVE DUE TO RELATEDNESS ###############################################################

# samples_to_remove
#
# The function called by the user.
# Takes a PLINK *.genome file that is already filtered so that it only contains sample pairs that are considered too related.
# Returns a smallest possible set of samples that need to be removed in order to erase all the given relationships.## genome                 A PLINK *.genome file, including the header, filtered so that only pairs that are considered too related#                        (for example with PI_HAT > 0.2) remain.# output                 Name for the output text file, defaults to "samples_to_remove, txt".# cases_over_controls    Decides whether the given relationships should be considered as one big graph (False),#                        or whether we should always try to keep as many cases as possible, and only then worry about keeping as many#                        controls as possible (True).#                        In that instance we do the removal in three phases: first considering the subgraph consisting of
#                        case-case -relationships only and removing the minimal amount (this is the only reason to ever remove a case),
#                        then removing the control from all the remaining case-control -relationships, and finally removing the minimal
#                        amount of controls from the subgraph consisting of all the remaining control - control -relationships.
#                        The default setting is cases_over_controls = True.
# family                 A PLINK *.fam file that contains the information (in the sixth Column) on which samples (the first and second
#                        column) are cases (value 2) and which are controls (value 1).
#                        Only needed if cases_over_controls = True, defaults to "".
def samples_to_remove(genome, output = "samples_to_remove.txt", cases_over_controls = True, family = ""):
    if cases_over_controls == False:

        g = open(output, "w")
        print("Creating a graph from the genome file...")
        graph = create_graph(genome, False)

        print("Done.")

        print("Breaking the graph into connected components...")
        components = break_graph(graph)

        if len(components) == 1:

            print("Done. There is only one connected component.")

        else:

            print("Done. There are " + str(len(components)) + " connected components.")

        print("Computing a minimum vertex cover...")

        comp_count = 1
        for component in components:

            print("Component " + str(comp_count) + " out of " + str(len(components)) + ", with " + str(len(component.keys())) + " nodes.")
            comp_count += 1
            samples = mvc(component)
            for sample in samples:
                g.write(sample)
                g.write("\n")

        print("Done.")
        g.close()
    else:
        if family == "":
            print("You need to give the parameter family (a PLINK *.fam file) because I don't who is a case and who is a control.")
            return()
        else:
            h = open(family, "r")
            lines = [line.split() for line in h]
            case_information = {}
            for i in range(0, len(lines)):
                case_information.update({lines[i][0] + " " + lines[i][1]: lines[i][5]})
            h.close()
        g = open(output, "w")
        cases = []
        controls = []

        print("Creating graphs from the genome file...")
        (graph_cases, pairs, graph_controls) = create_graph(genome, True)

        print("Done.")

        print("Breaking the case-case -graph into connected components...")
        components = break_graph(graph_cases)
        if len(components) == 1:

            print("Done. There is only one connected component.")

        else:

            print("Done. There are " + str(len(components)) + " connected components.")
        print("Computing a minimum vertex cover...")

        comp_count = 1
        for component in components:

            print("Component " + str(comp_count) + " out of " + str(len(components)) + ", with " + str(len(component.keys())) + " nodes.")

            comp_count += 1
            cases = cases + mvc(component)

        print("Done.")

        print("Identifying the controls related to any remaning cases...")
        L = len(pairs) - 1
        for i in range(0, L + 1):
            if pairs[L - i][0] in cases:
                del pairs[L - i]
        for pair in pairs:
            if case_information[pair[0]] == "1":
                control = pair[0]
            if case_information[pair[1]] == "1":
                control = pair[1]
            if control not in controls:
                controls.append(control)
        graph_controls = remove_nodes(graph_controls, controls)

        print("Done.")

        print("Breaking the control-control -graph into connected components...")
        components = break_graph(graph_controls)

        if len(components) == 1:

            print("Done. There is only one connected component.")
        else:

            print("Done. There are " + str(len(components)) + " connected components.")

        print("Computing a minimum vertex cover...")

        comp_count = 1
        for component in components:

            print("Component " + str(comp_count) + " out of " + str(len(components)) + ", with " + str(len(component.keys())) + " nodes.")

            comp_count += 1
            controls = controls + mvc(component)

        print("Done.")
        for case in cases:
            g.write(case)
            g.write("\n")
        for control in controls:
            g.write(control)
            g.write("\n")
        g.close()

###### AUXILIARY FUNCTIONS FOR THE MAIN FUNCTION TO USE ###################################################################################

# create_graph
#
# The parameter genome is a (filtered) PLINK *.genome file of too related sample pairs.
# If cases_over_controls is True (default), returns a graph of too related case-case -instances, a graph of too related control-control
# -instances and and an array of too related case-control -instances.# If cases over controls is False, just returns one graph of too related sample pairs.
# Graphs are represented as dictionaries describing the edges of the graph (in the manner {vertex: [neighbours of vertex]},
# so each edge is mentioned twice).
def create_graph (genome, cases_over_controls = True):
    if cases_over_controls == False:
        f = open(genome, "r")
        all_edges = {}
        line = f.readline () # This is the header.
        line = f.readline()
        while line != "":
            split = line.split()
            sample_1 = split[0] + " " + split[1]
            sample_2 = split[2] + " " + split[3]
            if sample_1 in all_edges:
                all_edges[sample_1].append(sample_2)
            else:
                all_edges.update({sample_1: [sample_2]})
            if sample_2 in all_edges:
                all_edges[sample_2].append(sample_1)
            else:
                all_edges.update({sample_2: [sample_1]})
            line = f. readline()
        f.close()
        return(all_edges)
    else:
        f = open(genome, "r")
        all_edges_cases = {}
        all_edges_mix = []
        all_edges_controls = {}
        line = f.readline() # This is the header.
        line = f.readline()
        while line != "":
            split = line.split()
            sample_1 = split[0] + " " + split[1]
            sample_2 = split[2] + " " + split[3]
            phe = int(split[10])
            if phe == 1:
                if sample_1 in all_edges_cases:
                    all_edges_cases[sample_1].append(sample_2)
                else:
                    all_edges_cases.update({sample_1: [sample_2]})
                if sample_2 in all_edges_cases:
                    all_edges_cases[sample_2].append(sample_1)
                else:
                    all_edges_cases.update({sample_2: [sample_1]})
            if phe == 0:
                all_edges_mix.append([sample_1, sample_2])
            if phe == - 1:
                if sample_1 in all_edges_controls:
                    all_edges_controls[sample_1].append(sample_2)
                else:
                    all_edges_controls.update({sample_1: [sample_2]})
                if sample_2 in all_edges_controls:
                    all_edges_controls[sample_2].append(sample_1)
                else:
                    all_edges_controls.update({sample_2: [sample_1]})
            line = f.readline()
        f.close()
        return((all_edges_cases, all_edges_mix, all_edges_controls))

# break_graph
#
# Breaks a graph into an array of connected components (all the graphs are represented as dictionaries like before).
def break_graph(graph):
    graph_copy = dict(graph)
    components = []
    component = {}
    newcomers = []
    while len(graph_copy) > 0:
        if len(newcomers) == 0:
            newcomers.append(list(graph_copy.keys())[0])
        while len(newcomers) > 0:
            newcomer = newcomers[0]
            for friend in graph_copy[newcomer]:
                if friend not in component.keys() and friend not in newcomers:
                    newcomers.append(friend)
            component.update({newcomer: graph_copy[newcomer]})
            del graph_copy[newcomer]
            newcomers.remove(newcomer)
        components.append(component)
        component = {}
    return(components)

# mvc
#
# Takes a graph (represented as a dictionary like before) and finds a minimum vertex cover, returned as an array.
def mvc(graph):
    nodes = list(graph.keys())
    # Cliques in the complement graph are the independent vertex sets of the original graph.
    cliques = []
    for i in range (0, len(nodes)):
        cliques.append([i])
    while len(cliques) > 0:
        new_cliques = []
        maximum_clique = cliques[0]
        for clique in cliques:
            for i in range(clique[len(clique) - 1] + 1, len(nodes)):
                still_clique = True
                for j in range(0, len(clique)):
                    if nodes[clique[j]] in graph[nodes[i]]:
                        still_clique = False
                if still_clique == True:
                    new_clique = list(clique)
                    new_clique.append(i)
                    new_cliques.append(new_clique)
        cliques = new_cliques
    # The complements of independent vertex sets are the vertex covers.
    L = len(maximum_clique) - 1
    for i in range(0, L + 1):
        del(nodes[maximum_clique[L - i]])
    return(nodes)

# remove_nodes
#
# Given a graph (represented as a dictionary) and an array containing a list of nodes, removes the nodes from the graph.
def remove_nodes(graph, nodes):
    for node in nodes:
        if node in graph:
            del graph[node]
        for other_node in list(graph.keys()):
            if node in graph[other_node]:
                graph[other_node].remove(node)
                if len(graph[other_node]) == 0:
                    del graph[other_node]
    return(graph)
