#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/5 14:19
# @Author  : Stan
# @File    : static_chart.py

from chart_option import *
import copy
import warnings
from HtGenerator import Element, ScriptElement, counter
from JsGenerator import JsGen


class TranArray(object):
    ARRAY_NAME = 'tran_array'

    def __init__(self, init_data, length=None):
        self.length = length
        self.init_data = list(init_data)
        self._data = []
        self.name = self.ARRAY_NAME + '_' + str(next(counter))

        if length and len(self.init_data) > length:
            self.init_data = self.init_data[len(self.init_data)-length:]

    def append_data(self, data):
        '''
        :param data: [1, 2] or (1, 2) or 1
        '''
        if isinstance(data, (list, tuple)):
            self._data.extend(data)
        else:
            self._data.append(data)

    def get_data(self):
        data = self._data
        self._data = []
        return data


class Chart(object):
    JS_URL = 'http://echarts.baidu.com/dist/echarts.common.min.js'
    CHART_NAME = 'myChart'
    OPT_NAME = 'myOpt'
    OPT_DUMP_NAME = OPT_NAME + '_dump'

    def __init__(self, width, height, opt):
        self.width = width
        self.height = height
        self.opt = copy.deepcopy(opt)
        self._opt = opt  # original opt
        self._x = 1
        self._y = 1
        self._s = 1
        self._js = JsGen()
        self._arrays = set()
        c = str(counter.next())
        self.name = self.CHART_NAME + '_' + c
        self.opt_name = self.OPT_NAME + '_' + c

    def _check_option(self):
        if self.opt is None:
            raise Exception('no option available, please set one')

    def _add(self, pos, kwargs):
        '''
        :param pos: [str, str, ..., int]
        :param kwargs:
        :return:
        '''
        if len(pos) > 1 and kwargs:
            ori_opt = self._opt
            opt = self.opt
            for p in pos[:-1]:
                opt = opt[p]
                ori_opt = ori_opt[p]
            if len(opt) == pos[-1]:
                config = opt[-1]
                for k, v in kwargs.items():
                    if k not in config or config[k] is not TO_BE_SET:
                        warnings.warn('"%s" should not be set, otherwise may have unintended consequence' % k)
                    # todo judge is TranArray
                    if isinstance(v, TranArray):
                        self._arrays.add(v)
                        config[k] = self._js[v.name]
                    else:
                        config[k] = v
                return
            assert len(opt) + 1 == pos[-1]
            opt.append(copy.deepcopy(ori_opt[0]))
            self._add(pos, kwargs)

    def _set(self, pos, v):
        if pos and v:
            ori_opt = self._opt
            opt = self.opt
            # make sure the pos is reachable, or raise KeyError
            for p in pos[:-1]:
                opt = opt[p]
                ori_opt = ori_opt[p]
            if ori_opt[pos[-1]] is not TO_BE_SET:
                warnings.warn('"%s" should not be set, otherwise may have unintended consequence' % pos[-1])
            # now set the value
            opt[pos[-1]] = v

    def set_title(self, t):
        '''
        :param t: title unicode
        :return:
        '''
        self._check_option()
        try:
            self._set(['title', 'text'], t)
        except KeyError:
            raise Exception('can not set title in this option')

    def add_legend(self, name):
        '''
        name unicode
        '''
        self._check_option()
        if name:
            try:
                self.opt['legend']['data'].append(name)
            except KeyError:
                raise Exception('can not set legend in this option')

    def add_series(self, legend=False, **kwargs):
        '''
        unicode
        '''
        self._check_option()
        if kwargs:
            try:
                self._add(['series', self._s], kwargs)
                self._s += 1
                if legend and 'name' in kwargs:
                    self.add_legend(kwargs['name'])
            except KeyError:
                raise Exception('can not set series in this option')

    def add_x_axis(self, **kwargs):
        '''
        unicode
        '''
        self._check_option()
        if kwargs:
            try:
                self._add(['xAxis', self._x], kwargs)
                self._x += 1
            except KeyError:
                raise Exception('can not set xAxis in this option')

    def add_y_axis(self, **kwargs):
        '''
        unicode
        '''
        self._check_option()
        if kwargs:
            try:
                self._add(['yAxis', self._y], kwargs)
                self._y += 1
            except KeyError:
                raise Exception('can not set yAxis in this option')

    @property
    def build(self):
        _, div = self._build_common()
        return div.build()

    def _build_common(self):
        # build <div>
        div = Element(tag='div', width=self.width, height=self.height)
        # build <script>
        script = ScriptElement(tag_type=ScriptElement.TEXT)
        div.add_child(script)
        js = script.create_script()
        # js begin

        # predefined vars
        for v in self._arrays:
            js[v.name] = v.init_data

        js[self.name] = js.echarts.init(js.document.getElementById(div.id))
        js[self.opt_name] = self.opt
        js.LVALUE = js[self.name].setOption(js[self.opt_name])
        return js, div

    @property
    def prepare(self):
        '''load js and css'''
        script_link = ScriptElement(indent=4, tag_type=ScriptElement.LINK, url=self.JS_URL)
        return script_link.build()


def test_stack():
    chart = Chart(opt=StackOption, width=600, height=300)
    chart.set_title('堆叠分区图')
    data = [1,2,3]
    chart.add_series(legend=True, name='1', data=data)
    data.append(5)
    chart.add_series(legend=True, name='2', data=data)
    chart.add_x_axis(data=['s', 't', 'n'])
    print chart.build
    print chart.prepare


def test_stack2():
    chart = Chart(opt=StackOption, width=600, height=300)
    chart.set_title('堆叠分区图2')
    data = TranArray([1, 2, 3])
    chart.add_series(legend=True, name='1', data=data)
    chart.add_x_axis(data=['s', 't', 'n'])
    print chart.build

if __name__ == '__main__':
    test_stack2()