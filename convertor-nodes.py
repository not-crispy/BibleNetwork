import csv
import json
from strongs import StrongsDict

# Convert verses.csv into a readable data structure
# list<tuples> where a tuple is (id, dict<name, book, chap, verse>)

STRONGS_DICT = StrongsDict()
    
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
            try:
                data["stop_word"] = STRONGS_DICT.is_stopword(data["sn"])
            except KeyError:
                data["stop_word"] = False
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
            try:
                data["stop_word"] = STRONGS_DICT.is_stopword(data["sn"])
            except KeyError:
                # print(data, rows[_verse])
                data["stop_word"] = False
            verse.append(data)

            # print(f"verse: {current} sn: {data["sn"]} greek: {data["word"]} trans: {data["trans"]} eng: {data["eng"]}")
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

    # print(f"appending {len(normalised)} verses for {group[0][0]}")
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
            data["strongs"] = strongs[data['name']] if data['name'] in strongs else [] #if verse has strongs, assign strongs

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

def read_json(path):
        """Reads json and returns it"""
        with open(path, 'r') as config_file:
            data_loaded = json.load(config_file)
        
        return data_loaded
    

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

    greek = assign_strong_greek(strongs_greek_path, books_csv)
    write_json(greek, strongs_greek_write)
    hebrew = assign_strong_hebrew(strongs_hebrew_path, books_csv)
    write_json(hebrew, strongs_heb_write)
    greek.update(hebrew)
    write_json(greek, translation_path)

    # Read verses and write in graph-readable format
    verses, verse_lookup = read_verses(verses_csv, books_csv, topics_csv, translation_path)
    write_json(verses, nodes_path)
    # write_json(verse_lookup, lookup_path)