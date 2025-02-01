import csv
import json
from strongs import StrongsDict

# Convert verses.csv into a readable data structure
# list<tuples> where a tuple is (id, dict<name, book, chap, verse>)

def get_topic_dict():
    """ Return JSON dictionary for topics"""
    return read_json("topic_dict.json")

def read_json(path):
        """Reads json and returns it"""
        with open(path, 'r') as config_file:
            data_loaded = json.load(config_file)
        
        return data_loaded

STRONGS_DICT = StrongsDict()
NOT_WORDS = ["...", "", "vvv", "-", " ", ".", "..", "...."]
TOPIC_DICT = get_topic_dict()
    
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

def unpack(row, key, main_key, dl="|"):
    value = row[main_key].split(dl)
    index = main_key.split(dl).index(key)
    return value[index]

def assign_strong_greek(path, books_path):
    """Reads Greek New Testament and applies Strongs words for a given verse."""
    bible_books = create_bible_dict(books_path)
    greek_bible = {}
    count = 0
    current = ""
    verse = []
    data = {}
    _verse = "Book|Chapter|Verse"
    _greek = "OGNTk|OGNTu|OGNTa|lexeme|rmac|sn"
    _transliteration ="transSBLcap|transSBL|modernGreek|Fonética_Transliteración"
    _translation = "TBESG|IT|LT|ST|Español"
    _strongs = "sn"
    _get_greek = "OGNTk"
    _get_trans = "transSBL"
    _get_eng = "ST"
    dl = "|"

    print("Reading strongs greek...")

    # Read open_greek_nt.csv and create list of verses
    with open(path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, delimiter='\t')

        # Get verse data from each row
        for rows in csvReader:

            if current != rows[_verse] and current != "": 
                # if a new verse, store previous verse
                bk, ch, vs = current.split(dl)
                bk = lookup_book(str(int(bk) - 1), bible_books)
                key = f"{bk}.{ch}.{vs}"
                greek_bible[key] = verse
                verse = []

            data = {}
            current = rows[_verse]
            data["sn"] = unpack(rows, _strongs, _greek)
            data["lemma"] = unpack(rows, _get_greek, _greek)
            data["translit"] = unpack(rows, _get_trans, _transliteration)
            data["eng"] = unpack(rows, _get_eng, _translation)

            # If not a word, do not add
            if data["eng"] in NOT_WORDS:
                continue

            # Check if stop word
            try:
                data["stop_word"] = STRONGS_DICT.is_stopword(data["sn"])
            except KeyError:
                data["stop_word"] = False

            # Add the word
            verse.append(data)
            count = count + 1

            # if count == 10:
            #     print(greek_bible)
            #     break

        if current:
                # add final verse
                bk, ch, vs = current.split(dl)
                bk = lookup_book(str(int(bk) - 1), bible_books)
                key = f"{bk}.{ch}.{vs}"
                greek_bible[key] = verse
    
    return greek_bible

def assign_strong_hebrew(path, books_path):
    """Reads Hebrew Old Testament and applies Strongs words for a given verse."""
    bible_books = create_bible_dict(books_path)
    hebrew_bible = {}
    count = 0
    current = ""
    verse = []
    data = {}
    _verse = "〔KJVverseSort｜KJVbook｜KJVchapter｜KJVverse〕"
    _strongs = "extendedStrongNumber"
    _get_hebrew = "BHSwordPointed"
    _get_trans = "SBLstyleTransliteration"
    _get_type = "morphologyCode"
    _get_eng = "extendedGloss"
    dl = "｜"

    print("Reading strongs hebrew...")

    # Read open_hebrew_ot.csv and create list of verses
    with open(path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, delimiter='\t')

        # Get verse data from each row
        for rows in csvReader:

            if current != rows[_verse] and current != "": 
                # if a new verse, store previous verse
                x, bk, ch, vs = current.split(dl)
                vs = vs.replace("\u3015", "")
                bk = lookup_book(str(int(bk) - 1), bible_books)
                key = f"{bk}.{ch}.{vs}"
                hebrew_bible[key] = verse
                verse = []

                # print(greek_bible)

            data = {}
            current = rows[_verse]
            data["sn"] = rows[_strongs]
            data["lemma"] = rows[_get_hebrew].replace('<heb> </heb>', "").replace('<heb>', "").replace('</heb>', "")
            data["translit"] = rows[_get_trans]
            data["type"] = rows[_get_type]
            data["eng"] = rows[_get_eng]

            # If not a word, do not add
            if data["eng"] in ["...", "", "vvv"]:
                continue

            # Check if a stop word
            try:
                data["stop_word"] = STRONGS_DICT.is_stopword(data["sn"])
            except KeyError:
                # print(data, rows[_verse])
                data["stop_word"] = False

            # Add the word
            verse.append(data)
            count = count + 1

            # if count == 10:
            #     print(greek_bible)
            #     break

        if current:
                # add final verse
                x, bk, ch, vs = current.split(dl)
                bk = lookup_book(str(int(bk) - 1), bible_books)
                vs = vs.replace("\u3015", "")
                key = f"{bk}.{ch}.{vs}"
                hebrew_bible[key] = verse
                print(key, verse)
    
    return hebrew_bible

def assign_strong_to_esv(path):
    """
    Reads Strong csv and creates array representing the Strongs words for a given verse.

    e.g. 
    $Gen 1:1	03=<07225>	04=<00430>	05=<01254>	07=<08064>	10=<00776>	
    is equal to Gen 1: In the beginning	<07225>, God <00430> created <01254> the heavens <08064> and the earth <00776>
    is represented as [[],[],[07225],[00430],[01254],[],[08064],[],[], 00776]
    """

    strongs_dict = {}
    count = 0
    
    print("Reading Strongs data...")
    with open(path, encoding='utf-8') as strongs:
        for x in strongs:
            x = x.strip().replace("+00", "000").replace(".\t", "=")
            if x.startswith("$"):
                # Initialise
                words = x.split("\t")
                code = []
                verse = words[0].replace("$", "")   # Get verse

                print(words)

                 # Validate indexes
                length = len(words)
                for i, ind in enumerate(words):
                    if i != 0: # i.e. don't check the verse
                        try:
                            prev, v = words[i - 1].split("=")
                        except ValueError:
                            prev = "00"

                        try:
                            next, z = words[i + 1].split("=")
                        except IndexError:
                            next, z = words[i].split("=")
                        
                        current, y = words[i].split("=")
                        current = current.split("+")
                        next = next.split("+")
                        prev = prev.split("+")

                        # if current index is larger than the next, something is wrong

                        # print(prev, current, next)
                        if int(current[0]) > int(next[0]):  
                            current = next[0]
                            words[i] = f"{current}={y}"
                            next = str(int(next[0]) + 1)
                            words[i+1] = f"{next}={z}"

                        # if current index is much larger than previous, something is wrong
                        elif int(current[0]) > ( int(prev[0]) + 10):
                            current = int(prev[0]) + 1
                            words[i] = f"{current}={y}" 


                # print(f"scrubbed {words}")
                prev_index = 0
                k = 0

                # Assign strong word to index
                while len(words) > 1:
                    k = k + 1
                    words = words[1:] 
                    index, word = words[0].split("=")
                    index = index.strip()
                    index = index[0].split("+")

                    # If index matches
                    if int(index[0]) == k:
                        word = word.replace("<", "").replace(">", "").split("+")
                        words.pop(0)
                        # If multiple indexes given
                        for i in index:
                            code.append(word)
                    else :
                        code.append([])

                    # print(k, words)
                    if k == 57: 
                        raise LookupError

                # if count == 118: 
                #         raise LookupError

                strongs_dict[verse] = code
                # print(strongs_dict)
                count = count + 1

                if count % 100 == 1:
                    print(f"Converting {verse}")

    print("Built Strongs data...")
    return strongs_dict



    # for x in open(path, "r"):
    #     x = x.strip()
    #     print(x)
    #     if x[0] == "$":
    #         print(x)

    #     count = count + 1
    #     if count == 10:
    #         break

def create_similar_topics_dict(all_topics):
    """Identify similar topics and group them."""
    topics_dict = {}
    SMALL_WORDS_TO_KEEP = ["word"]
    TOPICS_TO_KEEP = ["kingdom of god", "promised land", "speaking in tongues", "holy spirit", "the spirit of", "holy ghost", "gods word", "the word"
                      "seeking gods will", "seeking knowledge", "spiritual leader", "the word"]
    TOPICS_TO_DELETE = ["tests", "bethany", "others", "moving", "people", "spirit", "ghost", "stubborn women", "revel", "yourself", "family", "loving", "giving", "stand"]
    SUBTOPICS_TO_DELETE = {"black": ["black magic"], "rejoicing": ["rejoicing in the truth"],
                           "tongue": ["speaking in tongues", "talking in tongues", "speaking in tongue jesus", "the gift of tongues"],
                           "the spirit": ["the spirit of rejection", "the spirit of religion", "the spirit of pride", "the spirit of man", "the spirit of witchcraft", "the spirit of"],
                           "seeking": ["seeking wisdom", "seeking knowledge", "seeking gods will", "seeking revenge", "self seeking"],
                           }
    TOPICS_TO_RENAME = {"black": "black (skin colour)", "confess": "confessing sin", "theory": "scientific theories", "living": "godly living",
                        "overcoming": "overcoming temptation / sin", "world": "the world", "forsake": "leaving / forsaking", "the spirit": "in the spirit", "the spirit of": "spiritual evils",
                        "holy ghost": "holy spirit", "tattoo": "tattoos", "word": "our words", "seeking": "seeking god", "gods will": "knowing gods will",
                        "the word": "gods word", "humble": "humility", "forgive": "forgiveness", "rude": "rudeness", "being rude": "rudeness", "loving each other": "loving others", "offering": "tithing", "tithe": "tithing",
                        "spiritual": "life in the spirit", "understanding": "knowledge", "knowledge": "knowledge / understanding", "selfless": "selflessness",
                        "special": "being special", "relationship": "relationships"}
    # "tattoo": "tattoos",  #"the word": "gods word", 
    SUBTOPICS_TO_ADD = {"selfish": ["self seeking"], "humility": ["humble"], "kindness": ["kind"], "love": ["loving"], 
                        "generosity": ["giving", "giving to others", "gift giving", "giving money"], 
                        "giving to the poor": ["giving to others in need", "giving to the needy"],
                        "tithing": ["giving money to the church", "giving 10 percent", "giving to your pastor"],
                        "gods word": ["word of god",  "gods word"], "confessing sins": ["confession of sin"]} 
    SUBTOPICS_TO_SUBTRACT = {"our words": "gods word", }

    # Find subtopics and group them under parents
    for topic in all_topics:
        for x in all_topics:

            contains_topic = (f"{topic} " in x) or (f" {topic}" in x) or (f"{topic}ity" in x) or (f"{topic}s" in x) or (f"{topic}ing" in x) or (f"{topic}ship" in x) or (f"{topic}ness" in x)

            if contains_topic and topic is not x and (len(topic) > 4 or topic in SMALL_WORDS_TO_KEEP):
                if topic in topics_dict:
                    topics_dict[topic].append(x)
                else: 
                    topics_dict[topic] = [x]

    # Remove any unhelpful / vague parent topics

    for topic in TOPICS_TO_DELETE:
        topics_dict.pop(topic, None)
        print(f"deleting {topic}") 

    # Remove any children that are also parents
    x = dict(topics_dict)
    for topic, subtopics in x.items():
        for key in x.keys():
            if topic in key and topic is not key:
                if key in TOPICS_TO_KEEP: # ignore it
                    continue
                topics_dict.pop(key, None)
                print(f"{key} ---> {topic}")
             
    
    print("\nDELETING")
    # Remove subtopics
    for topic, subtopics in SUBTOPICS_TO_DELETE.items():
        for subtopic in subtopics:
            topics_dict[topic].remove(subtopic)
            print(f"{subtopic} from {topic}")

    # Rename topics
    print("\nRENAMING")
    for topic in TOPICS_TO_RENAME:
        new_name = TOPICS_TO_RENAME[topic]

        # If topic to rename does not exist
        if topic not in topics_dict:
            topics_dict[topic] = []

        # If new name already exists, merge
        if new_name in topics_dict:
            topics_dict[new_name] = topics_dict[topic] + topics_dict[new_name] + [topic]
        else:
            topics_dict[new_name] = topics_dict[topic] + [topic]
        
        topics_dict.pop(topic)         
        print(f"{topic} ---> {new_name}")

    print("\nADDING")
    for topic, add_subtopics in SUBTOPICS_TO_ADD.items():
        for subtopic in add_subtopics:
            if topic in topics_dict:
                topics_dict[topic].append(subtopic)
            else:
                topics_dict[topic] = [subtopic]
            print(f"{topic} += {subtopic}")

    print("\nSUBTRACTING")
    for topic, minus_topic in SUBTOPICS_TO_SUBTRACT.items():
        x =  list(set(topics_dict[topic]) - set(topics_dict[minus_topic]))
        topics_dict[topic] = x
        print(f"{topic} no longer contains {minus_topic}")
        print(topics_dict[topic])

    print("\n")
    write_json(topics_dict, "all_topics_dict.json")
    

def flip_dict(index):
    inverse = {}
    for k,v in index.items():
        for x in v:
            inverse.setdefault(x, []).append(k)
    
    return inverse

def write_topic_dict():
    """Build and write a topic_dict to json files."""
    create_similar_topics_dict(read_json("all_topics.json"))
    all_topics = read_json("all_topics_dict.json")
    write_json(flip_dict(all_topics), "topic_dict.json")

def sophisticated_topics(path):
    """Iterate over every topic and group similar topics. Then normalise."""
    builder = {}
    topics = []
    count = 0

     # Preprocess topics.csv
    with open(path, encoding='utf-8') as csvt:
        csvReader = csv.DictReader(csvt)
        for rows in csvReader:
            # Retreive topic data
            topic = rows['Topic']
            verse = rows['Verse'].split('-')[0]
            weight = rows['Votes']

            topic_og = topic

            # Combine similar topics
            if topic in TOPIC_DICT:
                topic = TOPIC_DICT[topic][0]

            if topic == "being rude": 
                print(f"{topic} !! dict: {TOPIC_DICT[topic]} data: {verse}, {weight}")


            weight = int(weight)
            
            # Add to builder
            if topic not in builder:
                builder[topic] = {verse: weight}
            elif verse not in builder[topic]:
                builder[topic][verse] = weight
            else:
                # print(f"Duplicate! {topic_og} ---> {topic} with {verse, weight}")
                builder[topic][verse] += weight 

            # if count > 350:
            #     break

            count = count + 1

    for topic, verses in builder.items():
        # Reformat topic data
        values = []
        for verse in verses:
            weight = verses[verse]
            values.append((topic, verse, weight))

        # Normalise topic data
        values = normalise_weights(values)
        topics.append(values)
                         
    return topics

def read_topics(path):
    """Lazily iterate over every topic and normalise. Cannot handle similar topic groups."""
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

            if count > 330: 
                return topics

    return topics

def assign_topics(path): 
    """
    Reads topics.csv and assigns topic-weight pair to verses dictionary.
    """
    # topics = read_topics(path)
    topics = sophisticated_topics(path)
    topic_dict = {}

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
        # normalised.append((topic, verse, weight))    
        if is_significant(weight, 0):
            normalised.append((topic, verse, weight))    

    # print(f"appending {len(normalised)} verses for {group[0][0]}")
    return normalised

def is_significant(x, threshold):
    threshold = threshold * 100
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

def read_verses(verses_path, books_path, topics_path, strongs_path):
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
    strongs = read_json(strongs_path)

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
            # data["strongs"] = strongs[data['name']] if data['name'] in strongs else [] #if verse has strongs, assign strongs

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


def write_nodes(data, path):
    """Write list of nodes to nodes.json"""

    x = int( len(data) / 2 )
    data1 = data[:x]
    data2 = data[x:]

    x = int( len(data2) / 2)
    data3 = data2[:x]
    data4 = data2[x:]

    x = int( len(data4) / 2)
    data5 = data4[:x]
    data6 = data4[x:]

    data = [data1, data3, data5, data6]
    xpath, x = path.split(".")

    # Write all files in form data1.json, data2.json, etc
    for i, data in enumerate(data):
        path = f"{xpath}{i + 1}.json"
        with open(path, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(data, indent=4))
            print(f"Successfully written nodes to {path}")

if __name__ == "__main__":
    verses_csv = r'bible-esv.csv'
    books_csv = r'bible-taxonomy.csv'
    topics_csv = r'bible-topics.csv'
    nodes_path = r'nodes.json'
    lookup_path = r'verse_lookup.json'
    esv_strong_path = r'strong-tags-for-esv.txt'
    strongs_greek_path = r'strongs_open_greek_nt.csv'
    strongs_greek_path = r'new_strongs_open_greek_nt.tsv'
    strongs_hebrew_path = r'strongs_open_hebrew_bible.csv'

    strongs_greek_write = r"strongs-greek.json"
    strongs_heb_write = r"strongs-hebrew.json"
    translation_path = r"strong-translation.json"

    # greek = assign_strong_greek(strongs_greek_path, books_csv)
    # write_json(greek, strongs_greek_write)
    # hebrew = assign_strong_hebrew(strongs_hebrew_path, books_csv)
    # write_json(hebrew, strongs_heb_write)
    # greek.update(hebrew)
    # write_json(greek, translation_path)

    # Read verses and write in graph-readable format

    print("Writing topics...")
    write_topic_dict()

    print("Writing verses...")
    verses, verse_lookup = read_verses(verses_csv, books_csv, topics_csv, translation_path)
    write_nodes(verses, nodes_path)
    # write_json(verse_lookup, lookup_path)