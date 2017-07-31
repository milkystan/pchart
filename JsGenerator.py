#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/5 14:20
# @Author  : Stan
# @File    : JsGenerator.py

'''
USE UNICODE !
'''

INDENT = 4


def dump(obj):
    '''implement dump instead of use json because the quote problem'''

    if obj is True:
        return 'true'
    if obj is False:
        return 'false'
    if obj is None:
        return 'null'
    if isinstance(obj, basestring):
        # return repr(obj)
        return '"' + obj + '"'

    if isinstance(obj, (list, tuple)):
        '''json does not have ()'''
        return '[' + ', '.join([dump(o) for o in obj]) + ']'

    if isinstance(obj, dict):
        return '{' + ', '.join([dump(k) + ':' + dump(v) for k, v in obj.items()]) + '}'

    return unicode(obj)


class JsGen(object):
    '''
    usage:
        js = JsGen()
        js.a = 3    --->  var a = 3;
        js.a.b = 3  --->  a.b = 3;
        js.a = [1, 2, js.b]   ---> a = [1,2,b]
        js.a = {1:[1,2]} ---> a = {1:[1,2]}
        js.a = js.b ---> a = b;
        js.a = js.foo(1, 'word', js.b) ---> var a = foo(1, "word", b); # kwargs is not supported
        js.LVALUE = js.a  ---> a;
        js.LVALUE = js.foo() ---> foo();
        js.build() # produce javascript
        version 1.1 : add function definition

        foo = js.function(js.a, js.b)
        with foo.block() as bk:
            bk.a = 3
            bk.b = bk.a
            bk.foo(1, 2, 3)
        js.foo = foo
        js.build()
        --->
        var foo = function(a, b){
            var a = 3;
            var b = a;
        };
        version 1.1 :
        ADD js[] support
            js['var1'] = 3 ---> var1 = 3
            js.a['var2'] = 3  ---> a.var2 = 3
            js.a = js.b['var3'] ---> a = b.var3

            var1 = 'tan'
            js[var1] = 3  ---> tan = 3

            * or other tricks like js['new C()']  ---> new C()

        ADD if, else, else if, but renamed to If, Else, Elif
        REMOVE ';' at the end of the line


        remove 'var' cause of namespace problem

        version 1.2 : add operator:+-*/

        version 1.3 : to add logical operator
        version 1.4 : to support if else
        ...
    '''
    LVALUE = 'LVALUE'  # default left value

    class KeywordClass(object):
        def __init__(self, keyword, outer, inner):
            self._keyword = keyword
            self._outer = outer
            self._inner = inner

        def __unicode__(self):
            return self._keyword + ' ' + unicode(self._inner)

    class BlockClass(object):
        def __init__(self, keyword, outer, v):
            self._keyword = keyword
            self._outer = outer
            self._var = v
            self._jsGen = None

        def block(self):
            self._jsGen = JsGen(self._outer.indent + INDENT)
            return self._jsGen

        def __unicode__(self):
            if self._var:
                ret = self._keyword + ' (' + unicode(self._var) + '){\n'
            else:
                ret = self._keyword + '{\n'
            if self._jsGen:
                ret += self._jsGen.build()
            ret += self._outer.indent * ' ' + '}'
            return ret

    class DefClass(object):

        def __init__(self, outer, *args):
            self._outer = outer
            self._args = args
            self._jsGen = None

        def block(self):
            self._jsGen = JsGen(self._outer.indent + INDENT)
            return self._jsGen

        def __unicode__(self):
            ret = 'function(' + ', '.join([dump(i) for i in self._args]) + '){\n'
            if self._jsGen:
                ret += self._jsGen.build()
            ret += self._outer.indent * ' ' + '}'
            return ret

    class VarClass(object):

        def __init__(self, outer, v):
            self._setattr('_outer', outer)
            self._setattr('_var', v)
            self._setattr('_forbids', self.__class__.__dict__.keys() + self.__dict__.keys())
            self._forbids.append('_forbids')

        @staticmethod
        def _other(other):
            if isinstance(other, basestring):
                return '"' + other + '"'
            return unicode(other)

        def __eq__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') == (' + other + ')')

        def __gt__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') > (' + other + ')')

        def __lt__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') < (' + other + ')')

        def __le__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') <= (' + other + ')')

        def __ge__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') >= (' + other + ')')

        def __add__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') + (' + other + ')')

        def __sub__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') - (' + other + ')')

        def __mul__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') * (' + other + ')')

        def __div__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') / (' + other + ')')

        def __mod__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') % (' + other + ')')

        def __and__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') && (' + other + ')')

        def __or__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') || (' + other + ')')

        def __xor__(self, other):
            other = self._other(other)
            return JsGen.VarClass(self._outer, '(' + self._var + ') ^ (' + other + ')')

        def __pow__(self, power, modulo=None):
            return JsGen.VarClass(self._outer, '(' + self._var + ' ** ' + unicode(power) + ')')

        def __pos__(self):
            return self

        def __neg__(self):
            return JsGen.VarClass(self._outer, '(-' + self._var + ')')

        def __call__(self, *args):
            func_args = ', '.join([dump(i) for i in args])
            return JsGen.VarClass(self._outer, self._var + '(' + func_args + ')')

        def __getattr__(self, item):
            return JsGen.VarClass(self._outer, self._var + '.' + item)

        def __setattr__(self, key, value):
            if key in self._forbids:
                raise KeyError('Shadows built-in name "%s"!' % key)
            self._outer.add_to_process(JsGen.VarClass(self._outer, self._var + '.' + key), value)

        def _setattr(self, key, value):
            super(JsGen.VarClass, self).__setattr__(key, value)

        def __getitem__(self, item):
            return JsGen.VarClass(self._outer, self._var + '.' + item)

        def __setitem__(self, key, value):
            self._outer.add_to_process(JsGen.VarClass(self._outer, self._var + '.' + key), value)

        def __unicode__(self):
            return self._var

    def __init__(self, indent=0):
        self._setattr('indent', indent)
        self._setattr('_process', [])
        self._setattr('_forbids', self.__class__.__dict__.keys() + self.__dict__.keys())
        self._forbids.append('_forbids')
        self._forbids.remove(self.LVALUE)

    def __setattr__(self, key, value):
        if key in self._forbids:
            raise KeyError('Shadows built-in name "%s"!' % key)
        if key is self.LVALUE:
            self.add_to_process(key, value)
        else:
            self.add_to_process(JsGen.VarClass(None, key), value)

    def __getattr__(self, item):
        return self.VarClass(self, item)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return self.VarClass(self, item)

    def _setattr(self, key, value):
        super(JsGen, self).__setattr__(key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_to_process(self, key, value):
        self._process.append((key, value))

    def function(self, *args):
        return self.DefClass(self, *args)

    def new(self, value):
        return self.KeywordClass('new', self, value)

    def Return(self, value):
        return self.KeywordClass('return', self, value)

    def If(self, value):
        return self.BlockClass('if', self, value)

    def Else(self):
        return self.BlockClass('else', self, None)

    def Elif(self, value):
        return self.BlockClass('else if', self, value)

    def build(self):
        js = ''
        space = ' ' * self.indent
        for p in self._process:
            line = ''
            if p[0] is not self.LVALUE:
                assert isinstance(p[0], JsGen.VarClass)
                line += dump(p[0]) + ' = '
            line += dump(p[1]) + '\n'
            line = space + line
            js += line

        return js


def test_assign():
    js = JsGen()
    js['stan'] = 'ff'
    js.a = 'fd'
    js.a = [1, 2, js.cc]
    js.a = {'a': js.aa}
    js.b = 4
    js.a = js.b
    js.a.b = 3
    js.a = None
    js.a = True
    js.a.b = js.c.d
    js.a.b = js.new(js.C(1, 2))
    js.LVALUE = js.a.b['c']
    js.a.b['cc'] = js.b
    print js.build()


def test_func():
    js = JsGen()
    js.a = 3
    js.b = js.c("word")
    js.LVALUE = js.goo(js.a, 3, 5)
    js.LVALUE = js.goo(js.foo(1, 23))
    js.LVALUE = js.goo(js.foo(js.a))
    js.aa = js.goo(1, 2).a.boo(3, 4)
    print js.build()


def test_def():
    js = JsGen()
    foo = js.function(js.a, js.b)
    with foo.block() as bk:
        bk.a = 3
        bk.b = bk.a
        bk.LVALUE = bk.foo(1, 2, 3, {'1':u'中'})
        bk.aa = {'1': {'2': {'3': u'士大夫'}}}
        bk.LVALUE = bk.Return(bk.aaa)
    js.foo = foo
    js.goo = js.function(js.a, js.b)
    print js.build()


def test_if():
    pass


def test_operation():
    js = JsGen()
    js.a = (js.b + js.c) * (-js.d)
    js.b = -js.foo(1, 2, 4)
    js.a = js.a ** js.b
    js.a = js.a ^ js.b
    js.a = js.a & js.b
    js.a = js.a | js.b
    print js.build()


def test_echart():
    js = JsGen()
    js.myChart = js.echarts.init(js.document.getElementByid('main'))
    js.option = {
        'title': {
            'text': 'Echarts'
        },
        'tooltip': {},
        'legend': {
            'data': [u'销量']
        },
        'xAxis': {
            'data': [u"衬衫", u"羊毛衫", u"雪纺衫", u"裤子", u"高跟鞋", u"袜子"]
        },
        'yAxis': {},
        'series': [{
            'name': u'销量',
            'type': 'bar',
            'data': [5, 20, 36, 10, 10, 20]
        }]

    }
    js.LVALUE = js.myChart.setOption(js.option)
    print js.build()


def test_dump():
    js = JsGen()
    a = [1, 2, 3, '4', js.a]
    b = (js.a, js.b, True, False, None)
    c = {1: [1, 2, 3], '2': {3:[4,5,6]}}
    print dump(c)


def test_if():
    js = JsGen()
    i_f = js.If(js.a)
    with i_f.block() as bk:
        iif = bk.If(bk.aa == '3')
        with iif.block() as ib:
            ib.iia = 3
        bk.LVALUE = iif

    e_l = js.Else()
    with e_l.block() as bk:
        bk.b = 2

    js.LVALUE = i_f
    js.LVALUE = e_l
    print js.build()

if __name__ == '__main__':
    test_assign()
    test_func()
    test_echart()
    test_operation()
    test_if()
    test_def()
