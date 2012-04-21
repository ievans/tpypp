tpypp
=====
###tiny python preprocessor###
(c) 2012 Isaac Evans

usage: tpypp inputfile [outputfile]

example macros:

    #define TEMP r6
    #define SWAP(A, B) mov TEMP, A\n mov B, A\n mov TEMP, B\n
    #include "../tests.asm"
    #ifdef TEMP
    SWAP(TEMP, r2)
    #else
    SWAP(r5, r2)
    #endif
