#!/usr/bin/python

helpstring = \
'''usage: tpypp inputfile [outputfile]
tiny python preprocessor
(c) 2012 Isaac Evans

example macros:
#define TEMP r6
#define SWAP(A, B) mov TEMP, A\\n mov B, A\\n mov TEMP, B\\n'''

import re, sys
functions, definitions = {}, {}
verbose = True

if not 2 <= len(sys.argv) <= 3:
    print helpstring
    sys.exit(-1)
if len(sys.argv) == 3 and sys.argv[1] == sys.argv[2]:
    print 'input file cannot be same as output file'
    sys.exit(-1)

definitionRegex = r"#define (\w+)\s+(.*)"
functionRegex = r"#define\s+(\w+)\((\w+(?:,\w+)*)\)\s(.*)"
functionCallRegex = r"(\w+)\(([^\)]+)"

def isFunction(s): return re.match(functionRegex, s) != None
def isDefinition(s): return re.match(definitionRegex, s) != None
def isFunctionCall(s): return re.match(functionCallRegex, s) != None

def parseFunctionText(s):
    return s.replace('\\n', '\n')

def parseFunction(s):
    parsed = re.search(functionRegex, s)
    name, args, text =  parsed.group(1), parsed.group(2).split(","), parsed.group(3)
    if verbose: print '<pre>:parsed function ' + name + ' -> ' + str(args)
    functions[name] = args, parseFunctionText(text)

def parseDefinition(s):
    parsed = re.search(definitionRegex, s)
    name, value = parsed.group(1), parsed.group(2)
    if verbose: print '<pre>:parsed definition ' + name + ' -> ' + value
    definitions[name] = value

def parseFunctionCall(s):
    parsed = re.search(functionCallRegex, s)
    name, args = parsed.group(1), parsed.group(2).split(",")
    return name, args

def parseLine(s):
    if isDefinition(s):
        parseDefinition(s)
    if isFunction(s):
        parseFunction(s)

def preprocessLine(s, linenumber):
    # definition expansion
    for name, value in definitions.items():
        if name in s:
            s = s.replace(name, value)

    # function call expansion
    if isFunctionCall(s):
        linename, lineargs = parseFunctionCall(s)
        if linename in functions:
            if verbose: print str(linenumber) + ': matched ' + linename + str(lineargs)
            args, text = functions[linename]
            if len(args) != len(lineargs):
                print 'error: call to ' + linename + ' needs ' + str(len(args)) + ' arguments'
                sys.exit(-1)
            for i, a in enumerate(args):
                text = text.replace(a, lineargs[i])
            s = text

    return s

for line in open(sys.argv[1], 'r'):
    parseLine(line)
out = open(sys.argv[1] + '.p' if len(sys.argv) != 3 else sys.argv[2], 'w')
for i, line in enumerate(open(sys.argv[1], 'r')):
    out.write(preprocessLine(line, i))
