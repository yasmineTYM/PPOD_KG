import requests
import yaml 

def loadYAML(url, github):
    if github:
        r = requests.get(url)
        data_linkml = yaml.safe_load(r.content)
    else:
        with open(url, "r") as stream:
            data_linkml = yaml.safe_load(stream)
    return data_linkml 

def addRelation(relation_info):
    if "range" in relation_info:
        if isinstance(relation_info['range'], str):
            # only one range
            return [relation_info['range']]
        else:
            ## contain multiple range 
            return relation_info['range']
    else:
        return [] 
"""
Input: networkx G (ontology), taxonomy 
Output: Graph format for visualizing in Neo4jd3
"""
def G2Neo4jG(G, vocab):
    nodes = []
    nodes_id = []
    relationships = []
    count_rel = 0
    print(vocab.keys())
    filters = list(vocab['enums'].keys())
#     print(filters)
    for source, target, hdata in G.edges(data=True):
        if source not in nodes_id: ## do not have this node 
            if source in filters:
                color = "green"
                stroke_color = "black"
#                 info = vocab['enums'][source]
            else:
                color = "blue"
                stroke_color = "black"
#                 info = {}
            nodes.append({
                'id': source,
                'name': source,
                'color': color,
                'stroke_color': stroke_color, 
                'labels': [],
#                  'info': info,
                'properties': {},
                
            })
            nodes_id.append(source)
        if target not in nodes_id:
            if target in filters:
                color = "green"
                stroke_color = "black"
#                 info = vocab['enums'][target]
            else:
                color = "blue"
                stroke_color = "black"
#                 info = {}
            nodes.append({
                'id': target, 
                'name': target,
                'color': color,
                'stroke_color': stroke_color, 
                'labels': [],
#                 'info': info,
                'properties': {}
            })
            nodes_id.append(target)
        
        vals = hdata['relation']
        
        relationships.append({
            'id': str(count_rel),
            'label': str(vals),
            'startNode': source, 
            'endNode': target,
            'properties': dict(zip(vals, vals))
        })
        count_rel+=1
    output = {
        "results": [{
            "columns":[],
            "data":[{
                "graph":{
                    "nodes": nodes,
                    "relationships":relationships
                }
            }]
        }],
        "errors":[]
    }
    return output
"""
Input: Read-in Yaml file 
Output: Networkx build directed graph (Ontology)
"""
def constructOntogy(linkml):
    G = nx.DiGraph()
    nodes = []
    nodes_id = []
    relationships = []
    entity_names = linkml['classes'].keys()
    
    
    for entity in entity_names:
        entity_info = linkml['classes'][entity]
        entity_slots = entity_info['slots']
        for relation_name in entity_slots :
            relation_info = linkml['slots'][relation_name]
            target_ = addRelation(relation_info)
            if len(target_) == 0:
                continue
                ## no target entity, target is a string 
            else:
                for target in target_:
                    if G.has_edge(entity, target):
                        G[entity][target]['relation'].append(relation_name)
                    else:
                        G.add_edge(entity, target, relation = [relation_name])
    
    return G
"""
Input: 
linkml: url for LinkML, either github url or local path 
vocab: url for Taxonomy, either github url or local path 

Output:
G: A graph format (in Neo4j format) to be visualized in our viewer. 
"""
def Parser(linkml, vocab, github):
    ## Loading YAML file 
    linkml = loadYAML(linkml, github)
    vocab = loadYAML(vocab, github)
    
    ## Construct ontology from linkml 
    G1 = constructOntogy(linkml)
    ## Combine filtering information from Taxonomy YAML file 
    G2 = G2Neo4jG(G1, vocab)
    
    return G1, G2


import networkx as nx

linkml = "https://raw.githubusercontent.com/yasmineTYM/PPOD_KG/main/PPOD_new.yaml"
vocab= 'https://raw.githubusercontent.com/yasmineTYM/PPOD_KG/main/vocabs_new.yaml'
G1, G2 =  Parser(linkml, vocab, True)


# import matplotlib.pyplot as plt
# fig, ax = plt.subplots(figsize=(15,8))
# nx.draw(G1, with_labels=True)