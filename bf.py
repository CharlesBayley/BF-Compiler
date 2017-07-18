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

from ast import parseFile

if __name__ == '__main__':
    args = docopt(__doc__)
    ast = parseFile(args['<bffile>'])
    ast.optimize()
    if args['run']:
        ast.run()
    elif args['compile']:
        ast.compile(args['--out'])
