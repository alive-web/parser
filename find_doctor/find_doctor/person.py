# -*- coding: utf-8 -*-
import re

from datetime import datetime

from find_doctor.items import Person


class CreateObject():
    def __init__(self, row, date, url):
        self.url = url
        self.date = datetime.strptime(date, '%Y-%m-%d')
        self.words = []
        for string in row:
            string = re.sub('\n|,|\?|!|>|Sammankallande', '', string)
            self.words += string.split()

    def get_fields(self):
        person = Person()
        useless = self.words[:]
        for word in self.words:
            if re.match(r"Planerings", word):
                i = self.words.index(word)
                development = "utvecklingsdirektör"
                if self.words[i+1] == "och" and self.words[i+2] == development.decode('utf-8'):
                    word = ' '.join((self.words[i], self.words[i+1], self.words[i+2]))
            if word.lower() == 'vice':
                i = self.words.index(word)
                word = ' '.join((word, self.words[i+1]))
            if word.lower() == 'bitr.':
                i = self.words.index(word)
                word = ' '.join((word, self.words[i+1]))
            if word.lower() == 'medicinsk' or word.lower() == 'medicinskt':
                i = self.words.index(word)
                if self.words[i+1].lower() == 'ansvarig':
                    word = ' '.join((word, self.words[i+1], self.words[i+2]))
                elif self.words[i+1].lower() == u'rådgivare':
                    word = ' '.join((word, self.words[i+1]))
            role = get_correct_role(word)
            if role and 'role' not in person:
                person['role'] = role
                for el in word.split():
                    useless.remove(el)
                continue
            title = get_correct_title(word)
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
            if len(useless[0]) == 2 and useless[0] != 'Bo':
                person['first_name'] = ' '.join((useless[0], useless[1])).encode('utf-8')
                person['last_name'] = useless[2].encode('utf-8')
                useless = useless[3:]
            else:
                person['first_name'] = useless[0].encode('utf-8')
                person['last_name'] = useless[1].encode('utf-8')
                useless = useless[2:]
        person['url'] = self.url
        person['workplace'] = ' '.join(useless).encode('utf-8')
        person['doc_updated'] = self.date
        person['download_date'] = datetime.now()
        return person


def get_correct_role(role):
    role = role.lower().encode('utf-8')
    roles = {
        'ordförande': 'ordf',
        'vice ordförande': 'vice ordf',
        'sekreterare': 'sekr',
        'informationsläkare': 'inf',
    }
    return roles.get(role, '')


def get_correct_title(title):
    title = title.lower().encode('utf-8')
    titles = {
        'planerings- och utvecklingsdirektör': 'planning and development',
        'diabetessköterska': 'diabetes Nurse',
        'kommunsköterska': 'municipality nurse',
        'farmaceut': 'pharmacist',
        'verksamhetschef': 'Operations',
        'bitr. avdelningsföreståndare': 'asst. department director',
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
        'övertandläkare': 'over dentists',
        'privatläkare': 'private doc'
    }
    return titles.get(title, '')