
import networkx as nx
import json
from random import choice

class BibleNetwork:
    """A network of the bible where verses are nodes."""
    def __init__(self):
        self.bible = nx.DiGraph()
        self.nodes_path = r"nodes.json"
        self.crossrefs_path = [r"edges.json", r"edges2.json"]

        self._init_verses()
        self._init_crossrefs()
        self.active = self.get_random_node() # set random verse as active node
        #self.active = self.get_node(0)
        self.active = self.get_node(27169)
        # self.active = self.get_node(22151)
        # self.active = self.get_node(8351)f
        # self.active = self.get_node(24230)
        self.active = self.get_node(2487)
        print(f"Your verse is:\n{self.active}")
        
    def get_active(self):
        return self.active
    
    def get_id(self):
        """Get id of active verse (e.g. 14500)"""
        return self.active["id"]
    
    def get_random_id(self):
        """Get id of an random verse"""
        return self.get_random_node()['id']
    
    def get_name(self, id=""):
        """Get name of given verse by id, or active verse if no id is supplied."""
        return self.active["name"] if id == "" else self.get_node(id)["name"]
        
    def get_fullname(self, id=""):
        """Get formatted name of given verse by id, or get active verse if no id is supplied."""
        if id == "":
            book, chap, verse = (self.active["book"], self.active["chap"], self.active["verse"])
        else:
            book, chap, verse = (self.get_node(id)["book"], self.get_node(id)["chap"], self.get_node(id)["verse"])

        return f"{book} {chap}:{verse}"
    
    def sanitise(self, text):
        return ''.join(char for char in text if char.isalnum())
    
    def get_topics(self, id=""):
        """Get verse of given verse by id (e.g. 340). Get active verse if no id is supplied."""
        topics = self.active["topics"] if id == "" else self.get_node(id)["topics"]
        new = {self.sanitise(topic): weight

            for topic, weight in (topics)
        }
        # print(f"topics!!! {new}")
        return new
        # return sorted(topics, key=lambda x: x[1], reverse=True)
        
    def get_verse(self, id=""):
        """Get verse of given verse by id (e.g. 340). Get active verse if no id is supplied."""
        return self.active["content"] if id == "" else self.get_node(id)["content"]
    
    def get_node(self, id):
        return self.bible.nodes(data=True)[id]
    
    def get_crossrefs(self, id=""):
        """Sorted by weights"""
        return sorted(self._get_crossrefs(id=id).items(), key=lambda x: x[1]['weight'], reverse=True)
    
    def get_crossrefs_ids(self, id="", how_many=100, preprocess=False):
        """Get a list of crossref ids of a given id."""
        crossrefs = self.get_crossrefs(id=id)
        crossrefs = self._remove_low_quality_crossrefs(crossrefs[:how_many+5]) if preprocess else crossrefs
        crossrefs = crossrefs[:how_many]

        ids = {x for x, data in crossrefs}
        return ids
    
    def _remove_low_quality_crossrefs(self, crossrefs):
        """Remove cross-references that are low quality (i.e. they have not received many votes)"""
        # Check if crossrefs exist
        total = len(crossrefs)
        if total == 0:
            return crossrefs
        
        # Get diversity
        weights = [crossref[1]['weight'] for crossref in crossrefs]
        uniqueness = len(set(weights))
        diversity = uniqueness / total

        if diversity < 0.45:
            # Remove low-quality crossrefs
            # Example: [100, 92, 82, 71, 71, 71, 71, 71, 71] ---> [100, 92, 82]
            crossrefs = self._remove_crossrefs_by_weight(crossrefs, {weights[-1]})

        return crossrefs                

    def _remove_crossrefs_by_weight(self, crossrefs, weights={}):
        """Remove crossrefs with the given weight/s"""
        new_crossrefs = []
        weights.discard(100) # Do not remove "100" weights

        # Remove any verse with the given weight
        for crossref in crossrefs:
            if crossref[1]['weight'] not in weights:
                new_crossrefs.append(crossref)

        return new_crossrefs

    def count_topics(self, G, weighted=True, sort=True):
        """Get a count matrix for topics in a given subgraph."""
        counter = {}
        for verse, topics in list(G.nodes(data="topics")):
            for topic, weight in topics:
                # count the topics
                weight = weight / 100 + 1 if weighted else 1
                if topic in counter:
                    counter[topic] += 1 * weight
                else:
                    counter[topic] = 1 * weight
        
        # sort dictionary
        if sort: 
            return dict(sorted(counter.items(), key=lambda x: x[1], reverse=True))
        return counter

    def get_related_topics(self, id="", k=15):
        """Get a sorted dictionary of k related topics"""
        subgraph = self.get_related_subgraph(id=id)
        topics = self.count_topics(subgraph)
        return {x: topics[x] for x in list(topics)[:k]}
    
    def get_related_adj_subgraph(self, factor=1, id=""):
        id = self.get_id() if id == "" else id
        # ids = [(id - 1), (id), (id + 1)]4
        id = {0,1}

        return self.get_related_subgraph(factor, id)
    
    def get_shortest_path(self, source, target, graph=None):
        if graph is None:
            graph = self.bible

        return nx.single_source_dijkstra(graph, source=source, target=target, weight=self._weight_function)
    
    def get_serendipity(self, subgraph):
        total_nodes = len(subgraph)
        serendipity = 0

        for node in subgraph:
            for target in subgraph:
                lengths, paths = self.get_shortest_path(node, target)
                serendipity += lengths

        serendipity = serendipity / ( total_nodes * total_nodes)

        return serendipity  
    
    def get_related_subgraph_force_crossrefs(self, factor=1, id="", how_many=-1):
        crossrefs = self.get_crossrefs_ids(id=id, how_many=how_many, preprocess=True)
        crossrefs.add(id)
        return self.get_related_subgraph(id=crossrefs, factor=factor)
    
    def get_best_related_subgraph(self, id):
        return self._get_optimal_subgraph(id)
    
    def _get_optimal_subgraph(self, id):
        pairs = [(0.35, 5), (0.55, 4), (0.65, 2), (0.85, 0)]
        centrality = {}
        graphs = {}

        for f, k in pairs:
            ids = self.get_crossrefs_ids(id=id, how_many=k, preprocess=True)
            ids.add(id)
            G = self.get_related_subgraph(f, ids)
            centrality[(f, k)] = self.get_centrality_measures(G)
            graphs[(f, k)] = G

        top_graph = sorted(centrality.items(), key=lambda x: x[1]['degree'])[0][0]
        print(f"selecting... factor: {top_graph[0]} cutoff: {top_graph[1]}")     
        return graphs[top_graph]

    
    def get_related_subgraph(self, factor=1, id=""):
        """Get subgraph of verses that are closely "related" to one another. Returns a subgraph G.
        
        factor -- A larger factor means a bigger subgraph."""

        # Ensure an id in the form {1} or {1,45,33231} is being passed
        id = self.get_id() if id == "" else id
        id = id if type(id) is set else {id}
        count = 0

        nodes = self._get_cluster(factor, id)[0]

        while len(nodes) < 15 and count < 3: # if few nodes in subgraph, try again but be more sensitive
            # print("increasing factor ... +0.1") 
            factor = factor + 0.1
            nodes = self._get_cluster(factor, id)[0]
            count += 1

        while len(nodes) > 25: # if many nodes in subgraph, try again but be less sensitive
            # print("decreasing factor ... -0.05") 
            factor = factor - 0.05
            nodes = self._get_cluster(factor, id)[0]

        # create subgraph from cluster
        nodes, lengths, paths = self._get_cluster(factor, id)
        subgraph = self.bible.subgraph(nodes)
        pos = nx.spring_layout(subgraph)
        nx.set_node_attributes(subgraph, pos, 'position') # default position
        nx.set_node_attributes(subgraph, paths, 'path') # path between initial node and this node
        # nx.set_node_attributes(subgraph, lengths, 'path-length') # length of path between initial node and this node

        return subgraph

    def previous_verse(self):
        prev_verse = self.get_id() - 1
        self.active = self.get_node(prev_verse)
        #print(f"Your new verse is:\n{self.active}")

    def next_verse(self):
        next_verse = self.get_id() + 1
        self.active = self.get_node(next_verse)
        #print(f"Your new verse is:\n{self.active}")

    def set_verse(self, id):
        id = int(id)
        self.active = self.get_node(id)
    
    def get_random_node(self):
        return choice(self.bible.nodes(data=True))
    
    def _weight_function(self, u, v, d):
        """An inverse function. Highest weights are now the lowest and vice versa."""
        return 101 - d['weight']
    
    def _get_cluster(self, factor=1, id=""):
        """Gets clusters of verses that are "related" to one another. Verses that are weighted more will clustered.
        Returns list of nodes in cluster."""
        source = {self.get_id()} if id == "" else id
        cutoff = 15 * factor # a larger factor means a larger graph
        length, paths = nx.multi_source_dijkstra(self.bible, source, cutoff=cutoff, weight=self._weight_function)
        nodes = list(paths.keys()) # list of nodes in cluster
        
        return nodes, length, paths
    
    def _get_crossrefs(self, id=""):
        return self.bible[self.get_id()] if id == "" else self.bible[id]
       
    def _init_verses(self):
        """Add verses to graph."""
        verses = self._read_verses()
        self.bible.add_nodes_from(verses)
        return

    def _init_crossrefs(self):
        """Add cross-references to graph."""
        crossrefs = self._read_crossrefs()
        self.bible.add_edges_from(crossrefs)
        return

    def _read_verses(self):
        """Reads json and returns list of verses [ tuple1(id, dict<attrs>), tuple2(id, dict<attrs>), ... ]."""
        with open(self.nodes_path, 'r') as config_file:
            data_loaded = json.load(config_file)
        
        return data_loaded
    
    def _read_crossrefs(self):
        """Reads json and returns list of crossrefs [ tuple1(to, from, dict<attrs>), tuple2(to, from, dict<attrs>), ... ]."""

        data = []
        for path in self.crossrefs_path:
            with open(path, 'r') as config_file:
                data_loaded = json.load(config_file)
                data += data_loaded
                    
        return data
    
    def test_attributes(self, node):
        # Initalise variables
        factors = [x/100 for x in range(5, 201, 10)]
        cutoffs = [x for x in range(0,6)]
        string = ""

        # Cycle through every combination
        for factor in factors:
            prev_hash = -1
            prev_serendipity = -1
            for cutoff in cutoffs:

                subgraph = network.get_related_subgraph_force_crossrefs(id=node, factor=factor, how_many=cutoff)
                nodes = len(subgraph)
                if nodes > 26:
                    continue
                degree = round_avg(nx.degree_centrality(subgraph).values(), nodes)
                closeness = round_avg(nx.closeness_centrality(subgraph).values(), nodes)
                betweeness = round_avg(nx.betweenness_centrality(subgraph).values(), nodes)
                hash = factor * ( betweeness + closeness + degree + node ) * 100

                serendipity = prev_serendipity if hash == prev_hash else round(network.get_serendipity(subgraph), 4)
                per_node = round_avg([serendipity], nodes)
                prev_hash = hash
                prev_serendipity = serendipity

                values = f"factor: {factor} cutoff: {cutoff} per_node: {per_node} nodes: {nodes} serendipity: {serendipity} degree: {degree} closeness: {closeness} betweens: {betweeness}"
                print(values)
                string = string + values + "\n"
            print("")
            string = string + "\n"
            
        path = r'tests/serendipity-raw.csv'
        write(string, path)

    def get_random_ids(self, k):
        count = 0 
        ids = []
        while count < k:
            ids.append(self.get_random_id())
            ids = list(set(ids))
            count = len(ids)
        
        return ids
    
    def get_centrality_measures(self, G):
        nodes = len(G)
        degree = round_avg(nx.degree_centrality(G).values(), nodes)
        closeness = round_avg(nx.closeness_centrality(G).values(), nodes)
        betweens = round_avg(nx.betweenness_centrality(G).values(), nodes)

        return {'degree': degree, 'closeness': closeness, 'betweens': betweens}
    
    def k_test(self, k):
        nodes = self.get_random_ids(k)
        factors = [x/100 for x in range(5, 131, 10)]
        cutoffs = [x for x in range(0,6)]
        centrality_measures = ['degree', 'closeness', 'betweens', 'avg_nodes']
        data = {}

        for f in factors:
            for c in cutoffs:
                sums = {x: 0 for x in centrality_measures}
                k = 0
                for n in nodes:
                    # Generate graph
                    subgraph = network.get_related_subgraph_force_crossrefs(id=n, factor=f, how_many=c)
                    total = len(subgraph)
                    if total > 26:
                        continue

                    # Get centrality
                    centrality = self.get_centrality_measures(subgraph)
                    centrality['avg_nodes'] = total

                    # Sum centrality
                    for x in centrality_measures:
                        sums[x] = sums[x] + centrality[x]

                    k = k + 1
                
                if k == 0:
                    continue
                # Average centrality
                key = (f,c)
                data[key] = { x: round_avg([sums[x]], k) for x in centrality_measures}
                data[key]['total_graphs'] = k
                print(f"factor: {f} cutoff: {c} k: {k} avg_nodes: {data[key]['avg_nodes']} degree: {data[key]['degree']} closeness: {data[key]['closeness']} betweens: {data[key]['betweens']}")

        print(data)
        return sorted(data.items(), key=lambda x: x[1]['degree'])

def write(data, path):
    """Write data_structure to given path"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

    print(f"Successfully written to {path}")    

def round_avg(x, nodes):
    return round(sum(x) / nodes, 4)

def write_json(data, path):
    """Write data_structure to given path"""
    with open(path, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))

    print(f"Successfully written verses to {path}")

if __name__ == "__main__":
    dump_path = f"dump.json"
    # interesting passages:
    # 22151 - Hosea 4:18
    # 27169 - Acts 7:53
    # 12354 - Nehemiah 3:27
    network = BibleNetwork()
    # nodes = [0, 1, 2, 3, 4, 5, 6, 29480]
    # nodes = [23949, 0, 1, 22151, 27169, 12354]
    # nodes = [x for x in range(0, 31100, 1780)]
    # nodes = [28375, 5842, 27169]

    # low 
    node = 24332
    print(network.get_crossrefs(1250))
    print(network.get_crossrefs_ids(1250, 5, True))
    print(network.get_name(node))
    print(network.optimise_cluster(22151))
    # results = network.k_test(1500)
    # write_json(results, dump_path)
    # network.test_attributes(node)