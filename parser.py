# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from csv_worker import WorkWithFile
from datetime import datetime
import urllib2
import re


def parse_tables(html):
    all_tables = []
    names = html.findAll('th', text=re.compile('Namn'))
    for name in names:
        for parent in name.parents:
            if parent is not None and parent.name == "table":
                all_tables.append(parent)
    if all_tables:
        convert_table_rows(all_tables)


def get_correct_role(role):
    role = role.lower()
    roles = {
        'ordförande': 'ordf',
        'vice ordförande': 'vice ordf',
        'sekreterare': 'sekr',
        'informationsläkare': 'inf',
    }
    return roles.get(role, '')


def get_correct_title(title):
    title = title.lower()
    titles = {
        'distriktssköterska': 'district nurse',
        'kvalitetssamordnare': 'quality Coordinator',
        'medicinskt ansvarig sjuksköterska': 'Head nurse',
        'apotekare': 'pharmacist',
        'familjeläkare': 'family',
        'Överläkare': 'physician',
        'överläkare': 'physician',
        'tandläkare': 'dentist',
        'mas': 'MAS',
        'sjuksköterska': 'nurse',
        'medicinsk rådgivare': 'medical advisor',
        'dietist': 'dietitian'
    }
    return titles.get(title, '')


def split_full_name(full_name):
    result = []
    if len(full_name) == 2:
        result.append(full_name[0].encode('utf-8'))
        result.append(full_name[1].encode('utf-8'))
    if len(full_name) == 1:
        result.append(full_name[0].encode('utf-8'))
    if len(full_name) == 3:
        result.append((' '.join(full_name[:1])).encode('utf-8'))
        result.append(full_name[2].encode('utf-8'))
    return result


def get_date(html):
    text_and_date = html.find(text=re.compile('Uppdaterad'))
    updated = ''
    if text_and_date:
        updated = re.search('\d{1,4}-\d{1,2}-\d{1,2}', str(text_and_date)) or ''
        if updated:
            updated = updated.group(0)
            updated = datetime.strptime(updated, '%Y-%m-%d')
    return updated


def convert_table_rows(tables):
    rows = []
    for table in tables:
        tr_tags = table.find_all('tr')
        column_name = False
        column_role = False
        column_title = False
        column_workplace = False
        for tr in tr_tags:
            person = {}
            if column_name:
                full_name = tr.contents[column_name].contents[0].split()
                full_name = split_full_name(full_name)
                person['first_name'] = full_name[0]
                person['last_name'] = full_name[1]
                if len(tr.contents[column_name].contents) > 3:
                    for el in tr.contents[column_name].contents:
                        if hasattr(el, "text") and el.text:
                            person['title'] = get_correct_title(re.sub(',\xc2\xa0', '', el.text.encode('utf-8')))
                            break
                        else:
                            person['title'] = get_correct_title(re.sub(',\xc2\xa0', '', el.encode('utf-8')))
                            if person['title']:
                                break
            if column_role:
                role = tr.contents[column_role].text.encode('utf-8')
                role = re.sub('\n', '', role)
                person['role'] = get_correct_role(role)
            if column_workplace:
                workplace = tr.contents[column_workplace].text.encode('utf-8')
                workplace = re.sub('\n', '', workplace)
                person['workplace'] = workplace
            if column_title:
                title = ""
                title_list = tr.contents[column_title].contents
                if len(title_list) == 1 or len(title_list) == 2:
                    title = tr.contents[column_title].contents[0].string.encode('utf-8')
                if len(title_list) == 3:
                    title = tr.contents[column_title].contents[2].string.encode('utf-8')
                person['title'] = get_correct_title(title)
            if not column_name and not column_role and not column_title and not column_workplace:
                for i, el in enumerate(tr.contents):
                    if hasattr(el, "text"):
                        if el.text == "Namn":
                            column_name = i
                        if el.text == "Funktion":
                            column_role = i
                        if el.text == "Titel":
                            column_title = i
                        if re.search('Arbetsplats', el.text):
                            column_workplace = i
            else:
                person['doc_updated'] = get_date(soup)
                person['download_date'] = datetime.now()
                person['url'] = url
                rows.append(person)
    if rows:
        WorkWithFile().write_rows(rows)

if __name__ == "__main__":
    url = 'http://www.regiongavleborg.se/A-O/Vardgivarportalen/Lakemedel/Lakemedelskommitten/Organisation/Lakemedelskommittens-ledamoter/'
    soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
    parse_tables(soup)