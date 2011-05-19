#!/usr/bin/env python
import re
import urllib
import urllib2
from pprint import pprint
import time
from datetime import date
from StringIO import StringIO
from os.path import expanduser
from xml.etree import ElementTree as etree

import html5lib
from html5lib import sanitizer
from shove import Shove


today = date(2000,1,1).today()
date_fmt = "%d/%m/%Y"
p = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder('etree', etree),
            #    tokenizer=sanitizer.HTMLSanitizer,
                namespaceHTMLElements=False)

link_sanca = "http://www2.ufscar.br/servicos/cardapio.php"
link_sorocaba = "http://www.sorocaba.ufscar.br/ufscar/index.php?pg_id=39"

def generate_description(almoco, janta):
    desc = StringIO()
    if almoco:
        desc.write(u'Almo\u00e7o: ')
        for key, value in almoco:
            desc.write(u'%s' % value)

    if janta:
        desc.write(u'Janta: ')
        for key, value in janta:
            desc.write(u'%s' % value)

    return desc.getvalue()

def generate_data_sanca():
        # open the web page
        page = urllib2.urlopen(link_sanca).read()
#        page = open("sanca.html").read()

        tree = p.parse(page)

        for table in tree.getiterator("table"):
            if table.get('class') == 'style3':
                days = table

        entries = []
        for weekday in days:
            header = weekday.getiterator('strong')

            menu_almoco = []
            menu_janta = []
            cardapio = weekday.getiterator('font')

            for item in cardapio[::2]:
                key = item[0].text
                # XXX etree parece nao suportar pegar o text inteiro...
                value = etree.tostring(item).split(':')[1].split('<')[0]
                menu_almoco.append((key, value))

            if len(header) > 1:
                for item in cardapio[1::2]:
                    key = item[0].text
                    # XXX etree parece nao suportar pegar o text inteiro...
                    value = etree.tostring(item).split(':')[1].split('<')[0]
                    menu_janta.append((key, value))

            day = {}
            day['title'] = header[0].text[:10]
            page_link = "http://www2.ufscar.br/servicos/cardapio.php"
            day["page_link"] = page_link
            day['guid'] = day["page_link"] + "#" + day['title']
            day["description"] = generate_description(menu_almoco,
                                                           menu_janta)
            daydate = [int(n) for n in day['title'].split('/')]
            daydate = date(daydate[2], daydate[1], daydate[0])
            day["pubDate"] = daydate
            entries.append(day)
        return reversed(entries)

def get_element_text(el):
    texts = []
    texts.append(el.text or "")
    for e in el.getiterator()[1:]:
        texts.append(e.text or "")
    return "".join(texts)

def generate_data_soro():
        # open the web page
        page = urllib2.urlopen(link_sorocaba).read()
#        page = open("soro.html").read()

        tree = p.parse(page)
        menu = {}
        for div in tree.getiterator('div'):
            if div.get('class') == 'noticia':
                for table in div.getiterator('table'):
                    titulo = get_element_text(table[0][0]).split('-')[1].strip()
                    dias = [el[0][0].text for el in table[0][1]]

                    datas = [get_element_text(el) for el in table[0][2]]

                    menus_norm = []
                    for td in table[0][3].getiterator('td'):
                        ps = td.findall('p')
                        tipos = [get_element_text(e) for e in ps[::3]]
                        pratos = [get_element_text(e) for e in ps[1::3]]
                        menus_norm.append(dict(zip(tipos, pratos)))

                    menus_veg = []
                    for td in table[0][5].getiterator('td'):
                        ps = td.findall('p')
                        tipos = ['Arroz']
                        if td.text != '\n':
                            pratos = [td.text[:-1]]
                            idx_t = 1
                            idx_p = 2
                        else:
                            pratos = [ps[0].text]
                            idx_t = 2
                            idx_p = 3

                        tipos += [e[0].text for e in ps[idx_t::3]]
                        pratos += [e.text for e in ps[idx_p::3]]
                        menus_veg.append(dict(zip(tipos, pratos)))

                    turn = dict(zip(datas, zip(menus_norm, menus_veg)))
                    import ipdb; ipdb.set_trace()
                    menu[titulo] = turn
        return menu

def save_data(shf, data):
    for key, value in data.items():
        print key
        shf[key] = data[key]

data_soro = generate_data_soro()
data_sanca = list(generate_data_sanca())

db = Shove("sqlite:///persist_soro.db")
save_data(db, data_soro)

db = Shove("sqlite:///persist_sanca.db")
save_data(db, data_sanca)
