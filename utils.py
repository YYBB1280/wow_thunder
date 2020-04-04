# -*- coding: utf-8 -*-

from datetime import timedelta


def get_tuesday(dt):
    # 获取参数所在周的周二
    wd = dt.weekday()
    if wd == 0:
        return (dt + timedelta(days=1)).date()
    else:
        return (dt - timedelta(days=wd - 1)).date()
