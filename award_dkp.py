# -*- coding: utf-8 -*-

"""dkp新人及缺勤dkp扣分"""

import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import *
from models import get_players
from utils import get_tuesday


def get_player_data(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        print '请求出错, 重试'
        return

    soup = BeautifulSoup(resp.content, 'html.parser')
    nodes = soup.find_all('script', type='text/javascript')
    data = ''
    for node in nodes:
        data = node.get_text()
        if isinstance(data, unicode):
            data = data.encode('utf8').strip()
        if data.startswith('table = new PlayerHistoryTable'):
            break
        else:
            data = ''

    return data


def get_player_dt(player):
    # 获取第一次和最后一次参加活动的日期
    data = get_player_data(player.url)
    if not data:
        print '未抓取到数据'
        return

    page, pages = 1, 1
    for line in data.split('\n'):
        line = line.strip()
        if line.startswith('table.SetPageData'):
            page, pages = map(int, re.findall('(\d+)', line))

    first_dt = last_dt = None
    for line in data.split('\n'):
        line = line.strip()
        if line.startswith('table.Add'):
            matches = re.search(r'(\{.+\})', line)
            if not matches:
                continue
            dkp_info = json.loads(matches.groups()[0])
            info_name = dkp_info.get('name')
            if info_name and len(info_name) > 8 and info_name[:8].isdigit():
                dt_str = info_name[:8]
                _dt = datetime.strptime(dt_str, '%Y%m%d')
                if not last_dt:
                    last_dt = _dt
                first_dt = _dt

    if pages == 1:
        return first_dt, last_dt

    last_page_url = player.url + '/%s/date/desc' % pages
    data = get_player_data(last_page_url)
    if not data:
        print '未抓取到数据'
        return

    for line in data.split('\n'):
        line = line.strip()
        if line.startswith('table.Add'):
            matches = re.search(r'(\{.+\})', line)
            if not matches:
                continue
            dkp_info = json.loads(matches.groups()[0])
            info_name = dkp_info.get('name')
            if info_name and len(info_name) > 8 and info_name[:8].isdigit():
                dt_str = info_name[:8]
                _dt = datetime.strptime(dt_str, '%Y%m%d')
                first_dt = _dt

    return first_dt, last_dt


def go():
    now = datetime.now()
    this_tuesday = get_tuesday(now)
    # 活动的总周数
    weeks = (this_tuesday - get_tuesday(datetime.strptime(FIRST_DATE, '%Y-%m-%d'))).days / 7
    # 历史总dkp
    history_dkp = DKP_PER_WEEK * (weeks + DOUBLE_DKP_WEEKS) + EXTERNAL_DKP
    print history_dkp

    players = get_players()
    minus_info = []
    new_players = []
    for player in players:
        if player.name in EXCLUDE_PLAYERS or player.history_dkp > (history_dkp - DKP_PER_WEEK * 2):
            continue

        if 0 < player.history_dkp <= DKP_PER_WEEK:  # 新人
            first_dt, last_dt = get_player_dt(player)
            if get_tuesday(first_dt) == this_tuesday:
                new_players.append(player.name)
                continue

        if player.dkp > 0:
            first_dt, last_dt = get_player_dt(player)
            absence_weeks = (this_tuesday - get_tuesday(last_dt)).days / 7  # 缺勤周数
            if absence_weeks > 2:
                info = '%s，第%s次缺勤，扣除%s%%分' % (player.name, absence_weeks - 2, 10 * (absence_weeks - 2))
                minus_info.append(info)

    if new_players:
        print "====== 这个CD的新人如下 ======"
        for np in new_players:
            print np
    if minus_info:
        print "====== 缺勤需要的扣分情况如下 ======"
        for mi in minus_info:
            print mi


if __name__ == '__main__':
    go()
