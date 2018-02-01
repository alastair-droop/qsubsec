#!/usr/bin/env python
from collections import OrderedDict
from string import Formatter
from itertools import product
from copy import deepcopy
from sys import getrecursionlimit
import json
from pyparsing import *
from urllib.request import urlopen
import logging as log

class TokenError(Exception):
    """
    The base class for token exceptions.
    
    :param tokens: The token name(s) referenced by the exception.
    """
    def __init__(self, tokens):
        self.tokens = tokens

class MissingTokenError(TokenError):
    """
    Raised when a required token is missing.
    """
    pass

class IteratedTokenError(TokenError):
    """
    Raised when a token is iterated and must not be.
    """
    pass

class CyclicTokenDependencyError(TokenError):
    """
    Raised when a token references (maybe indirectly) itself.
    """
    pass

class TokenFormatter(Formatter):
    """
    The TokenFormatter class extracts tokens from raw strings.
    """
    def __init__(self): super(TokenFormatter, self).__init__()
    def get_value(self, key, args, kwargs): return kwargs[key]
    def format(self, string, token_dict):
        """Formats a string with a dictionary of known tokens."""
        try: return super(TokenFormatter, self).format(string, None, **token_dict)
        except KeyError as error: raise MissingTokenError(', '.join(error.args))
    def extractTokens(self, input_string):
        """Extracts all the tokens referenced in a given input string."""
        tokens = set()
        for i in self.parse(input_string):
            if i[1] is not None: tokens.add(i[1])
        return tokens
    def elementList(self, string):
        """Converts a string into an ElementList."""
        output = ElementList()
        for i in self.parse(string):
            if len(i[0]) != 0: output.append(SRef(i[0]))
            if i[1] != None: output.append(TRef(i[1]))
        return(output)

class TElement(object):
    """This class encapsulates a single part of a token string."""
    def __init__(self, value): self.value = value
    def getValue(self): return self._value
    def setValue(self, value): self._value = str(value)
    def __str__(self): return self.value
    def __repr__(self): return '{}("{}")'.format(type(self).__name__, self.value)
    value = property(getValue, setValue, "return the element value")

class SRef(TElement):
    """This class encapsulates a simple Token string element"""
    def __init__(self, value): super().__init__(value)

class TRef(TElement):
    """This class encapsulates a simple Token reference element"""
    def __init__(self, value): super().__init__(value)
    def __str__(self): return '{{{}}}'.format(self.value)

class ElementList(object):
    """This class encapsulates an ordered list of elements"""
    def __init__(self):
        self.elements = []
    def append(self, element):
        if not isinstance(element, TElement): raise ValueError('invalid element type')
        self._elements.append(element)
    def getElements(self): return self._elements
    def setElements(self, elements=[]):
        self._elements = []
        for element in elements: self.append(element)
    def asJSON(self): return json.dumps(str(self))
    def __str__(self): return ''.join([str(x) for x in self.elements])
    def __repr__(self): return 'ElementList("{}")'.format(str(self))
    def __getitem__(self, name): return self.elements[name]
    def __delitem__(self, name): del(self.elements[name])
    def __iter__(self): return iter(self.elements)
    def getDependencies(self):
        dependencies = set()
        for element in self.elements:
            if isinstance(element, TRef): dependencies.add(element.value)
        return(dependencies)
    elements = property(getElements, setElements, "Return the element list")
    dependencies = property(getDependencies, None, "Return the token dependencies")
    json = property(asJSON, None, "JSON representation of the element list")

class Token(object):
    """This class encapsulates a token which can take one or more values"""
    @classmethod
    def fromFile(cls, name, filename, simple=False):
        # output = Token(name=name, values=[])
        values = []
        with open(filename, 'rt') as file_handle:
            for line in file_handle.readlines():
                line = line.strip()
                if ((len(line) == 0) or line.startswith('#')) and (simple is False): continue
                values.append(line)
        return Token(name=name, values=values)
    @classmethod
    def fromURL(cls, name, url, simple=False):
        values = []
        with urlopen(url) as url_handle:
            for line in url_handle.readlines():
                line = line.strip().decode('ASCII')
                if ((len(line) == 0) or line.startswith('#')) and (simple is False): continue
                values.append(line)
        return Token(name=name, values=values)
    def __init__(self, name, values=[]):
        super(Token, self).__init__()
        self.name = name
        self.values = values
    def getName(self): return self._name
    def getValues(self): return self._values
    def setName(self, name): self._name = str(name)
    def add(self, value, formatter=None):
        if formatter is None: formatter = TokenFormatter()
        self._values.append(formatter.elementList(value))
    def setValues(self, values):
        self._values = []
        for value in values: self.add(str(value))
    def getDependencies(self):
        dependencies = set()
        for value in self.values:
            dependencies |= value.dependencies
        return dependencies
    def __len__(self): return len(self.values)
    def isIterated(self): return len(self) > 1
    def isSingle(self): return len(self) == 1
    def isEmpty(self): return len(self) < 1
    def asJSON(self): return '{}: [{}]'.format(json.dumps(self.name), ', '.join([i.json for i in self.values]))
    def asTFF(self): return '"{}" = {}'.format(self.name, ', '.join([i.json for i in self.values]))
    def asText(self): return '{} ("{}")'.format(self.name, '", "'.join([str(i) for i in self.values]))
    def __iter__(self): return iter(self.values)
    def __getitem__(self, name): return self.values[name]
    def __delitem__(self, name): del(self.values[name])
    def __repr__(self):
        if len(self) > 0: value_str = ', '.join(['"{}"'.format(i) for i in self.values])
        else: value_str = ''
        return 'Token("{}", [{}])'.format(self.name, value_str)
    name = property(getName, setName, "The token name")
    values = property(getValues, setValues, "The values the token can take")
    iterated = property(isIterated, "Is this an iterated token?")
    single = property(isSingle, "Does the token have a single value?")
    empty = property(isEmpty, "Is this token empty?")
    json = property(asJSON, None, "JSON representation of the token")
    tff = property(asTFF, None, "TFF representation of the token")
    dependencies = property(getDependencies, None, "Return the token dependencies")

class TokenSet(object):
    """This class encapsulates a set of Tokens"""
    def __init__(self, formatter=None):
        super(TokenSet, self).__init__()
        if formatter == None: self.formatter = TokenFormatter()
        else: self.formatter = formatter
        self._tokens = OrderedDict()
    def getFormatter(self): return self._formatter
    def setFormatter(self, formatter): self._formatter = formatter
    def add(self, token):
        """Add a single Token to the TokenSet"""
        assert(isinstance(token, Token))
        if token.name in self.names:
            log.info('redefining existing token {} ("{}" -> "{}")'.format(token.name, '", "'.join([str(i) for i in self.tokens[token.name].values]), '", "'.join([str(i) for i in token.values])))
        self._tokens[token.name] = token
        log.debug('added token {}'.format(token.asText()))
    def extend(self, token_set):
        """Extent the TokenSet by adding all tokens from a second TokenSet"""
        for t in token_set.tokens:
            self.add(token_set[t])
    def getTokens(self): return self._tokens
    def setTokens(self, tokens):
        """Set the Tokens in the TokenSet"""
        self._tokens = OrderedDict()
        for token in tokens: self.add(token)
    def getNames(self): return list(self.tokens.keys())
    def getDependencies(self):
        """Get all dependencies (internal & external) referenced by tokens in the TokenSet"""
        output = set()
        for t in self.names: output |= self[t].dependencies
        return output
    def getInternalDependencies(self):
        """Get all internal dependencies (i.e. tokens that are also in this TokenSet) referenced by tokens in the TokenSet"""
        return self.getDependencies() & set(self.names)
    def getExternalDependencies(self):
        """Get all external dependencies (i.e. tokens that are not in this TokenSet) referenced by tokens in the TokenSet"""
        return self.getDependencies() - set(self.names)
    def getTokenDependencies(self, name):
        """Get the entire dependency set (recursively) for a single token"""
        output = set([name])
        while True:
            new_deps = set()
            for new_dep in (output & set(self.names)):
                new_deps |= self[new_dep].dependencies - output
            if len(new_deps) == 0: break
            output |= new_deps
        return output - set([name])
    def getIndependentTokens(self):
        """Get all tokens in the TokenSet that have no dependencies"""
        output = set()
        for t in self.names:
            if len(self[t].dependencies) == 0: output |= set([t])
        return(output)
    def getDependentTokens(self):
        """Get all tokens in the TokenSet that have dependencies"""
        return set(self.names) - self.getIndependentTokens()
    def getDependencyGraph(self):
        """Return a simple graph object representing the TokenSet dependencies"""
        output = {}
        for t in self.names:
            output[t] = self.tokens[t].dependencies
        return output
    def getCyclicDependencyGraph(self):
        """Prune leaf tokens from the TokenSet dependency graph, leaving the subgraph that contains cyclic dependencies.
        NB: external token dependencies are treated as leaves"""
        g = self.getDependencyGraph()
        all_nodes = set(self.names) | self.getDependencies()
        all_leaves = set()
        while True:
            leaves = set()
            # Identify leaves:
            for node in all_nodes:
                if (node not in g.keys()) or (len(g[node]) == 0):
                    leaves |= set([node])
                    for i in g.keys(): g[i] -= set([node])
            # Remove empty nodes:
            for leaf in leaves:
                if leaf in g.keys():
                    del g[leaf]
            all_leaves |= leaves
            all_nodes -= leaves
            # Determine if we need another round:
            if (len(leaves) == 0) or (len(g) == 0): return((g, all_leaves))
    def getSubgraph(self, name):
        """Return the minimal connected subgraph of the TokenSet based on the given token name"""
        output = TokenSet()
        deps = self.getTokenDependencies(name) | set([name])
        for t in self.names:
            if t in deps: output.add(self[t])
        return(output)
    def isComplete(self):
        """Check if the TokenSet is complete (i.e. has no external dependencies)"""
        return len(self.getExternalDependencies()) == 0
    def isCyclic(self):
        """Check if the TokenSet contains any cycles"""
        return len(self.getCyclicDependencyGraph()[0]) > 0
    def isIterated(self):
        """Check if the TokenSet contains any iterated tokens"""
        for t in self.names:
            if self[t].iterated is True: return True
        return False
    def singularize(self):
        """Generate a list of TokenSets each with only a single value per token"""
        # Check the TokenSet is valid:
        if self.complete is not True: raise MissingTokenError(self.getExternalDependencies())
        if self.cyclic is True: raise CyclicTokenDependencyError(ts.getCyclicDependencyGraph()[0].keys())
        # Expand the token set to produce a list of non-iterated TokenSets:
        names = self.names
        values = [self[i].values for i in names]
        output = []
        for i in list(product(*values)):
            new_tokenset = TokenSet()
            for j in range(len(names)):
                new_tokenset.add(Token(names[j], i[j]))
            output.append(new_tokenset)
        return(output)
    def resolve(self):
        """Generate a list of non-iterated TokenSets with all dependencies resolved to their values"""
        # Check the TokenSet is valid:
        if self.complete is not True: raise MissingTokenError(self.getExternalDependencies())
        if self.cyclic is True: raise CyclicTokenDependencyError(self.getCyclicDependencyGraph()[0].keys())
        output = []
        for tokenset in self.singularize():
            while True:
                dependent_tokens = tokenset.getDependentTokens()
                if len(dependent_tokens) == 0: break
                for dependent_token in dependent_tokens:
                    unresolved_value = str(list(self[dependent_token].values)[0])
                    resolved_value = self.formatter.format(unresolved_value, tokenset.asDict())
                    tokenset[dependent_token].values = [resolved_value]
            output.append(tokenset)
        return output
    def resolveToken(self, name):
        """Attempt to resolve the value of a single token, even if the rest of the TokenSet has unmet dependencies"""
        res = self.getSubgraph(name).resolve()
        output = [i.asDict()[name] for i in res]
        return(output)
    def resolveString(self, string):
        """Attempt to resolve an arbitrary string using the TokenSet"""
        # Find a mangled name that is not already in the token set:
        ts = TokenSet()
        for t in self.formatter.extractTokens(string): ts.extend(self.getSubgraph(t))
        n = '_STR_'
        while n in ts.names: n = '_{}'.format(n)
        ts.add(Token(n, [string]))
        res = ts.resolveToken(n)
        return res
    def asTFF(self):
        """Return a TFF representation of the TokenSet"""
        output = []
        for t in self.tokens: output.append(self.tokens[t].tff)
        return '\n'.join(output)
    def asJSON(self, indent='\t'):
        """Return a JSON representation of the TokenSet"""
        output = []
        for t in self.tokens:
            output.append('{}{}'.format(indent, self.tokens[t].json))
        return('{{\n{}\n}}'.format(',\n'.join(output)))
    def asDict(self):
        """Return the TokenSet as a simple dictionary"""
        output = {}
        for t in self.names:
            if self[t].empty is True: output[t] = None
            elif self[t].single is True: output[t] =  str(self[t].values[0])
            else: output[t] = [str(i) for i in self[t].values]
        return output
    def asDot(self, graph_name='G'):
        """Return the Dot-formatted dependency graph for the TokenSet"""
        output = []
        g = self.getNames
        output.append('digraph "{}" {{'.format(graph_name))
        for n in self.names: output.append('\t"{}";'.format(n))
        for n in self.names:
            for t in self.tokens[n].dependencies:
                output.append('\t"{}" -> "{}";'.format(n, t))
        output.append('}')
        return '\n'.join(output)
    def __getitem__(self, name): return self._tokens[name]
    def __delitem__(self, name): del(self.tokens[name])
    def __iter__(self): return iter(self.tokens)
    def __repr__(self): return('TokenSet({})'.format(', '.join([repr(self[t]) for t in self.names])))
    formatter = property(getFormatter, setFormatter, "Formatter used for parsing tokens")
    tokens = property(getTokens, setTokens, "The tokens held in the TokenSet")
    names = property(getNames, None, "The token names held in the TokenSet")
    dependencies = property(getExternalDependencies, None, "The external token dependencies")
    complete = property(isComplete, None, "Does the TokenSet have any external dependencies?")
    cyclic = property(isCyclic, None, "Does the TokenSet have any internal cyclic dependencies?")
    iterated = property(isIterated, None, "Does the TokenSet contain any iterated tokens?")
    tff = property(asTFF, None, "TFF representation of the TokenSet")
    json = property(asJSON, None, "JSON representation of the TokenSet")

class TFFParser(object):
    """This class encapsulates a parser for TFF files"""
    def __init__(self, recursionLimit=getrecursionlimit()):
        super(TFFParser, self).__init__()
        self.recursionLimit = recursionLimit
        # Define the TFF DSL:
        kw_chars = alphanums + '.' + '-' + '_' + '{' + '}' + '/' + ':'
        fn_chars = alphanums + '.' + '-' + '_' + '{' + '}' + '/' + ':'
        equals = Suppress(Literal('='))
        open_parenthesis = Suppress(Literal('('))
        close_parenthesis = Suppress(Literal(')'))
        function_keyword = oneOf(['FILE', 'SFILE', 'URL'], caseless=True)
        import_keyword = oneOf(['IMPORT'], caseless=True)
        name = Word(kw_chars) ^ QuotedString('"') ^ QuotedString('\'')
        fname = Word(fn_chars) ^ QuotedString('"') ^ QuotedString('\'').setResultsName('filename')
        value = Word(kw_chars) ^ QuotedString('"') ^ QuotedString('\'')
        values = Group(delimitedList(value, delim=','))
        comment = Suppress(pythonStyleComment())
        empty_line = Optional(comment) + Suppress(LineEnd())
        assignment = Group(name.setResultsName('token') + equals + values.setResultsName('token_values')).setResultsName('assignment')
        function_field = function_keyword.setResultsName('func') + open_parenthesis + fname.setResultsName('filename') + close_parenthesis
        function_assignment = Group(name.setResultsName('token') + equals + function_field).setResultsName('func_assignment')
        import_statement = Group(import_keyword + open_parenthesis + fname.setResultsName('filename') + close_parenthesis).setResultsName('import')
        statement = assignment ^ function_assignment ^ import_statement + Optional(comment) ^ Suppress(LineEnd())
        self._parser = ZeroOrMore(empty_line ^ statement)
    def getParser(self): return self._parser
    def getRecursionLimit(self): return self._recursion_limit
    def setRecursionLimit(self, limit): self._recursion_limit = limit
    def parse(self, filename, depth=0):
        """Parse a TFF file to yield a TokenSet"""
        log.debug('parsing TFF file "{}"'.format(filename))
        output_ts = TokenSet()
        # Open and parse the file:
        file_data = self.parser.parseFile(filename, parseAll=True)
        # Update the output token set:
        for s in file_data:
            if s.getName() is 'assignment':
                output_ts.add(Token(s.token, s.token_values))
            elif s.getName() is 'func_assignment':
                if s.func is 'FILE':
                    for resolved_filename in output_ts.resolveString(s.filename):
                        log.info('reading data from file "{}"'.format(resolved_filename))
                        output_ts.add(Token.fromFile(s.token, resolved_filename, simple=False))
                elif s.func is 'SFILE':
                    for resolved_filename in output_ts.resolveString(s.filename):
                        log.info('reading data from simple file "{}"'.format(resolved_filename))
                        output_ts.add(Token.fromFile(s.token, resolved_filename, simple=True))
                elif s.func is 'URL':
                    for resolved_url in output_ts.resolveString(s.filename):
                        log.info('reading data from from URL "{}"'.format(resolved_url))
                        output_ts.add(Token.fromURL(s.token, resolved_url))
                else: raise NotImplementedError('Assignment from function {} not implemented yet'.format(s.func))
            elif s.getName() is 'import':
                for resolved_filename in output_ts.resolveString(s.filename):
                    log.info('including TFF file "{}"'.format(resolved_filename))
                    new_data = self.parse(resolved_filename, depth=depth + 1)
                    output_ts.extend(new_data)
            else: raise Exception('Invalid statement type')
        return output_ts
    recursionLimit = property(getRecursionLimit, setRecursionLimit, "The maximum permissibe recursion limit")
    parser = property(getParser, None, "The TFF DSL parser object")
