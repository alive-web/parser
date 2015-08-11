# -*- coding: utf-8 -*-
import os
import csv


class FindDoctorPipeline(object):
    def __init__(self):
        mod = 'a' if os.path.exists("persons.csv") else 'w'
        fields = ['first_name', 'last_name', 'role', 'title', 'workplace', 'doc_updated', 'download_date', 'url',
                  'email']
        self.csv_file = open('persons.csv', mod)
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fields)
        if mod == 'w':
            self.writer.writeheader()

    def process_item(self, item, spider):
        if 'role' in item or 'title' in item:
            self.writer.writerow(item)
            return item

    def __del__(self):
        self.csv_file.close()