#!/usr/bin/env python

class Option(object):
    def __init__(self, switch, argument=None, value=None):
        self.switch = switch
        self.argument = argument
        self.value = value
    def setSwitch(self, switch): self._switch = switch
    def setArgument(self, argument): self._argument = argument
    def setValue(self, value): self._value = value
    def getSwitch(self): return self._switch
    def getArgument(self): return self._argument
    def getFullSwitch(self):
        if self.argument == None: return self.switch
        return '{} {}'.format(self.switch, self.argument)
    def getValue(self): return self._value
    def __str__(self):
        output = '-{}'.format(self.switch)
        if self.argument != None: output = '{} {}'.format(output, self.argument)
        if self.value != None: output = '{}={}'.format(output, self.value)
        return output
    switch = property(getSwitch, setSwitch)
    fullswitch = property(getFullSwitch, None)
    argument = property(getArgument, setArgument)
    value = property(getValue, setValue)

class OptionList(object):
    def __init__(self):
        super().__init__()
        self.setOptions()
    def append(self, option):
        if not isinstance(option, Option): raise ValueError('invalid option type')
        self._options.append(option)
    def getOptions(self): return self._options
    def setOptions(self, options=[]):
        self._options = []
        for option in options: self.append(option)
    def __getitem__(self, key): return self.options[key]
    def __delitem__(self, key): del(self.options[key])
    def __iter__(self): return iter(self.options)
    options = property(getOptions, setOptions, "The Options contained in the OptionList")
