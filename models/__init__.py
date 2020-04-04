# -*- coding: utf-8 -*-

import re
import json
import requests
from bs4 import BeautifulSoup
from config import *


URL = 'http://webdkp.wowcat.net/dkp/%s/%s/{page}?t=1' % (SERVER_NAME, GUILD_NAME)


class Player(object):

    def __init__(self, user_id, dkp, history_dkp, name, occupation):
        self.use_id = user_id
        self.dkp = dkp
        self.history_dkp = history_dkp
        self.name = name
        self.occupation = occupation

    def __repr__(self):
        return 'Play<name=%s>' % self.name

    @property
    def url(self):
        return 'http://webdkp.wowcat.net/dkp/%s/%s/Player/%s' % (SERVER_NAME, GUILD_NAME, self.name)


def get_url_data(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        print '请求出错, 重试'

    soup = BeautifulSoup(resp.content, 'html.parser')
    nodes = soup.find_all('script', type='text/javascript')
    data = ''
    for node in nodes:
        data = node.get_text()
        if isinstance(data, unicode):
            data = data.encode('utf8').strip()
        if data.startswith('table = new'):
            break
        else:
            data = ''
    return data


def get_players_from_url_data(data):
    players = []
    for line in data.split('\n'):
        line = line.strip()
        if line.startswith('table.Add'):
            matches = re.search(r'(\{.+\})', line)
            if not matches:
                continue
            play_info = json.loads(matches.groups()[0])
            user_id, dkp, history_dkp, name, occupation = \
                play_info.get('userid'), float(play_info.get('dkp')), float(play_info.get('lifetime')), play_info.get('player').encode('utf8'), play_info.get('playerclass')
            if not user_id and dkp and history_dkp and name and occupation:
                continue
            players.append(Player(user_id, dkp, history_dkp, name, occupation))
    return players


def get_players():
    url = URL.format(page=1)
    data = get_url_data(url)
    if not data:
        print '未抓取到第%s页数据' % 1
        return

    page, pages = 1, 1
    for line in data.split('\n'):
        line = line.strip()
        if line.startswith('table.SetPageData'):
            page, pages = map(int, re.findall('(\d+)', line))

    players = get_players_from_url_data(data)
    if pages > 1:
        for p in range(2, pages + 1):
            url = URL.format(page=p)
            data = get_url_data(url)
            if not data:
                print '未抓取到第%s页数据' % p
                return
            players.extend(get_players_from_url_data(data))

    return players
