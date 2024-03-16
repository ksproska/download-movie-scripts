import csv
import json


def csv_to_json(csv_file_path, json_file_path):
    # Read CSV file
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # Convert CSV data to list of dictionaries
        data = list(csv_reader)

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

    # Write JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


# Example usage
csv_to_json('imdb_top_1000.csv', 'imdb_top_1000.json')
