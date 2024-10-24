import csv
import json
import math
import scipy.stats

# Convert cross-references.csv into a readable data structure
# list<tuples> where a tuple is (verse1, verse2, dict<id, weight>)

# Create INVERSE VERSE dictionary {verse: id}
with open(r'verse_lookup.json') as lookup:
    VERSE_LOOKUP  = json.load(lookup)

def get_id(verse):
    verse = verse.split('-')[0]
    return VERSE_LOOKUP[verse]

def read_edges(path):
    """
    Reads crossref.csv and returns a list of crossref tuples: (verse1, verse2, dict<id, weight, type>) where

    id -- the crossref id (e.g. 0)
    weight -- the crossref weight (e.g. 6)
    type -- the type of edge (e.g. "crossre")
    """
    # create data structures
    data = {}
    crossrefs = [] # array of dicts
    id = 0
    type = "crossref"
    group = []
    count = 0
     
    with open(path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        previous = None

        # Get crossref data from each row
        for crossref in csvReader:
            # init data
            data = {}
            data["id"] = id
            data["weight"] = crossref['Votes']
            data["type"] = type
            data["from"] = crossref['From']
            data["start"], x, data["end"] = crossref['To'].partition('-')

            # get node ids
            source = get_id(crossref['From'])
            target = get_id(crossref['To'])

            # Create crossref edge
            crossref = (source, target, data)
            crossrefs.append(crossref)
            id += 1

            # If we're looking at a new crossref group...
            if previous != source:
                normalise_weights_log(group) # normalise previous group
                # x = group.copy()
                # y = group.copy()
                # z = group.copy()
                # normalise_weights(x)
                # print(f"linear:\n{x}")
                # normalise_weights_zscore(y)
                # print(f"zscore:\n{y}")
                # normalise_weights_log(z)
                # print(f"log:\n{z}")

                group = [] #start new group
            
            # Remember the previous crossref...
            group.append(crossref)
            previous = source
            
    # Normalise final group
    normalise_weights(group)
    
    return crossrefs

def normalise_weights(crossrefs):
    """Count the total weights of a crossref group, and normalise it."""
    max = 0
    min = 0
    data = 2

    # get max / min
    for crossref in crossrefs:
        weight = int(crossref[data]['weight'])
        max = weight if weight > max else max
        min = weight if weight < min else min

    for crossref in crossrefs:
        # Normalise
        weight = int(crossref[data]['weight'])
        #print(weight - min, max - min)
        n = (weight - min + 1) / (max - min + 1)
        crossref[data]['weight'] = int(n * 100)


def normalise_weights_zscore(crossrefs):
    """Count the total weights of a crossref group, and normalise it."""
    data = 2
    values = []
    

    if len(crossrefs) == 0:
        return None

    # get mean
    for crossref in crossrefs:
        weight = int(crossref[data]['weight'])
        values.append(weight)

    zscores = scipy.stats.zscore(values)
    count = 0

    for crossref in crossrefs:
        # Normalise
        weight = int(crossref[data]['weight'])
        #print(weight - min, max - min)
        n = zscores[count]
        crossref[data]['weight'] = int(n * 100)
        count += 1

    normalise_weights(crossrefs)


def normalise_weights_log(crossrefs):  
    max = 0
    min = 0
    data = 2

    if len(crossrefs) == 0:
        return None

    # get max / min
    for crossref in crossrefs:
        weight = int(crossref[data]['weight'])
        max = weight if weight > max else max
        min = weight if weight < min else min
    
    for crossref in crossrefs:
        weight = int( crossref[data]['weight'] ) + abs(min) + 1
        n = math.log( weight )
        crossref[data]['weight'] = int(n * 100)

    normalise_weights(crossrefs)

def write_edges(verses, path):
    """Write list of edges to edges.json"""

    x = int( len(verses) / 2 )
    verses1 = verses[:x]
    verses2 = verses[x:]

    with open(f"{path}", 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(verses1, indent=4))

    xpath, x = path.split(".")

    with open(f"{xpath}2.json", 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(verses2, indent=4))

    print(f"Successfully written verses to {path}")

if __name__ == "__main__":
    edges_csv = r'cross-references.csv'
    edges_path = r'edges.json'

    # Read cross-references and write in graph-readable format
    edges = read_edges(edges_csv)
    write_edges(edges, edges_path)