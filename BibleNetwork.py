
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

    def get_related_subgraph(self, factor=1, id=""):
        """Get subgraph of verses that are closely "related" to one another. Returns a subgraph G.
        
        factor -- A larger factor means a bigger subgraph."""

        # Ensure an id in the form {1} or {1,45,33231} is being passed
        id = self.get_id() if id == "" else id
        id = id if type(id) is set else {id}
        count = 0 

        nodes = self._get_cluster(factor, id)[0]

        while len(nodes) < 18 and count < 5: # if few nodes in subgraph, try again but be less sensitive
            print("increasing factor ... +0.1") 
            factor = factor + 0.1
            nodes = self._get_cluster(factor, id)[0]
            count += 1

        while len(nodes) > 40: # if few nodes in subgraph, try again but be less sensitive
            print("decreasing factor ... -0.1") 
            factor = factor - 0.1
            nodes = self._get_cluster(factor, id)[0]

        # if len(nodes) > 50: # if few nodes in subgraph, try again but be less sensitive
        #     print("decreasing factor ... -0.3") 
        #     factor = factor - 0.3
        #     nodes = self._get_cluster(factor, id)[0]

        # if len(nodes) < 10: # if few nodes in subgraph, try again but be less sensitive
        #     print("increasing factor ... +0.5") 
        #     factor = factor + 0.5
        #     nodes = self._get_cluster(factor, id)[0]

        # if len(nodes) < 20: # if few nodes in subgraph, try again but be less sensitive
        #     print("increasing factor ... +0.3") 
        #     factor = factor + 0.3
        #     nodes = self._get_cluster(factor, id)[0]

        # if len(nodes) < 12:
        #     print("increasing factor ...+0.2") 
        #     factor = factor + 0.2
        #     nodes = self._get_cluster(factor, id)[0]

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

if __name__ == "__main__":
    # interesting passages:
    # 22151 - Hosea 4:18
    # 27169 - Acts 7:53
    # 12354 - Nehemiah 3:27
    network = BibleNetwork()
    nodes = [0, 1, 2, 3, 4, 5, 6, 29480]
    for node in nodes:
        print (f"Crossrefs for {node}:\n{network.get_crossrefs(node)}")
    # print(network.get_topics(3))
    # print(network.get_topics(""))
    # print(network.get_related_topics())
    #print(network.get_crossrefs())
    #print(network.get_related_subgraph(factor=1))
    # print(network.get_crossrefs())