#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date

from shove import Shove
from twitter import Twitter

today = date(2000,1,1).today()

def fix_description(string):
    tmp = string.split(u"&lt;br&gt;")[1:-2]
    return u"\n".join(tmp).replace(u"&lt;strong&gt;", "").replace(u"&lt;/strong&gt;", "")

twitter = Twitter("card.ru.ufscar@gmail.com", "****")

db = Shove("sqlite:////home/enc2004/luizcarlos/data/feeds/ru/persist.db")
for key in db:
    if db[key]['pubDate'] == today:
        almoco, janta = db[key]['description'].split('Janta')

        almoco = fix_description(almoco)
        janta = fix_description(janta)

        twitter.statuses.update(status=(u"%s: %s" % (u"Janta", janta)).encode('utf-8'))
        twitter.statuses.update(status=(u"%s: %s" % (u"Almo\u00e7o", almoco)).encode('utf-8'))
        print 'adicionou ', str(today)

print 'rodou sem problemas'
#print twitter.statuses.user_timeline()#since=today.)
