import csv
import os


class WorkWithFile():
    def __init__(self):
        pass

    def write_rows(self, rows, url):
        mod = 'w'
        if os.path.exists("names.csv"):
            mod = 'a'
        with open('names.csv', mod) as cs_vfile:
            fieldnames = ['first_name', 'last_name', 'doc_updated', 'download_date', 'role', url]
            writer = csv.DictWriter(cs_vfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)