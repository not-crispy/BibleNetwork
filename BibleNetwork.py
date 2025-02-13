
import networkx as nx
import json
from random import choice
from cooccurence import Co_Occurence
from statistics import mode
from strongs import StrongsDict

URL = "" # if native

URL = "https://biblenetwork.s3.us-east-2.amazonaws.com/" # if online

class BibleNetwork:
    """A network of the bible where verses are nodes."""
    def __init__(self):
        print("Building BibleNetwork...")
        self.bible = nx.DiGraph()

        self.strongs_enabled = False

        if self.strongs_enabled:
            print("Retrieving Strongs Dictionary...")
            self.strongs_dict = StrongsDict()
        else:
            print("Did not build Strongs Dictionary...")

        self.nodes_path = [r"nodes1.json", r"nodes2.json", r"nodes3.json", r"nodes4.json"]
        # self.nodes_path = r"nodes1.json"
        self.crossrefs_path = [r"edges.json", r"edges2.json"]

        print("Loading Bible...")
        self._init_verses()
        print("Building cross references...")
        self._init_crossrefs()
        self._first_id = 0
        self._last_id = len(self.bible.nodes()) - 1
        self.active = self.get_random_node() # set random verse as active node
                
    def get_active(self):
        return self.active
    
    def get_id(self):
        """Get id of active verse (e.g. 14500)"""
        return self.active["id"]
    
    def get_id_by_name(self, verse):
        """Lookup the id of a verse based on a given reference e.g. Matt.3.3"""
        # Initialise verse lookup 
        path = "verse_lookup.json"
        with open(path, 'r') as config_file:
            lookup = json.load(config_file)

        # Conduct lookup and return ID
        return lookup[verse] if verse in lookup else ""
    
    def get_random_id(self):
        """Get id of an random verse"""
        return self.get_random_node()['id']
    
    def get_edges(self, path):
        """Get a list of edges for a given path"""
        edges = []
        count = 1
        while count < len(path):
            x = path[count - 1]
            y = path[count]
            edges.append(self.bible.edges[x,y])
            count += 1 

        return edges

    def get_path_passages(self, path):
        """Get the passages of the given path."""
        edges = self.get_edges(path)
        edges.insert(0, {'end': ''}) # initialise with starting verse
        passages = []
        
        for i, edge in enumerate(edges):
            # Get start and end ids
            start = path[i]
            end = start if edge['end'] == '' else self.get_id_by_name(edge['end']) 

            # Get passage           
            passage = self.get_passage(start, end)
            data = {'passage': passage['passage'], 'name': passage['name'], 'start': start, 'end': end}
            passages.append(data)

        return passages
    
    def get_passage_name(self, start, end):
        """Construct the name of the passage given a start and end id."""
        if start == end : # If not a passage
            return self.get_fullname(start)
        
        # If a passage, get data
        taxonomies = ['book', 'chap', 'verse']
        name = f"{self.get_fullname(start)}-"
        start = self.get_node(start)
        end = self.get_node(end)
        diff = False

        # Build the name
        for taxonomy in taxonomies:
            if start[taxonomy] != end[taxonomy]:
                diff = True               
            if diff:
                name += end[taxonomy]
                name += " " if taxonomy == "book" else ""
                name += ":" if taxonomy == "chap" else "" 

        return name

    def get_passage(self, x, y, active=''):
        """Get a passage from the id x to the id y."""
        # Initialise
        active = active if active != '' else x
        start, end = (y, x) if x > y else (x, y) # ensure start id is always smaller
        verses = []
        ids = []
        verses_as_string = ""
        name = self.get_passage_name(start, end)

        # Iterate through start to end
        while start <= end :
            verse = self.get_verse(start)
            verses.append(verse)
            ids.append(start)
            verses_as_string += f" {verse}"
            start += 1

        return {"name": name, "passage": verses_as_string.strip(" "), "verses": verses, "ids": ids, "active": active}

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
    
    def get_dictname(self, id=""):
        id = self.get_id() if id == "" else id
        return {
                "bk": self.get_node(id)["book"].replace(" ", "-"),
                "ch": self.get_node(id)["chap"],
                "vs": self.get_node(id)["verse"]
                }
    
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
    
    def get_context(self, id=""):
        """Get verse, and the verse before and after this verse."""
        id = self.get_id() if id == "" else id
        start = id if id == self._first_id else id - 1
        end = id if id == self._last_id else id + 1

        return self.get_passage(start, end, active=id)
    
    def get_strongs(self, id="", no_stopwords=False):
        """Return verse in original language, including Strongs numbers, Greek/Hebrew, transliteration and English translation."""
        id = self.get_id() if id == "" else id
        verse = []
        verse_eng = []
        verse_trans = []
        strongs = []
        for word in self.get_node(id)['strongs']:
            if no_stopwords and word['stop_word']:
                continue # do not include stop words
            else:
                x = word['lemma']
                verse.append(x)
                verse_eng.append(word['eng'])
                verse_trans.append(word['translit'])
                strongs.append(word['sn'])

        return {"strongs": strongs, "lemma": verse, "translit": verse_trans, "english": verse_eng}

    def get_node(self, id):
        """Returns the node data of a given id"""
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

        # Remove any verse with the given weight
        for crossref in crossrefs:
            significant = crossref[1]['weight'] > 86 # Do not remove "100" weights
            if significant:
                new_crossrefs.append(crossref)
            elif crossref[1]['weight'] not in weights:
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
        """Get the topics (k = max) of verses related to the given verse. Returns a sorted dictionary of topics."""
        subgraph = self.get_best_subgraph(id=id) #
        topics = self.count_topics(subgraph)
        return {x: topics[x] for x in list(topics)[:k]}
    
    def get_related_adj_subgraph(self, factor=1, id=""):
        id = self.get_id() if id == "" else id
        # ids = [(id - 1), (id), (id + 1)]4
        id = {0,1}

        return self.get_related_subgraph(factor, id)
    
    def get_shortest_path(self, source, target, graph=None):
        """Returns the shortest path between source and target of a given subgraph (default: all the bible)
        
        Return: The form of [distance, [source_id, ..., target_id]]"""
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
    
    def get_best_subgraph(self, id):
        return self._optimise_subgraph(id)
    
    def get_related_subgraph_force_crossrefs(self, factor=1, id="", how_many=-1):
        """Get subgraph containing the given crossreferences"""
        crossrefs = self.get_crossrefs_ids(id=id, how_many=how_many, preprocess=True)
        crossrefs.add(id)
        return self.get_related_subgraph(id=crossrefs, active=id, factor=factor)
    
    def get_path_related_subgraph(self, id1="", id2=""):
        ids = self.get_shortest_path(source=id1, target=id2)[1]
        return self.get_related_subgraph(id=ids, active=id1, shortest_path=ids)
    
    def get_related_subgraph(self, id="", active="", factor=0.4, shortest_path=None):
        """Get subgraph of verses that are closely "related" to one another. Returns a subgraph G.
        s
        factor -- A larger factor means a bigger subgraph."""

        # Initialise
        id = self.get_id() if id == "" else id
        active = id if active == "" else active

        # Parse data
        id = {id} if type(id) is int else set(id)
        # active = {active} if type(active) is int else set(active)
        nodes = self._get_cluster(factor, id)[0]
        count = 0
        count_k = 0

        # Be more sensitive
        while len(nodes) < 3 and count_k < 5:
            factor = factor + 0.3
            nodes = self._get_cluster(factor, id)[0]
            count_k += 1

        while len(nodes) < 15 and count < 5:
            factor = factor + 0.1
            nodes = self._get_cluster(factor, id)[0]
            count += 1

        # Be less sensitive
        while len(nodes) > 25:
            factor = factor - 0.05
            nodes = self._get_cluster(factor, id)[0]

        # Get subgraph
        cluster = self._get_cluster(factor, id)
        return self._convert_cluster_to_subgraph(cluster, active, shortest_path=shortest_path)
    
    def _convert_cluster_to_subgraph(self, cluster, active, get_attribs=True, shortest_path=None):
        """Convert cluster into subgraph. If attribs = True, add extra attributes to each node."""
        nodes, lengths, paths = cluster
        subgraph = self.bible.subgraph(nodes)

        # print(f"nodes: {nodes}\n lengths: {lengths} \n paths: {paths}")

        for key, path in paths.items():
            if shortest_path:
                # Find a path between current node and active node (either n1 or n2)
                node = path[0]
                k = shortest_path.index(node)

                # Is n1 or n2 shorter? 
                n1, n2 = shortest_path[:k], shortest_path[k+1:]
                path = n1 + path

                #### ABOVE CODE DRAWS PATH FROM NODE: n1

                #### THE BELOW CODE ATTEMPTS TO DRAW THE SHORTEST PATH
                #### BUT DOES NOT WORK FOR ALL NODES -- i.e. sometimes an edge used in short_path is not yet added to the graph
                #### POSSIBLE SOLUTION: ENFORCE EDGES IN BOTH DIRECTIONS
                # if len(n1) < len(n2):
                #     print("left")
                #     if len(path) != 1:
                #         print("BANG!")
                #     path = n1 + path # if len(path) == 1 else n1 + path[::-1]
                # else: 
                #     print("right")
                #     if len(path) != 1:
                #         print("BANG!")
                #     path = path[::-1] + n2 if len(path) == 1 else n1 + path # n2[::-1] + path
                # path = n1 + path if len(n1) < len(n2) else path[::-1] + n2 # This is the shorter path

            elif path[0] is not active:
                path.insert(0, active)
            paths[key] = path 

        # print(f"Paths {paths}")

        if get_attribs:
            pos = nx.spring_layout(subgraph)
            nx.set_node_attributes(subgraph, pos, 'position') # default position
            nx.set_node_attributes(subgraph, paths, 'path') # path between initial node and this node
            nx.set_node_attributes(subgraph, lengths, 'length') # length of path between initial node and this node

        return subgraph
    
    def _optimise_subgraph(self, id):
        """Select the subgraph with the most optimal serendipity (approximated using centrality measures)."""
        pairs = [(0.35, 5), (0.55, 4), (0.65, 2), (0.85, 0)] # (0.35, 7) is good for densely connected verses, but not good for sparse verses
        centrality = {}
        graphs = {}
        max_nodes = 0

        # Try a few subgraphs
        for f, k in pairs:
            G = self.get_related_subgraph_force_crossrefs(factor=f, id=id, how_many=k)
            centrality[(f, k)] = self.get_centrality_measures(G)
            graphs[(f, k)] = G
            max_nodes = len(G) if len(G) > max_nodes else max_nodes
            # print(f"centrality: {centrality[(f, k)]} length: {len(G)}")
            
        # Remove any very small subgraphs if a larger one exists
        for pair, G in graphs.items():
            if max_nodes > 3 and len(G) < 3:
                centrality.pop(pair) 

        # A lower degree approximates a lower serendipity (i.e. more optimal)
        # print(f"centrality of {id}:\n{centrality}")
        top1 = sorted(centrality.items(), key=lambda x: x[1]['betweens'])[0][0]
        top2 = sorted(centrality.items(), key=lambda x: x[1]['degree'])[0][0]
        top3 = sorted(centrality.items(), key=lambda x: x[1]['closeness'])[0][0]
        top_graph = mode([top1, top2, top3])
        # print(f"top_graphs: {[top1, top2, top3]} mode: {top_graph}")

        print(f"selecting... factor: {top_graph[0]} cutoff: {top_graph[1]} options: {top1, top2, top3}")     
        return graphs[top_graph]

    def previous_verse(self, id=""):
        id = self.get_id() if id == "" else id
        id = id - 1

        # Check verse still exists (i.e. is not below 0)
        previous = self._first_id if id < self._first_id else id
        self.active = self.get_node(previous)
        return previous

    def next_verse(self, id=""):
        id = self.get_id() if id == "" else id
        id = id + 1
        # Check verse still exists (i.e. is not above 31102)
        next = self._last_id if id > self._last_id else id
        self.active = self.get_node(next)
        return next

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
        for path in self.nodes_path:
            verses = self._read_verses(path)
            # print(verses[0:3])
            self.bible.add_nodes_from(verses)

        return

    def _init_crossrefs(self):
        """Add cross-references to graph."""
        crossrefs = self._read_crossrefs()
        self.bible.add_edges_from(crossrefs)
        return

    def _read_verses(self, path):
        """Reads json and returns list of verses [ tuple1(id, dict<attrs>), tuple2(id, dict<attrs>), ... ]."""
        # data = []
        # for path in self.nodes_path:
        #     with open(path, 'r') as config_file:
        #         data_loaded = json.load(config_file)
        #         data += data_loaded
        #         # print(data[0:1])

        with open(path, 'r') as config_file:
            data_loaded = json.load(config_file)
            data = data_loaded

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
    
    def get_cooccurence(self, ids=[]):
        """Get the co_occurence graph of a given id, or given ids."""
        # Initialise
        ids = self.get_id if ids == [] else ids
        ids = [ids] if type(ids) is int else ids
        builder = None

        # Create co_occurence of all given ids
        for id in ids:
            verse = self.get_strongs(id, no_stopwords=True)
            strongs = verse["strongs"]
            attrs = verse["english"]
            cooccurence = Co_Occurence(strongs, nodes_attrs=attrs, label=self.get_name(id))
            builder = builder.merge(cooccurence) if builder else cooccurence

        return builder

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
    nodes = [23949, 1, 22151, 27169, 12354]
    # nodes = [x for x in range(0, 31100, 1780)]
    # nodes = [28375, 5842, 27169]

    # low 
    node = 0
    node2 = 24335
    # print(f"Your current verse is:\n{network.get_node(node)}")
    # # print(network.get_strongs(node))
    # cooccurence = network.get_cooccurence(node)

    # node = 24230
    # print(f"Your current verse is:\n{network.get_node(node)}")
    # print(network.get_best_subgraph(node))

    # for node in nodes:
    #     subgraph_nodes = network.get_best_subgraph(node).nodes
    #     print(f"\n{network.get_name(node)}")
    #     print(f"{network.get_verse(node)}")
    #     # print(f"\nGet topics")
    #     # print(f"{network.get_topics(node)}")
    #     # print("\nGet related topics")
    #     # print(f"{network.get_related_topics(node)}")
    #     # print("\nGet topic count")
    #     # print(f"{network.count_topics(G=network.get_best_subgraph(node), weighted=False)}\n")

    #     cooccurence = network.get_cooccurence(subgraph_nodes)
    #     cooccurence.print_report(k=5)



    # for node in nodes:
    #     print(f"\n{network.get_name(node)}")
    #     print(f"{network.get_verse(node)}")
    #     cooccurence = network.get_cooccurence([node, node-1, node+1])
    #     cooccurence.print_report(k=5)
    # cooccurence = network.get_cooccurence([node, node-1, node+1])
    # print(cooccurence.get_centrality_measures())
    # print(network.get_cooccurence(node))
    # print(network.get_crossrefs_ids(node, 5, True))
    # print(network.get_best_subgraph(node))
    # print(network.get_shortest_path(node, node2))
    # print("EGT PATH SUBGRAPH")
    # graph = network.get_path_related_subgraph(node, node2)
    # print(network.get_path_related_subgraph(node2, node))
    # print(network.get_passage(1, 3, 2))
    
    # node = network.get_id_by_name("Matthew.3.4")
    # print(network.get_crossrefs_ids(node, 5, preprocess=True))

    # node = 28697
    # network.get_best_subgraph(node)
    # results = network.k_test(1500)
    # write_json(results, dump_path)
    # network.test_attributes(node)