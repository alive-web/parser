# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from csv_worker import WorkWithFile
from datetime import datetime
import urllib2
import re


url = 'http://www.regiongavleborg.se/A-O/Vardgivarportalen/Lakemedel/Lakemedelskommitten/Organisation/Lakemedelskommittens-terapigrupper/'
soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
rows = []


def parse_tables(html):
    all_tables = []
    names = html.findAll('th', text=re.compile('Namn'))
    for name in names:
        for parent in name.parents:
            if parent is not None and parent.name == "table":
                all_tables.append(parent)
    if all_tables:
        convert_table_rows(all_tables)


# for string in soup.stripped_strings:
#     print(repr(string))


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


def get_correct_title(title):
    correct_title = ''
    titles = {
        'Distriktssköterska': 'district nurse',
        'Kvalitetssamordnare': 'quality Coordinator',
        'Medicinskt ansvarig sjuksköterska': 'Head nurse',
        'Apotekare': 'pharmacist',
        'Familjeläkare': 'family',
        'Överläkare': 'physician',
        'Tandläkare': 'dentist',
        'MAS': 'MAS',
        'Sjuksköterska': 'nurse',
        'Medicinsk rådgivare': 'medical advisor',
        'Dietist': 'dietitian'
    }
    if titles.has_key(title):
        correct_title = titles[title]
    return correct_title


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
        column_title = False
        for tr in tr_tags:
            row = {}
            if column_name:
                full_name = tr.contents[column_name].contents[0].split()
                row = split_full_name(full_name)
            if column_role:
                role = tr.contents[column_role].text.encode('utf-8')
                role = re.sub('\n', '', role)
                row["role"] = get_correct_role(role)
            if column_title:
                title = ""
                title_list = tr.contents[column_title].contents
                if len(title_list) == 1 or len(title_list) == 2:
                    title = tr.contents[column_title].contents[0].string.encode('utf-8')
                if len(title_list) == 3:
                    title = tr.contents[column_title].contents[2].string.encode('utf-8')
                row['title'] = get_correct_title(title)
            if not column_name and not column_role and not column_title:
                for i, el in enumerate(tr.contents):
                    if hasattr(el, "text"):
                        if el.text == "Namn":
                            column_name = i
                        if el.text == "Funktion":
                            column_role = i
                        if el.text == "Titel":
                            column_title = i
            else:
                row['doc_updated'] = get_date(soup)
                row['download_date'] = datetime.now()
                row['url'] = url
                rows.append(row)
    if rows:
        WorkWithFile().write_rows(rows)

parse_tables(soup)