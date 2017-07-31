#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/9 18:07
# @Author  : Stan
# @File    : test_flask.py

from flask import Flask, render_template
from static_chart import Chart
from dynamic_chart import DynamicChart, TranArray
from chart_option import *

app = Flask(__name__)


def add_data(data, chart):
    import time
    import random
    while True:
        time.sleep(0.1)
        data.append_data(random.randint(0, 100))
        chart.send_data()


@app.route('/')
def hello_world():
    chart = Chart(opt=StackOption, width=600, height=300)
    chart.set_title(u'堆叠分区图')
    data = [1,2,3]
    chart.add_series(legend=True, name='1', data=data)
    chart.add_series(legend=True, name='2', data=data)
    chart.add_x_axis(data=['s', 't', 'n'])
    x_data = ['s', 't', 'a']
    chart2 = DynamicChart(opt=PolylineOption, width=600, height=300)
    chart2.set_title(u'堆叠分区图2')
    t_data = TranArray([5,6,7], length=10)
    chart2.add_series(legend=True, name='1', data=t_data)
    import threading
    t = threading.Thread(target=add_data, args=(t_data, chart2))
    t.start()
    return render_template('chart.html', chart=chart, chart2=chart2)


if __name__ == '__main__':
    app.run(port=8888, debug=True)