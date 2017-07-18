#!/usr/bin/python

class AstNode:
    def __init__(self, parentNode):
        self.parentNode = parentNode

class StatementNode(AstNode):
    def __init__(self, parentNode, statement):
        super().__init__(parentNode)
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

class ValueAdjustmentNode(AstNode):
    def __init__(self, parentNode, amount):
        super().__init__(parentNode)
        self.amount = amount

    def run(self, state):
        state.increment(self.amount)

    def compile(self, nest):
        statement = ''
        if self.amount >= 0:
            statement = '*ptr += {};'.format(self.amount)
        else:
            statement = '*ptr -= {};'.format(-self.amount)
        return '{}{}\n'.format(nest * ' ', statement)

class PointerAdjustmentNode(AstNode):
    def __init__(self, parentNode, amount):
        super().__init__(parentNode)
        self.amount = amount

    def run(self, state):
        state.incrementCounter(self.amount)

    def compile(self, nest):
        statement = ''
        if self.amount >= 0:
            statement = 'ptr += {};'.format(self.amount)
        else:
            statement = 'ptr -= {};'.format(-self.amount)
        return '{}{}\n'.format(nest * ' ', statement)

class StatementSequenceNode(AstNode):
    def __init__(self, parentNode=None, statementNodes=None):
        super().__init__(parentNode)
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

    def _optimizeStackableNodes(self, instructionList, newNodeClass):
        newStatementNodes = []
        nextNode = newNodeClass(self, 0)
        def resetNextNodeState(statementNode=None):
            nonlocal newStatementNodes
            nonlocal nextNode
            if nextNode.amount != 0:
                newStatementNodes.append(nextNode)
                nextNode = newNodeClass(self, 0)
            if statementNode:
                newStatementNodes.append(statementNode)
        for statementNode in self.statementNodes:
            try:
                if not statementNode.statement in instructionList:
                    raise AttributeError()
                if statementNode.statement is instructionList[0]:
                    nextNode.amount += 1
                else:
                    nextNode.amount -= 1
            except AttributeError:
                resetNextNodeState(statementNode)
        resetNextNodeState()
        self.statementNodes = newStatementNodes

    def optimize(self):
        self._optimizeStackableNodes('+-', ValueAdjustmentNode)
        self._optimizeStackableNodes('><', PointerAdjustmentNode)
        for node in self.statementNodes:
            try:
                node.optimize()
            except AttributeError:
                pass

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
