import re, sys, os
functions, definitions = {}, {}
verbose = False

ifDefRegex = r"#ifdef (\w+)"
ifNDefRegex = r"#ifndef (\w+)"
elseDefRegex = r"#else"
endifDefRegex = r"#endif"
includeRegex = r"#include \"(.+)\""
definitionRegex = r"#define[ ]+(\w+)\s+(.*)"
functionRegex = r"#define\s+(\w+)\((\w+(?:\s*,\s*\w+)*)\)\s(.*)"
functionCallRegex = r"(\w+)\(([^\)]+)"

def isFunction(s): return re.match(functionRegex, s) != None
def isDefinition(s): return re.match(definitionRegex, s) != None
def isFunctionCall(s): return re.match(functionCallRegex, s) != None

def parseFunctionText(s):
    return s.replace('\\n', '\n')

def parseFunction(s, linenumber):
    parsed = re.search(functionRegex, s)
    name, args, text =  parsed.group(1), parsed.group(2).split(","), parsed.group(3)
    if verbose: print '<parser:' + str(linenumber) + '> parsed function ' + name + ' -> ' + str(args)
    functions[name] = args, parseFunctionText(text)

def parseDefinition(s, linenumber):
    parsed = re.search(definitionRegex, s)
    name, value = parsed.group(1), parsed.group(2)
    if verbose: print '<parser:' + str(linenumber) + '> parsed definition ' + name + ' -> ' + value
    definitions[name] = value

def parseFunctionCall(s):
    parsed = re.search(functionCallRegex, s)
    name, args = parsed.group(1), parsed.group(2).split(",")
    return name, args

def parseLine(s, linenumber):
    if isDefinition(s):
        parseDefinition(s, linenumber)
    elif isFunction(s):
        parseFunction(s, linenumber)
    else:
        return True

def parseFile(inputFilename):
  for i, line in enumerate(open(inputFilename, 'r')):
    parseLine(line, i + 1)

def transformFile(inputFilename):
  parseFile(inputFilename)
  for i, line in enumerate(open(inputFilename, 'r')):
      processedLine = preprocessLine(line, i + 1)
      if processedLine:
          for char in processedLine:
              yield char

def preprocessLine(s, linenumber):
    # if, else, endif block
    global preprocessorState
    global verbose
    modified = preprocessorState
    if re.match(ifDefRegex, s) != None or re.match(ifNDefRegex, s) != None:
        invert = re.match(ifNDefRegex, s) != None
        if preprocessorState != 'initial':
            print str(linenumber) + ': nested #ifdef/#ifndef is not supported!'
            sys.exit(-1)
        keyword = re.search((ifNDefRegex if invert else ifDefRegex), s).group(1)
        if keyword in definitions:
            preprocessorState = 'ifdef_true' if not invert else 'ifdef_false'
        else:
            preprocessorState = 'ifdef_false' if not invert else 'ifdef_true'
    elif re.match(elseDefRegex, s) != None:
        if preprocessorState == 'ifdef_false':
            preprocessorState = 'else_true'
        elif preprocessorState == 'ifdef_true':
            preprocessorState = 'else_false'            
        else:
            print str(linenumber) + ': invalid #else statement'
            sys.exit(-1)
        return None
    elif re.match(endifDefRegex, s) != None:
        if preprocessorState == 'initial':
            print 'invalid #endif statement at line ' + str(linenumber)
            sys.exit(-1)
        preprocessorState = 'initial'

    if preprocessorState != modified:
        if verbose: print '<pre:' + str(linenumber) + '> ' + preprocessorState + ': \t' + s.rstrip()
        return None

    if re.match(includeRegex, s) != None:
        filename = re.search(includeRegex, s).group(1)
        parseFile(filename)
        return ''.join([char for char in transformFile(filename)])

    # don't echo #define lines
    if isFunction(s) or isDefinition(s):
        return None
        
    # definition expansion
    for name, value in definitions.items():
        if name in s:
            s = s.replace(name, value)

    # function call expansion
    if isFunctionCall(s):
        linename, lineargs = parseFunctionCall(s)
        if linename in functions:
            if verbose: print '<pre:' + str(linenumber) + '> matched ' + linename + str(lineargs)
            args, text = functions[linename]
            if len(args) != len(lineargs):
                print 'error: call to ' + linename + ' needs ' + str(len(args)) + ' arguments'
                sys.exit(-1)
            for i, a in enumerate(args):
                text = text.replace(a, lineargs[i])
            s = text

    if (preprocessorState == 'ifdef_false' or preprocessorState == 'else_false'):
        return None

    return s

def preprocessFile(inputFilename, outputFilename, flagVerbose = False):
    global verbose
    verbose = flagVerbose
    global preprocessorState
    preprocessorState = 'initial'
    outfilename = inputFilename + '.p' if outputFilename == None else outputFilename
    if os.path.exists(outfilename):
        os.remove(outfilename)
    out = open(outfilename, 'w')
    for c in transformFile(inputFilename):
        out.write(c)
