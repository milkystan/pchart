#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/5 14:20
# @Author  : Stan
# @File    : chart_option.py

'''
xAxis:  MUST BE A LIST CONTAIN ONE DICT OBJECT
YAxis:  MUST BE A LIST CONTAIN ONE DICT OBJECT
series:  MUST BE A LIST CONTAIN ONE DICT OBJECT
ONLY SUPPORT: set_title, set_legend, set_x_axis, set_y_axis, set_series
'''

TO_BE_SET = 'TO_BE_SET'

StackOption = {
    'title': {
        'text': TO_BE_SET
    },
    'tooltip': {
        'trigger': 'axis'
    },
    'legend': {
        'data': []
    },
    'toolbox': {
        'feature': {
            'saveAsImage': {},
            'dataZoom': {},
            'restore': {},
        }
    },
    'grid': {
        'left': '3%',
        'right': '4%',
        'bottom': '3%',
        'containLabel': True
    },
    'xAxis': [
        {
            'type': 'category',
            'boundaryGap': False,
            'data': TO_BE_SET
        }
    ],
    'yAxis': [
        {
            'type': 'value'
        }
    ],
    'series': [
        {
            'name': TO_BE_SET,
            'type': 'line',
            'stack': 's',
            'label': {
                'normal': {
                    'show': True,
                }
            },
            'areaStyle': {'normal': {}},
            'data': TO_BE_SET
        }
    ]
};


PolylineOption = {
    'title': {
        'text': TO_BE_SET
    },
    'tooltip': {
        'trigger': 'axis'
    },
    'legend': {
        'data': []
    },
    'toolbox': {
        'feature': {
            'saveAsImage': {},
            'dataZoom': {},
            'restore': {},
        }
    },
    'grid': {
        'left': '3%',
        'right': '4%',
        'bottom': '3%',
        'containLabel': True
    },
    'xAxis': [
        {
            'type': 'category',
            'boundaryGap': False,
            'data': TO_BE_SET
        }
    ],
    'yAxis': [
        {
            'type': 'value'
        }
    ],
    'series': [
        {
            'name': TO_BE_SET,
            'type': 'line',
            'label': {
                'normal': {
                    'show': True,
                }
            },
            'data': TO_BE_SET
        }
    ]
};

