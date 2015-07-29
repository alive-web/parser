# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from csv_worker import WorkWithFile
from datetime import datetime
import urllib2
import re


url = 'http://www.regiongavleborg.se/A-O/Vardgivarportalen/Lakemedel/Lakemedelskommitten/Organisation/Lakemedelskommittens-terapigrupper/'
soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
all_tables = soup.findAll('table', {"class": "linjeradOrange"})
rows = []


def get_correct_role(role):
    correct_role = 'unspecified'
    roles = {
        'Ordförande': 'ordf',
        'Vice ordförande': 'vice ordf',
        'Sekreterare': 'sekr',
        'Informationsläkare': 'inf',
        'ordförande': 'ordf',
        'vice ordförande': 'vice ordf',
        'sekreterare': 'sekr',
        'informationsläkare': 'inf',
    }
    if roles.has_key(role):
        correct_role = roles[role]
    return correct_role


def split_full_name(full_name):
    row = {}
    if len(full_name) == 2:
        row['first_name'] = full_name[0].encode('utf-8')
        row['last_name'] = full_name[1].encode('utf-8')
    if len(full_name) == 1:
        row['first_name'] = full_name[0].encode('utf-8')
    if len(full_name) == 3:
        row['first_name'] = full_name[0].encode('utf-8') + " " + full_name[1].encode('utf-8')
        row['last_name'] = full_name[2].encode('utf-8')
    return row


def get_date(html):
    text_and_date = html.find(text=re.compile('Uppdaterad'))
    updated = ""
    if text_and_date:
        updated = re.search('(\d{1,4}-\d{1,2}-\d{1,2})', str(text_and_date)) or ""
        if updated:
            updated = updated.group(0)
            updated = datetime.strptime(updated, "%Y-%m-%d")
    return updated


def convert_table_rows(tables):
    for table in tables:
        tr_tags = table.find_all("tr")
        column_name = False
        column_role = False
        for tr in tr_tags:
            row = {}
            if column_name:
                full_name = tr.contents[column_name].contents[0].split()
                row = split_full_name(full_name)
                row['doc_updated'] = get_date(soup)
                row['download_date'] = datetime.now()
            if column_role:
                role = tr.contents[column_role].text.encode('utf-8')
                role = re.sub('\n', '', role)
                row["role"] = get_correct_role(role)
            if not column_name and not column_role:
                for i, el in enumerate(tr.contents):
                    if hasattr(el, "text") and el.text == "Namn":
                        column_name = i
                    if hasattr(el, "text") and el.text == "Funktion":
                        column_role = i
            else:
                rows.append(row)


convert_table_rows(all_tables)
WorkWithFile().write_rows(rows, url)
