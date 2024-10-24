import csv
import json

# Convert verses.csv into a readable data structure
# list<tuples> where a tuple is (id, dict<name, book, chap, verse>)

    
def create_bible_dict(path):
    """
    Reads taxonomy.csv and creates a dictionary of bible books and their associated metadata:

    short -- abbreviated name of book
    name -- full name of book
    total -- number of chapters in book
    volume -- "OT" or "NT"
    """
    bible_books = {}
    taxon = {}
     
    with open(path, encoding='utf-8') as books:
        csvReader = csv.DictReader(books)

        # Create keys for every book in the Bible
        for rows in csvReader:
            bible_books[rows['BookID']] = {
                'short': rows['Short'],
                'name': rows['Name'],
                'total': rows['TotalChapters'],
                'volume': rows['Volume'],
            }
            taxon[rows['Name']] = {
                'short': rows['Short'],
                'id': rows['BookID'],
                'total': rows['TotalChapters'],
                'volume': rows['Volume'],
                'spellings': [rows['Short'], rows['Name']]
            }

    # with open("bible.json", 'w', encoding='utf-8') as jsonf:
    #     jsonf.write(json.dumps(taxon, indent=4))

    return bible_books

def assign_topics(path): 
    """
    Reads topics.csv and assigns topic-weight pair to verses dictionary.
    """
    topic_dict = {}
    topics = []
    group = []
    previous = None
    count = 0

    # Preprocess topics.csv
    with open(path, encoding='utf-8') as csvt:
        csvReader = csv.DictReader(csvt)
        for rows in csvReader:
            # Retreive topic data
            topic = rows['Topic']
            verse = rows['Verse'].split('-')[0]
            weight = rows['Votes']

            # If we're looking at a new topic...
            # normalise and add previous group
            if previous != topic and previous != None:
                group = normalise_weights(group)
                topics.append(group)
                group = [] #start new group
            
            data = (topic, verse, weight)
            group.append(data)
            previous = topic
            count += 1

            # if count > 130: 
            #     break

   # Once preprocessed, assign topics to verses
    for t in topics:
        for item in t:
            topic, verse, weight = item

            # check if verse exists...
            if verse in topic_dict :
                topic_dict[verse].append((topic, weight))
            else:  
                topic_dict[verse] = [(topic, weight)] # if does not exist, create it

    return topic_dict

def normalise_weights(group):
    """Count the total weights of a group, and normalise it."""
    max = 0
    min = 0
    data = 2
    sum = 0
    normalised = []

    # get max / min
    for item in group:
        weight = int(item[2])
        max = weight if weight > max else max
        min = weight if weight < min else min
        sum += weight

    for item in group:
        # Normalise
        topic, verse, weight = item
        n = (int(weight) - min + 1) / (max - min + 1)
        weight = int(n * 100)
        weight = scale(weight, max)
        if is_significant(weight, 100):
            normalised.append((topic, verse, weight))    

    print(f"appending {len(normalised)} verses for {group[0][0]}")
    return normalised

def is_significant(x, threshold):
    threshold = threshold * 0.40
    return True if x > (threshold) else False

def scale (x, threshold):

    if threshold < 50:
        factor = 0.4
    elif threshold < 250:
        factor = 0.6
    elif threshold < 500:
        factor = 0.7
    elif threshold < 1000:
        factor = 0.8
    elif threshold < 2500:
        factor = 0.9
    else: 
        factor = 1

    return int( x * factor )

def lookup_book (index, books, abbrev=True):
    key = 'short' if abbrev == True else 'name'
    return books[index][key]

def read_verses(verses_path, books_path, topics_path):
    """
    Reads verses.csv and returns a list of verse tuples: (id, dict<name, book, chap, verse>) where

    name -- the verse code (e.g. Gen.1.2)
    book -- the book name (e.g. Gen)
    chap -- the chapter (e.g. 1)
    verse -- the verse (e.g. 2)
    """
     
    # create data structures
    data = {}
    verses = [] # array of dicts
    verse_lookup = {}
    id = 0
    bible_books = create_bible_dict(books_path)
    topics = assign_topics(topics_path)

    # Read verses.csv and create list of verses
    with open(verses_path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
         
        # Get verse data from each row
        for rows in csvReader:
            data = {}
            index = rows['book']
            data["name"] = lookup_book(index, bible_books) + "." + rows['chapter'] + "." + rows['verse']
            data["content"] = rows['content']
            data["book"] = lookup_book(index, bible_books, abbrev=False)
            data["chap"] = rows['chapter']
            data["verse"] = rows['verse']
            data["version"] = "ESV"
            data["id"] = id
            data["topics"] = topics[data['name']] if data['name'] in topics else [] # if verse has topics, assign topics
            
            # Create verse node
            verse = (id, data)
            #verse = (id, data)
            verses.append(verse)
            verse_lookup[data["name"]] = id
            id += 1

            # if count % count_init >= 2500:
            #     break;
 
    return verses, verse_lookup

def write_json(data, path):
    """Write data_structure to given path"""
    with open(path, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))

    print(f"Successfully written verses to {path}")

if __name__ == "__main__":
    verses_csv = r'bible-esv.csv'
    books_csv = r'bible-taxonomy.csv'
    topics_csv = r'bible-topics.csv'
    nodes_path = r'nodes.json'
    lookup_path = r'verse_lookup.json'

    # Read verses and write in graph-readable format
    verses, verse_lookup = read_verses(verses_csv, books_csv, topics_csv)
    write_json(verses, nodes_path)
    write_json(verse_lookup, lookup_path)