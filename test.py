#!/usr/bin/python
import sys
import os
import filecmp
import preprocessor

def checkFile(A, B):
    return filecmp.cmp(A, B)

subdirectory = './tests/'
outputSuffix = '.p'
expectedSuffix = '.expect'

files = [x for x in os.listdir(subdirectory) if not x.endswith(expectedSuffix)]
if len(files) == 0:
    print 'no tests found'
    
for i, filename in enumerate(files):
    pair = (subdirectory + filename, subdirectory + filename + outputSuffix)
    preprocessor.preprocessFile(*pair)
    checkPair = (subdirectory + filename + outputSuffix, subdirectory + filename + expectedSuffix)
    if checkFile(*checkPair) != True:
        print 'check failed for ' + str(checkPair)
        sys.exit(-1)
    os.remove(pair[1])
    print 'checked ' + str(i + 1) + ' of ' + str(len(files)) + ': ' + str(pair[0])
