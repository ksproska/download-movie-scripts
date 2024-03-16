import csv
import json
import os.path
from pprint import pprint
from fuzzywuzzy import fuzz


def csv_to_json(csv_file_path, jsons_dir):
    # Read CSV file
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # Convert CSV data to list of dictionaries
        data = list(csv_reader)

    for row in data:
        if 'Series_Title' in row:
            row['Title'] = row.pop('Series_Title')

    for row in data:
        if 'IMDB_Rating' in row:
            row['IMDB_Rating'] = float(row['IMDB_Rating'])

    for row in data:
        if 'Gross' in row:
            if row['Gross'] == '':
                row['Gross'] = None
            else:
                row['Gross'] = int(row['Gross'].replace(",", ""))

    for row in data:
        if 'Meta_score' in row:
            if row['Meta_score'] == '':
                row['Meta_score'] = None
            else:
                row['Meta_score'] = int(row['Meta_score'])

    for row in data:
        if 'No_of_Votes' in row:
            row['No_of_Votes'] = int(row['No_of_Votes'])

    for row in data:
        if 'Runtime' in row:
            if not row['Runtime'].endswith(" min"):
                raise Exception
            row['Runtime'] = int(row['Runtime'].replace(" min", ""))
            row['Runtime_minutes'] = row.pop('Runtime')

    for row in data:
        if 'Released_Year' in row:
            try:
                row['Released_Year'] = int(row['Released_Year'])
            except:
                row['Released_Year'] = None

    # Split Genre field by ", " and map to list
    for row in data:
        if 'Genre' in row:
            row['Genre'] = row['Genre'].split(", ")

    # Map Star1, Star2, Star3, Star4 to Stars field as list of strings
    for row in data:
        stars = []
        for i in range(1, 5):
            star_key = f"Star{i}"
            if row.get(star_key):
                stars.append(row[star_key])
            del row[star_key]
        row['Stars'] = stars

    filenames = [x.replace(".txt", "") for x in os.listdir('./scripts')]

    movies_without_scripts = []
    for row in data:
        if os.path.exists(f"./scripts/{row['Title']}.txt"):
            row['Script_path'] = f"{row['Title']}.txt"
        elif os.path.exists(f"./scripts/{row['Title'].replace('The ', '')}.txt"):
            row['Script_path'] = f"{row['Title'].replace('The ', '')}.txt"
        else:
            similarity_scores = [(string, fuzz.ratio(row['Title'], string)) for string in filenames]
            sorted_list = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            most_similar_string, similarity_score = sorted_list[0]
            if similarity_score > 80:
                row['Script_filename'] = f"{most_similar_string}.txt"
            else:
                movies_without_scripts.append(row['Title'])

    print(len(movies_without_scripts), "/", len(data))
    pprint(movies_without_scripts)
    pprint(filenames)

    # Write JSON file
    for i, row in enumerate(data):
        with_script = ""
        if 'Script_filename' in row:
            with_script = "_with_script"
            with open(f"./scripts/{row['Script_filename']}", 'r') as script:
                lines = script.readlines()
                row['Script'] = "".join(lines).replace('"', '\"')
        with open(jsons_dir + f'/movie_{i}{with_script}.json', 'w') as json_file:
            json.dump(row, json_file, indent=4)


# Example usage
csv_to_json('imdb_top_1000.csv', './movie_data')
