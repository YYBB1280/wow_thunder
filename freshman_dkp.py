# -*- coding: utf-8 -*-

"""各职责dkp分数"""

from consts import *
from config import *
from models import get_players


def go():
    players = get_players()

    tank_dkps = []
    ad_dkps = []
    ap_dkps = []
    healer_dkps = []
    for p in players:
        if p.name in EXCLUDE_PLAYERS:
            continue
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
