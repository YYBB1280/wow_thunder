# -*- coding: utf-8 -*-

import re
import json
import requests
from bs4 import BeautifulSoup
from consts import *


TANK_PLAYERS = ['小豆兜', '朝花夕拾', '暗夜王者', '北理老蚊子']
URL = 'http://webdkp.wowcat.net/dkp/%E9%9B%B7%E9%9C%86%E4%B9%8B%E5%87%BB/%E9%95%B6%E9%87%91%E7%8E%AB%E7%91%B0/{page}?t=1'
FRESHMAN_RATIO = 0.8


class Player(object):

    def __init__(self, user_id, dkp, name, occupation):
        self.use_id = user_id
        self.dkp = dkp
        self.name = name
        self.occupation = occupation

    def __repr__(self):
        return 'Play<name=%s>' % self.name


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


def get_players(data):
    players = []
    for line in data.split('\n'):
        line = line.strip()
        if line.startswith('table.Add'):
            matches = re.search(r'(\{.+\})', line)
            if not matches:
                continue
            play_info = json.loads(matches.groups()[0])
            user_id, dkp, name, occupation = play_info.get('userid'), float(play_info.get('dkp')), play_info.get('player').encode('utf8'), play_info.get('playerclass')
            if not user_id and dkp and name and occupation:
                continue
            players.append(Player(user_id, dkp, name, occupation))
    return players


def go():
    url = URL.format(page=1)
    data = get_url_data(url)
    if not data:
        print '未抓取到数据'

    page, pages = 1, 1
    for line in data.split('\n'):
        line = line.strip()
        if line.startswith('table.SetPageData'):
            page, pages = map(int, re.findall('(\d+)', line))

    players = get_players(data)
    if pages > 1:
        for p in range(2, pages + 1):
            url = URL.format(page=p)
            data = get_url_data(url)
            players.extend(get_players(data))

    tank_dkps = []
    ad_dkps = []
    ap_dkps = []
    healer_dkps = []
    for p in players:
        if p.name in TANK_PLAYERS:
            tank_dkps.append(p.dkp)
        elif p.occupation in HEALER_OCCUPATIONS:
            healer_dkps.append(p.dkp)
        elif p.occupation in AD_OCCUPATIONS:
            ad_dkps.append(p.dkp)
        elif p.occupation in AP_OCCUPATIONS:
            ap_dkps.append(p.dkp)

    stat_data = {
        'tank_total': sum(tank_dkps),
        'tank_count': len(tank_dkps),
        'tank_avg': round(sum(tank_dkps)/len(tank_dkps)),
        'tank_freshman': round(sum(tank_dkps)/len(tank_dkps)*FRESHMAN_RATIO),
        'ad_total': sum(ad_dkps),
        'ad_count': len(ad_dkps),
        'ad_avg': round(sum(ad_dkps)/len(ad_dkps)),
        'ad_freshman': round(sum(ad_dkps)/len(ad_dkps)*FRESHMAN_RATIO),
        'ap_total': sum(ap_dkps),
        'ap_count': len(ap_dkps),
        'ap_avg': round(sum(ap_dkps)/len(ap_dkps)),
        'ap_freshman': round(sum(ap_dkps)/len(ap_dkps)*FRESHMAN_RATIO),
        'healer_total': sum(healer_dkps),
        'healer_count': len(healer_dkps),
        'healer_avg': round(sum(healer_dkps)/len(healer_dkps)),
        'healer_freshman': round(sum(healer_dkps)/len(healer_dkps)*FRESHMAN_RATIO),
    }

    info = '''各职责dkp信息如下:
    坦克组: dkp总和 - {tank_total}, 人数 - {tank_count}, 平均dkp - {tank_avg}, 新人补分 - {tank_freshman}
    物理组: dkp总和 - {ad_total}, 人数 - {ad_count}, 平均dkp - {ad_avg}, 新人补分 - {ad_freshman}
    法系组: dkp总和 - {ap_total}, 人数 - {ap_count}, 平均dkp - {ap_avg}, 新人补分 - {ap_freshman}
    治疗组: dkp总和 - {healer_total}, 人数 - {healer_count}, 平均dkp - {healer_avg}, 新人补分 - {healer_freshman}
    '''.format(**stat_data)

    print info


if __name__ == '__main__':
    go()
