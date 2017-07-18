#!/usr/bin/python

from nodes import *

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
        message += ' char *ptr=array;\n'
        message += '{body}'
        message += ' return 0;\n'
        message += '}}\n'
        message = message.format(body=self.headNode.compile(0))
        with open(file, 'w') as f:
            f.write(message)

    def optimize(self):
        self.headNode.optimize()

def parseFile(filename):
    def nextInstruction():
        with open(filename) as f:
            for line in f:
                for char in line:
                    if char in '+-><[].,':
                        yield char
                    elif char is ';':
                        break
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
