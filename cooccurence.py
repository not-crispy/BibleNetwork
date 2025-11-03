import networkx as nx
from strongs import StrongsDict
class Co_Occurence:
    """A graph that stores and manipulates co-occurence data.
    
    Nodes are words (usually Hebrew or Greek).
    Edges are associations between words.
    """
    def __init__(self, nodes_list, nodes_attrs=[], edges_list=[], label="verses"):
        self.graph = nx.Graph()
        
        # Replace synonyms
        nodes_list = self.replace_synonyms(nodes_list)

        # Create network
        if nodes_attrs:
            nodes = [(nodes_list[i], {"label": nodes_attrs[i]}) for i, node in enumerate(nodes_list)]
        else:
            nodes = nodes_list
            
        self.graph.add_nodes_from(nodes)
        self.label = label

        # Add associations ("edges")
        if edges_list:
            self.graph.add_edges_from(edges_list)
        else:
            self.initialise_edges(nodes_list)

    def replace_synonyms(self, nodes_list):
        """Returns the nodes_list, with any synonyms replaced with a primary word."""
        x = []
        synonyms = StrongsDict().get_synonyms()

        # Build a new list of nodes with synoynms replaced
        for node in nodes_list:
            x.append(synonyms[node]) if node in synonyms else x.append(node)

        return x
    
    def initialise_edges(self, nodes_list):
        """Create an edge between every adjacent node in list. Increase weight for each repeated edge."""
        prev = None

        for node in nodes_list:
            # Add adjacent edge
            if prev: 
                self.add_edge(node, prev)
                prev = node
            # Skip on first loop
            else:
                prev = node
                continue

    def get(self):
        return self.graph
    
    def get_node_label(self, strongs):
        try: 
            return self.graph.nodes[strongs]['label']
        except KeyError:
            return ""
            
    def get_total_nodes(self):
        return len(self.graph.nodes)

    def add_edge(self, a, b, weight=1):
        """Add edge, if does not exist. Combine weights on repeat edges."""

        # Combine weight on repeat edge
        if self.graph.has_edge(a,b):
            self.graph[a][b]['weight'] += weight

        # Create a new edge
        else: 
            self.graph.add_edge(a, b, weight=weight)
    
    def merge(self, merge_graph):
        """Returns a Co_Occurence of a union of graph a and b. Combines weight on repeat edges."""
        # Create union of graph
        nodes = list(self.graph.nodes(data=True))+list(merge_graph.get().nodes(data=True))
        edges = self.graph.edges(data=True)
        label = f"{self.get_label()}+{merge_graph.get_label()}"
        merge = Co_Occurence(nodes, edges_list=edges, label=label)
        
        # Combine weight on repeat edges
        for edge in merge_graph.get().edges(data=True):
            a = edge[0]
            b = edge[1]
            weight = edge[2]['weight']
            merge.add_edge(a, b, weight)
            
        return merge
    
    def rich_str(self):
        return f"{str(self)}\n--- nodes: {self.get().nodes}\n--- edges: {self.get().edges(data=True)}"
    
    def get_centrality_measures(self):
        """Compute and return centrality measures.
        
        HOW TO INTERPRET (source: Czachesz, 2018)
        degree - These are dominant concepts in the passage. (i.e. are most well-connected)
        betweens - These words connect concepts.
        closeness - These are close to the centre of the network (i.e. part of its core)
        eigen - These words are part of more influential neighbourhoods
        frequency - Number of times word is in teh passage
        
        """
        key = lambda x:x[1]
        # sorted(footballers_goals.items(), key=key)
        betweens = sorted(nx.betweenness_centrality(self.get(), weight="weight").items(), key=key, reverse=True)
        degree = sorted(self.get_degree(nx.degree_centrality(self.get())).items(), key=key, reverse=True)
        eigen = sorted(nx.eigenvector_centrality(self.get(), max_iter=300).items(), key=key, reverse=True)
        closeness = sorted(nx.closeness_centrality(self.get(), distance="weight").items(), key=key, reverse=True)
        
        return {
            "degree": degree,
            "betweens": betweens,
            "closeness": closeness,
            "eigen": eigen
        }
    
    def get_centrality_measures_but_only(self, ids):
        """Returns centrality measures, but only of the given words.
        ids: a list of ids to keep"""

        measures = self.get_centrality_measures()
        ids = self.replace_synonyms(ids)
        new_measures = {}

        # Check every measure
        for measure, words in measures.items():
            new_words = []

            # Delete all words except those given
            for word in words:
                if word[0] in ids:
                    new_words.append(word)
            new_measures[measure] = new_words

        return new_measures

    def get_degree(self, measures):
        "Returns the degree of a node (as an int). k is the nodes' degree centrality measure."
        max_degree = self.get_total_nodes() - 1
        unnormalised_degrees = {key: value * max_degree for key, value in measures.items()}
        return unnormalised_degrees

    def _prepare_report(self, measures, strongs_dict=StrongsDict()):
        """Return a centrality report (replacing "strongs numbers" with actual words)"""
        centrality = measures
        report = {}

        for key in centrality:
            report[key] = []
            for word in centrality[key]:
                data = {
                    "strongs": word[0],
                    "translit": strongs_dict.get_translit(word[0]),
                    "english": strongs_dict.get_words(word[0]),
                    "score": word[1],
                    "label": self.get_node_label(word[0]),
                }
                report[key].append(data)

        return report
    
    def centrality_report(self, strongs_dict=StrongsDict()):
        """Returns centrality measures in the form of a dict report. 
        i.e. with keys: "strongs", "translit", "english", "score"
        """
        measures = self.get_centrality_measures()
        return self._prepare_report(measures, strongs_dict)

    def get_important_words_report(self, k=5, get_least=False, strongs_dict=StrongsDict()):
        """Returns the top k important words in the form of a dict report. 
        i.e. with keys: "strongs", "translit", "english", "score"
        """
        important_words = self.get_important_words(self.get_centrality_measures(), k, get_least)
        return self._prepare_report(important_words, strongs_dict)
    
    def get_only_these_words_report(self, ids, k=5, get_least=False, strongs_dict=StrongsDict()):
        """Returns the top k important words in the form of a dict report. 
        i.e. with keys: "strongs", "translit", "english", "score"
        """
        x = self.get_centrality_measures_but_only(ids)
        important_words = self.get_important_words(x, k, get_least)
        return self._prepare_report(important_words, strongs_dict)
    
    def get_important_words(self, measures=None, k=5, get_least=False):
        """Returns the top k important words for each centrality measure.
         
          get_least: Gets the least k important words instead."""
        
        measures = measures if measures else self.get_centrality_measures()

        if get_least:
            important_words = {key: value[::-1][:k]  for key, value in measures.items()}
        else :
            important_words = {key: value[:k]  for key, value in measures.items()}
        return important_words
    
    def print_report(self, k=-1, get_least=False, but_only=[]):
        """Print a report of top k important words in a readable format. 
        
        If but_only is given, print a report only containing these words."""
        x = "least important" if get_least else "important"
        total_nodes = self.get_total_nodes()
        k = total_nodes if k == -1 else k

        # Which report?
        if but_only:
            report = self.get_only_these_words_report(but_only, k, get_least) 
            total_nodes = len(set(but_only))
        else:
            report = self.get_important_words_report(k, get_least)

        print(f"Printing top {k} {x} words (total words: {total_nodes})")

        for measure, words in report.items():
            print(f"=== {measure.upper()} ===")
            for word in words:
                definition = ",".join(word['english'].replace("(","[").replace(")", "]").split(",")[:3])
                # english = word['label']
                # english = english if english else definition # if no label exists, get definition
                print(f"{round(word['score'], 4)}\t{word['translit']} ({definition}) | {word['strongs']}")
    
    def print(self):
        print(self.rich_str())

    def get_label(self):
        return self.label

    def __str__(self):
        return str(self.get()).replace("Graph", f"CoOccurence of {self.label}")

if __name__ == "__main__":
    strongs = ["G4000", "G434", "G121", "G434", "G4944"]
    strongs2 = ["G4000", "G434", "G4000", "G434", "G121", "G121"]

    graph = Co_Occurence(strongs)
    print(graph.get_centrality_measures())
    graph2 = Co_Occurence(strongs2)
    measures = graph.get_centrality_measures()
    print(measures)
    print("CENTRALITY REPORT")
    print(graph2.centrality_report())
    print("IMPORTANT WORDS")
    print(graph2.get_important_words(k=2))
    print(graph2.get_important_words(k=2, get_least=True))
    print(graph2.get_important_words_report(k=2, get_least=True))
    graph.print_report(k=5)
    # graph.print()
    # graph2.print()
    # graph3 = graph.merge(graph2)
    # graph3.print()








