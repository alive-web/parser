import csv
from datetime import datetime


class WorkWithFile():
    def __init__(self):
        pass

    def write_rows(self, rows, doc_updated):
        with open('names.csv', 'w') as csvfile:
            fieldnames = ['first_name', 'last_name', 'doc_updated', 'download_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in rows:
                row['doc_updated'] = doc_updated
                row['download_date'] = datetime.now()
                writer.writerow(row)