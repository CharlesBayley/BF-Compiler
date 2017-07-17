#!/usr/bin/python

class AstNode:
    pass

class StatementSequenceNode(AstNode):
    def __init__(self, parentNode=None, statementNodes=None):
        self.parentNode = parentNode
        self.statementNodes = statementNodes
        if not statementNodes:
            self.statementNodes = []

    def run(self, state):
        for statementNode in self.statementNodes:
            statementNode.run(state)

    def append(self, node):
        self.statementNodes.append(node)

    def compile(self, nest):
        nest += 1
        message = ''
        for statementNode in self.statementNodes:
            message += statementNode.compile(nest)
        return message

class LoopNode(StatementSequenceNode):
    def __init__(self, parentNode):
        super().__init__(parentNode)

    def run(self, state):
        while not state.testByte():
            super().run(state)

    def compile(self, nest):
        message = '{nest}while(*ptr) {{\n'
        message += '{body}'
        message += '{nest}}}\n'
        return message.format(nest=nest * ' ', body=super().compile(nest))

class StatementNode(AstNode):
    def __init__(self, parentNode, statement):
        self.parentNode = parentNode
        self.statement = statement

    def run(self, state):
        if self.statement is '+':
            state.increment()
        elif self.statement is '-':
            state.decrement()
        elif self.statement is '>':
            state.incrementCounter()
        elif self.statement is '<':
            state.decrementCounter()
        elif self.statement is '.':
            state.printByte()
        elif self.statement is ',':
            state.readByte()

    def compile(self, nest):
        statement = ''
        if self.statement is '+':
            statement = '++*ptr;'
        elif self.statement is '-':
            statement = '--*ptr;'
        elif self.statement is '>':
            statement = '++ptr;'
        elif self.statement is '<':
            statement = '--ptr;'
        elif self.statement is '.':
            statement = 'putchar(*ptr);'
        elif self.statement is ',':
            statement = '*ptr=getchar();'
        return '{}{}\n'.format(nest * ' ', statement)
