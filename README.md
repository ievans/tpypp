tpypp
=====
###tiny python preprocessor###
(c) 2012 Isaac Evans

usage: tpypp inputfile [outputfile]

flags: 

       --v for verbose mode

notes:
	if not specified, the output filename is the input filename + '.p'

example macros:

    #define TEMP r6
    #define SWAP(A, B) mov TEMP, A\n mov B, A\n mov TEMP, B\n
    #ifdef TEMP
    SWAP(TEMP, r2)
    #else
    SWAP(r5, r2)
    #endif

the preprocessor will be recursively run on included files:

    #include "../tests.asm"
