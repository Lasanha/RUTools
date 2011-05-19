#!/usr/bin/env python
import re
import urllib
from pprint import pprint
import time
from datetime import date
from StringIO import StringIO
from os.path import expanduser

# HACK to set the PATH, apparently cron is running without env vars
#import site
#site.addsitedir('/home/enc2004/luizcarlos/usr/lib/python2.5/site-packages')

from BeautifulSoup import BeautifulSoup

from hand import BaseFeedGenerator

today = date(2000,1,1).today()
date_fmt = "%d/%m/%Y"

class RUFeed(BaseFeedGenerator):

    def __init__(self, config_file):
        BaseFeedGenerator.__init__(self, config_file)

    def generate_description(self, almoco, janta):
        desc = StringIO()
        if almoco:
            desc.write(u'&lt;strong&gt; Almo\u00e7o &lt;/strong&gt;&lt;br&gt;')
            for key, value in almoco:
                desc.write(u'%s: %s&lt;br&gt;' % (key, value))

        if janta:
            desc.write(u'&lt;br&gt;&lt;strong&gt; Janta &lt;/strong&gt;&lt;br&gt;')
            for key, value in janta:
                desc.write(u'%s: %s&lt;br&gt;' % (key, value))

        return desc.getvalue()

    def generate_data(self):
        # open the web page
        proxies = {'http': 'http://proxy.comp.ufscar.br:3128'}
        f = urllib.urlopen("http://www2.ufscar.br/servicos/cardapio.php", proxies=proxies)

        # read it with beautiful soup
        page = BeautifulSoup(f.read(), fromEncoding='iso-8859-1')

        # some black magic to get the right parts of the file
        anchor = page.find('strong')
        root = anchor.findParent().findParent().findParent().findParent()
        days = root.findAll("table")[:-2]

        entries = []
        for weekday in days:
            header = weekday.contents[0].findAll('strong')

            menu_almoco = []
            menu_janta = []
            cardapio = weekday.findAll('font')

            for item in cardapio[::2]:
                key = item.contents[0].contents[0]
                menu_almoco.append((key, item.contents[1][2:]))

            if len(header) > 1:
                for item in cardapio[1::2]:
                    key = item.contents[0].contents[0]
                    menu_janta.append((key, item.contents[1][2:]))

            day = {}
            day['title'] = header[0].contents[0][:10]
            page_link = "http://www2.ufscar.br/servicos/cardapio.php"
            day["page_link"] = page_link
            day['guid'] = day["page_link"] + "#" + day['title']
            data = urllib.urlopen(page_link, proxies=proxies)
            day["description"] = self.generate_description(menu_almoco,
                                                           menu_janta)
            daydate = [int(n) for n in day['title'].split('/')]
            daydate = date(daydate[2], daydate[1], daydate[0])
            day["pubDate"] = daydate
            data.close()
            entries.append(day)
        return reversed(entries)

if __name__ == "__main__":
    rf = RUFeed(expanduser("~/projects/rurss/config.ini"))
    rf.process()
    print str(today) + ": rodou sem problemas"
