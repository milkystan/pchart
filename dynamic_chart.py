#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/5 14:19
# @Author  : Stan
# @File    : dynamic_chart.py

from static_chart import Chart, TranArray
from chart_option import *
from HtGenerator import counter
from JsGenerator import dump
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
from collections import defaultdict

'''
please set IP and PORT, do not change other attributes!
'''

IP, PORT = 'localhost', 8000
WS = 'ws://{ip}:{port}'.format(ip=IP, port=PORT)


class ChartSocket(WebSocket):
    def handleMessage(self):
        if self.data.startswith(DynamicChart.PACT):
            DynamicChart.ws_pool[self.data[len(DynamicChart.PACT):]].append(self)

    def handleConnected(self):
        pass

    def handleClose(self):
        pass


class DynamicChart(Chart):
    WS_NAME = 'webSocket'
    PACT = '%chart%'
    _ws_server_thread = None
    ws_pool = defaultdict(list)

    def send_option(self):
        '''
        it will send the entire option, may acquire large bandwidth
        '''
        if self.name in self.ws_pool and self.opt:
            opt_str = dump({'type': 'opt', 'data': self.opt}).decode('utf-8')
            remove = []
            for sok in self.ws_pool[self.name]:
                if sok.closed:
                    remove.append(sok)
                else:
                    sok.sendMessage(opt_str)
            for sok in remove:
                self.ws_pool[self.name].remove(sok)

    def send_data(self):
        '''
        Data transmission optimization,
        it will only send the data in TranArray object
        instead of sending the whole option
        '''
        data = {}
        for d in self._arrays:
            data[d.name] = d.get_data()
        if self.name in self.ws_pool:
            data_str = dump({'type': 'data', 'data': data}).decode('utf-8')
            remove = []
            for sok in self.ws_pool[self.name]:
                if sok.closed:
                    remove.append(sok)
                else:
                    sok.sendMessage(data_str)
            for sok in remove:
                self.ws_pool[self.name].remove(sok)

    def __init__(self, *args, **kwargs):
        super(DynamicChart, self).__init__(*args, **kwargs)
        c = str(counter.next())
        self.ws_name = self.WS_NAME + '_' + c
        self._start_ws_server()

    def _start_ws_server(self):
        if self._ws_server_thread is None or not self._ws_server_thread.isAlive():
            server = SimpleWebSocketServer(IP, PORT, ChartSocket)
            self._ws_server_thread = Thread(target=server.serveforever)
            self._ws_server_thread.start()

    @property
    def build(self):
        js, div = self._build_common()
        # JS: define array operation
        array_op = js.function(js.arr, js.to_add, js.len)
        with array_op.block() as bk:
            bk.arr = bk.arr.concat(bk.to_add)
            _if = bk.If(bk.len == -1)
            bk.LVALUE = _if
            _elif = bk.Elif(bk.arr.length > bk.len)
            with _elif.block() as eb:
                eb.arr = eb.arr.splice(eb.arr.length - eb.len)
            bk.LVALUE = _elif
            bk.LVALUE = bk.Return(bk.arr)
        js.array_op = array_op

        # JS: WebSocket begin
        js[self.ws_name] = js.new(js.WebSocket(WS))
        on_message = js.function(js.evt)
        with on_message.block() as bk:
            bk.data = bk.JSON.parse(bk.evt.data)
            _if = bk.If(bk.data.type == 'opt')
            with _if.block() as ifk:
                ifk.LVALUE = ifk[self.name].setOption(ifk.data.data)
            bk.LVALUE = _if
            _else = bk.Else()
            with _else.block() as elk:
                for arr in self._arrays:
                    elk[arr.name] = elk.array_op(elk[arr.name],
                                                 elk.data.data[arr.name],
                                                 arr.length if arr.length else -1)
                elk[self.opt_name] = self.opt
                elk.LVALUE = elk[self.name].setOption(elk[self.opt_name])
            bk.LVALUE = _else
        js[self.ws_name].onmessage = on_message
        on_open = js.function(js.evt)
        with on_open.block() as bk:
            bk.LVALUE = bk[self.ws_name].send(self.PACT + self.name)
        js[self.ws_name].onopen = on_open
        # JS: WebSocket end
        return div.build()


def test_stack():
    import time
    chart = DynamicChart(opt=StackOption, width=600, height=300)
    chart.set_title(u'堆叠分区图')
    data = [1,2,3]
    x_data = ['s', 't', 'n']
    chart.add_series(legend=True, name='1', data=data)
    chart.add_series(legend=True, name='2', data=data)
    chart.add_x_axis(data=x_data)

    chart2 = DynamicChart(opt=StackOption, width=600, height=300)
    chart2.set_title(u'堆叠分区图2')
    chart2.add_series(legend=True, name='1', data=data)
    chart2.add_series(legend=True, name='2', data=data)
    chart2.add_x_axis(data=x_data)

    print chart.build
    print chart2.build
    while True:
        data.append(55)
        x_data.append('x')
        time.sleep(2)
        chart.send_option()
        chart2.send_option()


def test_tran_array():
    chart = DynamicChart(opt=StackOption, width=600, height=300)
    chart.set_title(u'堆叠分区图2')
    data = TranArray([1, 2, 3], length=20)
    x_data = ['s', 't', 'n']
    chart.add_series(legend=True, name='1', data=data)
    chart.add_series(legend=True, name='2', data=data)
    chart.add_x_axis(data=x_data)
    chart.send_data()
    print chart.build


if __name__ == '__main__':
    test_tran_array()

