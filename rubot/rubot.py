#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
from datetime import date, timedelta
from os.path import expanduser
from random import choice

from jabberbot import JabberBot

today = date(2000,1,1).today()

class RUJabberBot(JabberBot):
    def bot_menu(self, mess, args):
        """Retorna o cardapio de hoje, ou o ultimo disponibilizado"""

        data = []
        for item in reversed(sorted(self.history)):
            day = date(int(item[:4]), int(item[5:7]), int(item[8:10]))
            delta = today - day
            if delta >= timedelta(0) and delta < timedelta(7):
                data.append(item + ':\n')
                for name, meal in self.history[item]:
                    data += name.decode('latin-1') + ": " + meal + '\n'
                break

        return u''.join(data)

    def connect_cb(self):
        quotes = open('quote_list.txt', 'r')
        self.quote_list = []
        for quote in quotes.readlines():
            self.quote_list.append(quote[:-1].decode('ISO-8859-1'))
        quotes.close()

        self.history = shelve.open(expanduser('~/projects/rurss/cardapio.ru'), 'r')

    def disconnect_cb(self):
        self.history.close()

    def unknown_command(self, mess, cmd, args):
        if cmd == "5:20":
            # creditos para o Baba, foi ideia dele este easter egg
            return "IMPULSO! SETINHA PRA CIMA!"
        elif cmd == 'reload':
            # recarrega o shelve
            self.history.close()
            self.history = shelve.open(expanduser('~/projects/rurss/cardapio.ru'), 'r')
            return 'cardapio recarregado'
        else:
            return choice(self.quote_list) + '\n...\n\n' + self.help_callback(mess, args)

username = 'card.ru.ufscar@gmail.com'
password = raw_input('senha: ')
bot = RUJabberBot(username, password)
bot.serve_forever(connect_callback=bot.connect_cb, disconnect_callback=bot.disconnect_cb)
