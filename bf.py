#!/usr/bin/python
"""BrainFuck

Usage:
  bf run <bffile>
  bf compile [options] <bffile>

Options:
  -o --out=<outfile>  The file to place the compiled code.
                      [Default: out.c]

"""

from docopt import docopt

class State:
    def __init__(self, ram=None, ramCounter=0):
        self.ram = ram
        if not self.ram:
            self.ram = [0] * 32768
        self.ramCounter = ramCounter

    def increment(self, n=1):
        self.ram[self.ramCounter] += n
        self.ram[self.ramCounter] %= 256

    def decrement(self, n=1):
        self.increment(-n)

    def incrementCounter(self, n=1):
        self.ramCounter += n

    def decrementCounter(self, n=1):
        self.incrementCounter(-n)

    def testByte(self):
        if self.ram[self.ramCounter] is 0:
            return True
        return False

    def printByte(self):
        print(chr(self.ram[self.ramCounter]), end='')

    def readByte(self):
        try:
            self.ram[self.ramCounter] = ord(input()[0])
        except IndexError:
            self.ram[self.ramCounter] = ord('\n')

class Ast:
    def __init__(self, headNode, state=None):
        self.headNode = headNode
        self.state = state
        if not self.state:
            self.state = State()

    def run(self):
        self.headNode.run(self.state)

    def compile(self, file='out.c'):
        message = '#include <stdio.h>\n'
        message += '\n'
        message += 'int main() {{\n'
        message += ' char array[32768];\n'
        message += ' char *ptr=array;'
        message += '{body}'
        message += ' return 0;'
        message += '}}\n'
        message = message.format(body=self.headNode.compile(0))
        with open(file, 'w') as f:
            f.write(message)

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

def parseFile(filename):
    def nextInstruction():
        with open(filename) as f:
            for line in f:
                for char in line:
                    if char in '+-><[].,':
                        yield char

    headNode = StatementSequenceNode()
    currentNode = headNode
    for instruction in nextInstruction():
        if instruction in '+-><.,':
            currentNode.append(StatementNode(currentNode, instruction))
        elif instruction is '[':
            newNode = LoopNode(currentNode)
            currentNode.append(newNode)
            currentNode = newNode
        else:
            currentNode = currentNode.parentNode
    return Ast(headNode)

if __name__ == '__main__':
    args = docopt(__doc__)
    ast = parseFile(args['<bffile>'])
    if args['run']:
        ast.run()
    elif args['compile']:
        ast.compile(args['--out'])
