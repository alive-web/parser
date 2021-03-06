import csv
import os

FIELDS = ['first_name', 'last_name', 'role', 'title', 'workplace', 'doc_updated', 'download_date', 'url']


class WorkWithFile():
    def __init__(self):
        pass

    def write_rows(self, rows):
        mod = 'w'
        if os.path.exists("names.csv"):
            mod = 'a'
        with open('names.csv', mod) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
            if mod == "w":
                writer.writeheader()
            writer.writerows(rows)