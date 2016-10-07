#!/usr/bin/python3 
#-*- coding:utf-8-*-

"""Train tickets query via command-line.

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets beijing shanghai 2016-08-25
"""

from docopt import docopt
from stations import  stations
import requests
import json
from prettytable import PrettyTable

class TrainCollection(object):
    # 显示车次、出发/到达站、 出发/到达时间、历时、一等坐、二等坐、软卧、硬卧、硬座
    header = 'train station time duration first second softsleep hardsleep hardsit'.split()

    def __init__(self, rows):
        self.rows = rows

    def _get_duration(self, row):
        """
        获取车次运行时间
        """
        duration = row.get('lishi').replace(':', 'h') + 'm'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for prow in self.rows:
            row = prow['queryLeftNewDTO']
            train_no = row.get('station_train_code')
            train = [
                # 车次
                train_no,
                # 出发、到达站
                '\n'.join([colored('green', row.get('from_station_name')),
                                colored('red', row.get('to_station_name'))]),
                # 出发、到达时间
                '\n'.join([colored('green', row.get('start_time')),
                                colored('red', row.get('arrive_time'))]),
                # 历时
                self._get_duration(row),
                # 一等坐
                row.get('zy_num'),
                # 二等坐
                row.get('ze_num'),
                # 软卧
                row.get('rw_num'),
                # 软坐
                row.get('yw_num'),
                # 硬坐
                row.get('yz_num')
            ]
            yield train

    def pretty_print(self):
        """
        数据已经获取到了，剩下的就是提取我们要的信息并将它显示出来。
        `prettytable`这个库可以让我们它像MySQL数据库那样格式化显示数据。
        """
        pt = PrettyTable()
        # 设置每一列的标题
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)

def colored(color, text):
    table = {
        'red': '\033[91m',
        'green': '\033[92m',
        # no color
        'nc': '\033[0m'
    }
    cv = table.get(color)
    nc = table.get('nc')
    return ''.join([cv, text, nc])

def cli():
    """command-line interface"""
    arguments = docopt(__doc__)
    from_station = stations.get(arguments['<from>'])
    to_station   = stations.get(arguments['<to>'])
    date         = arguments['<date>']

    # 构建url
    url = 'https://kyfw.12306.cn/otn/leftTicket/' \
          'queryT?leftTicketDTO.train_date={}&' \
          'leftTicketDTO.from_station={}&' \
          'leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(date, from_station, to_station)

    # 添加verify=False参数不验证证书
    r = requests.get(url, verify=False)
    rows = r.json()['data']
    trains = TrainCollection(rows)
    trains.pretty_print()
    #buffer = rows[:]['queryLeftNewDTO']
    #print(rows)


if __name__ == '__main__':
    cli()

