import csv
import json
import re

def read_serendipity(data_path, words):
    """
    Reads serendipity.csv
    """
    array = []
    string = ""
    dict = { x: [] for x in ['all', 0, 1, 2, 3, 4, 5, 'closeness', 'betweens', 'degree', 'sum']}
    threshold = 26
    dict[f'under-{threshold}'] = []
    dict[f'over-{threshold}'] = []

    # Read verses.csv and create list of verses
    with open(data_path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:
            for key, value in row.items():
                row[key] = int(value) if key == 'cutoff' or key == 'nodes' else float(value)

            cutoff = row['cutoff']
            nodes = row['nodes']
            
            coords = get_coords('serendipity', 'per_node', row)
            dict['all'].append(coords)
            dict[cutoff].append(coords)
    
            # delineate by number of nodes in graph
            dict[f'under-{threshold}'].append(coords) if nodes < threshold else dict[f'over-{threshold}'].append(coords)

            # get centrality measures
            for centrality in ['betweens', 'closeness', 'degree']:
                coords = get_coords(centrality, 'per_node', row)
                dict[centrality].append(coords)

            sum = ( row['betweens'] + row['closeness'] + row['degree'] ) / ( row['cutoff'] + 1)
            coords = (round(sum, 4) , row['per_node'])

            dict['sum'].append(coords)

    return dict

def get_coords(x, y, row):
    x = row[x] if x == 'betweens' else row[x] 
    y = row[y] if y == 'betweens' else row[y]
    return (x, y)

def clean(path, clean_path, words):
    string = ""
    for word in words:
        string = string + f"{word},"
    string = string.strip(",") + '\n'

    with open(path, encoding='utf-8') as f:
        for rows in f:
            rows = rows.replace(': ', ':')
            for word in words:
                rows = rows.replace(f'{word}:', '')
            rows = rows.replace(' ', ',').replace(',,', '!')
            rows = re.sub(',(,)+', '', rows).replace('!', ' ')
            string = string + rows

    string = re.sub('(\n)+','\n', string)
    string = re.sub(',[\n]', '\n', string)
    
    write(string, clean_path)

def write(data, path):
    """Write data_structure to given path"""
    with open(path, 'w', encoding='utf-8') as f:
        data = str(data).strip('[').strip(']')
        data = re.sub('], ', '],\n', data)
        data = data.replace('{', '{\n').replace('}', '\n}')
        data = data.replace('[', '').replace('],', '').replace(']', '').replace(': ', ':\n')
        f.write(data)

    print(f"Successfully written verses to {path}")
    
if __name__ == "__main__":
    serendipity_csv = r'tests/serendipity.csv'
    path = r'tests/serendipity-input.csv'
    words = ['factor', 'cutoff', 'per_node', 'nodes', 'serendipity', 'degree', 'closeness', 'betweens']

    clean_path = r'tests/clean.csv'
    test_path = r'tests/serendipity_results.txt'

    # Read verses and write in graph-readable format
    clean(path, clean_path, words)
    array = read_serendipity(clean_path, words)
    write(array, test_path)
