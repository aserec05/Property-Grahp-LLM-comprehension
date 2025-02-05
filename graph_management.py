import networkx as nx

def create_graph_for_wc(data):
    """Create a networkx object from json"""
    graph_nx = nx.Graph()
    for item in data:
        node_n = item['n']
        graph_nx.add_node(node_n['identity'], labels=node_n['labels'], **node_n['properties'])

        node_m = item['m']
        graph_nx.add_node(node_m['identity'], labels=node_m['labels'], **node_m['properties'])

        edge_r = item['r']
        graph_nx.add_edge(edge_r['start'], edge_r['end'], id=edge_r['identity'], label=edge_r['type'], **edge_r['properties'])
    return graph_nx


def create_graph_for_sub_wc(data):
    """Create a networkx object from json"""
    graph_nx = nx.Graph()

    for entry in data:
        main_node = entry['p']
        graph_nx.add_node(
            main_node['identity'],
            labels=main_node['labels'],
            **main_node['properties']
        )

        for related_node in entry['relatedNodes']:
            graph_nx.add_node(
                related_node['identity'],
                labels=related_node['labels'],
                **related_node['properties']
            )

        for relationship in entry['relationships']:
            graph_nx.add_edge(
                relationship['start'],
                relationship['end'],
                id=relationship['identity'],
                label=relationship['type'],
                **relationship['properties']
            )
    return graph_nx


def create_graph_for_synthea(folder):
    """Create a graph from Synthea CSV files based on provided schemas."""
    graph_nx = nx.Graph()

    # Paths to key Synthea files
    patient_file = os.path.join(folder, 'patients.csv')
    encounter_file = os.path.join(folder, 'encounters.csv')
    condition_file = os.path.join(folder, 'conditions.csv')
    medication_file = os.path.join(folder, 'medications.csv')

    # Read patients
    patient_ids = {}
    if os.path.exists(patient_file):
        with open(patient_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient_id = row['Id']
                patient_name = f"Patient_{patient_id}"
                graph_nx.add_node(patient_name, type='patient', data=row)
                patient_ids[patient_id] = patient_name

    # Read encounters
    if os.path.exists(encounter_file):
        with open(encounter_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                encounter_id = row['Id']
                patient_id = row['PATIENT']
                if patient_id in patient_ids:
                    encounter_name = f"Encounter_{encounter_id}"
                    graph_nx.add_node(encounter_name, type='encounter', data=row)
                    graph_nx.add_edge(patient_ids[patient_id], encounter_name)

    # Read conditions
    if os.path.exists(condition_file):
        with open(condition_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient_id = row['PATIENT']
                condition_code = row.get('CODE', 'UNKNOWN')  # Use condition code (e.g., SNOMED/ICD10)
                condition_name = f"Condition_{condition_code}"
                if patient_id in patient_ids:
                    if not graph_nx.has_node(condition_name):
                        graph_nx.add_node(condition_name, type='condition', data=row)
                    graph_nx.add_edge(patient_ids[patient_id], condition_name)

    # Read medications
    if os.path.exists(medication_file):
        with open(medication_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient_id = row['PATIENT']
                medication_code = row.get('CODE', 'UNKNOWN')  # Use medication code (e.g., RxNorm)
                medication_desc = row.get('DESCRIPTION', 'UnknownMedication')
                medication_name = f"Medication_{medication_code}_{medication_desc.replace(' ', '_')}"
                if patient_id in patient_ids:
                    if not graph_nx.has_node(medication_name):
                        graph_nx.add_node(medication_name, type='medication', data=row)
                    graph_nx.add_edge(patient_ids[patient_id], medication_name)

    return graph_nx


def create_node_string(graph):
    """Make nodes for incident encoding"""
    node_descriptions = []
    for node, props in graph.nodes(data=True):
        labels = props.pop('labels', [])
        labels_str = ', '.join(labels)
        prop_desc = ', '.join([f"{key}: {value}" for key, value in props.items()])
        node_descriptions.append(f"{node} [{labels_str}] ({prop_desc})")
    return ', '.join(node_descriptions)


def encode_graph(graph):
    """Encode the graph in the incident format"""
    nodes_string = create_node_string(graph)
    output = "G describes a graph among nodes: \n%s.\n" % nodes_string
    if graph.edges():
        output += "In this graph:\n"
    for source_node in graph.nodes():
        target_nodes = list(graph.neighbors(source_node))
        target_nodes_str = ""
        nedges = 0
        for target_node in target_nodes:
            edge_props = graph.get_edge_data(source_node, target_node)
            edge_props_str = ', '.join([f"{key}: {value}" for key, value in edge_props.items()])
            target_nodes_str += f"{target_node} ({edge_props_str}), "
            nedges += 1
        if nedges > 1:
            output += "Node %s is connected to nodes %s.\n" % (
                source_node,
                target_nodes_str[:-2],
            )
        elif nedges == 1:
            output += "Node %s is connected to node %s.\n" % (
                source_node,
                target_nodes_str[:-2],
            )
    return output