from bs4 import BeautifulSoup
from csv_worker import WorkWithFile
from datetime import datetime
import urllib2
import re


url = 'http://www.regiongavleborg.se/A-O/Vardgivarportalen/Lakemedel/Lakemedelskommitten/Organisation/Lakemedelskommittens-ledamoter/'
soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
all_tables = soup.findAll('table', {"class": "linjeradOrange"})
rows = []


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
        needed_el = 0
        for tr in tr_tags:
            if needed_el:
                full_name = tr.contents[needed_el].contents[0].split()
                row = split_full_name(full_name)
                row['doc_updated'] = get_date(soup)
                row['download_date'] = datetime.now()
                rows.append(row)
                continue
            for i, el in enumerate(tr.contents):
                if hasattr(el, "text") and el.text == "Namn":
                    needed_el = i
                    continue

convert_table_rows(all_tables)
WorkWithFile().write_rows(rows, url)
