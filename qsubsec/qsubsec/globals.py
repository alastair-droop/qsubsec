#!/usr/bin/env python3

from copy import copy

class X(object):
    def __init__(self):
        self.values = []

def run_f0():
    global x
    x.values.append(1)
    
def run_f1():
    global x
    print('f1 run (x is {})'.format(x))
    x.values.append(2)

x = X()
g = {'f0':run_f0, 'f1':run_f1}
code = 'f0()\nf1()\nf1()'

exec(code, g)
print(x.values)


