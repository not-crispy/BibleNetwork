import csv
import json

def create_bible_dict(path):
    """
    Reads taxonomy.csv and creates a dictionary of bible books and their associated metadata:

    short -- abbreviated name of book
    name -- full name of book
    total -- number of chapters in book
    volume -- "OT" or "NT"
    """

    bible_books = {}
     
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
    
    return bible_books

def decode(code):
    bk = str(int(code[:2]) - 1)
    ch = int(code[2:5])
    vs = int(code[-3:])
    return bk, ch, vs

def get_name(bk, ch, vs):
    return f"{bk}.{ch}.{vs}"

def preprocess_votes(path, books_path):
    bible_books = create_bible_dict(books_path)
    data = [['Topic', 'Verse', 'Votes']]

    with open(path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
         
        # Get verse data from each row
        for rows in csvReader:
            topic = rows["Topic"]
            code = rows["Start"]
            endcode = rows["End"]
            votes = rows["Votes"]
            
            # convert code to form Exod.20.1
            bk, ch, vs = decode(code)
            bk = bible_books[bk]['short']
            name = get_name(bk, ch, vs)
        
            # append row
            row = [topic, name, votes]
            data.append(row)

            # TO DO : How to parse verse chunks ?

            if endcode:
                bk2, ch2, vs2 = decode(endcode)
                while vs2 > vs:
                    vs = vs + 1
                    name = get_name(bk, ch, vs)
                    data.append([topic, name, votes])

    return data

def write_csv(path, data):
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

    print(f"Written topics to {path}")

if __name__ == "__main__":
    books_csv = r'bible-taxonomy.csv'
    topics_csv = r'topic-votes.csv'
    topics_csv_new = r'bible-topics.csv'

    # Read verses and write in graph-readable format
    data = preprocess_votes(topics_csv, books_csv)
    write_csv(topics_csv_new, data)