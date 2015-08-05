# -*- coding: utf-8 -*-
import re
import urllib2
from datetime import datetime

from bs4 import BeautifulSoup

from csv_worker import WorkWithFile


def create_obj(all_words):
    person = {}
    useless = []
    useless += all_words
    for word in all_words:
        if word.lower() == 'vice':
            i = all_words.index(word)
            word = ' '.join((word, all_words[i+1]))
        if word.lower() == 'medicinsk' or word.lower() == 'medicinskt':
            i = all_words.index(word)
            if all_words[i+1].lower() == 'ansvarig':
                word = ' '.join((word, all_words[i+1], all_words[i+2]))
            elif all_words[i+1].lower() == u'rådgivare':
                word = ' '.join((word, all_words[i+1]))
        role = get_correct_role(word.encode('utf-8'))
        if role and 'role' not in person:
            person['role'] = role
            for el in word.split():
                useless.remove(el)
            continue
        title = get_correct_title(word.encode('utf-8'))
        if title and 'title' not in person:
            person['title'] = title
            for el in word.split():
                useless.remove(el)
            continue
        if re.match(r"^[a-zA-Z0-9._]+\@[a-zA-Z0-9._]+\.[a-zA-Z]{2,}$", word):
            person['email'] = word
            useless.remove(word)
            continue
    if len(useless) >= 2:
        if len(useless[0]) == 2:
            person['first_name'] = ' '.join((useless[0], useless[1])).encode('utf-8')
            person['last_name'] = useless[2].encode('utf-8')
            useless = useless[3:]
        else:
            person['first_name'] = useless[0].encode('utf-8')
            person['last_name'] = useless[1].encode('utf-8')
            useless = useless[2:]
    person['url'] = url
    person['workplace'] = ' '.join(useless).encode('utf-8')
    person['doc_updated'] = get_date(soup)
    person['download_date'] = datetime.now()
    return person


def get_text(html):
    roles = html.findAll(text=re.compile('l.{1}kare|mas|apotekare|medicinsk|sk.{1}terska|'
                                         'samordnare|dietist|barnmorska|bakteriolog', re.I))
    previous_parent = ''
    all_words = []
    for role in roles:
        parent = role.find_parent(['tr', 'li'])
        if parent and parent != previous_parent:
            words = []
            for string in parent.stripped_strings:
                free = re.compile("Vakant", re.I)
                if re.match(free, string):
                    words = []
                    break
                string = re.sub('\n|,|\?|!|>|Sammankallande', '', string)
                words += string.split()
            if words:
                all_words.append(words)
        previous_parent = parent
    return all_words


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
        'specialistläkare': 'specialist doctors',
        'st-läkare': 'resident physician',
        'distriktssköterska': 'district nurse',
        'kvalitetssamordnare': 'quality coordinator',
        'medicinskt ansvarig sjuksköterska': 'Head nurse',
        'apotekare': 'pharmacist',
        'familjeläkare': 'family',
        'Överläkare': 'physician',
        'överläkare': 'physician',
        'tandläkare': 'dentist',
        'mas': 'MAS',
        'sjuksköterska': 'nurse',
        'medicinsk rådgivare': 'medical advisor',
        'dietist': 'dietitian',
        'barnmorska': 'midwife',
        'bakteriolog': 'bacteriological',
        'chefläkare': 'head doctor',
        'Övertandläkare': 'over dentists',
        'privatläkare': 'private doc'
    }
    return titles.get(title, '')


def get_date(html):
    text_and_date = html.find(text=re.compile('Uppdaterad', re.I))
    updated = ''
    if text_and_date:
        updated = re.search('\d{1,4}-\d{1,2}-\d{1,2}', str(text_and_date)) or ''
        if updated:
            updated = updated.group(0)
            updated = datetime.strptime(updated, '%Y-%m-%d')
    return updated


def start(html):
        needed_text = get_text(html)
        persons = []
        for words in needed_text:
            person = create_obj(words)
            persons.append(person)
        WorkWithFile().write_rows(persons)

if __name__ == "__main__":
    url = 'http://www.regiongavleborg.se/A-O/Vardgivarportalen/Lakemedel/Lakemedelskommitten/Organisation/Lakemedelskommittens-ledamoter/'
    soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
    start(soup)