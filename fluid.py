#!/usr/bin/env python3

import argparse
import errno
from os import strerror
import sys
import string
import textwrap

def controllo_stroke(stroke):                                                                   #controllo della corsa del pistone, deve essere in formato 'lettera' + '+ o -'
    ok = False
    while ok == False:                                                                          #variabile di controllo booleana, se Falsa allora la corsa non e' definita correttamente
        try:
            if stroke[0] in string.ascii_lowercase or stroke[0] in string.ascii_uppercase:      #controllo che ci sia una lettera e non un simbolo nel nome della corsa
                
                if stroke[1] == '+' or stroke[1] == '-':                                        #se ho una lettera prima, controllo che ci sia il '+' o il '-'
                    ok = True
                    break

                else:
                    ok = False                                                                  #corsa errata, ritorno ok Falso
                    break

            elif '/' in stroke[0]:                                                              #controllo se il comando di 'termina sequenza' e' stato inserito
                ok = True
                print("The sequence is terminated.\n")
            
            else:
                print("A letter must be the name of the actuator")
        
        except len(stroke) > 2:                                                                 #una specie di limite buffer cosi non andiamo oltre la lunghezza di due dati inseriti
            print("Too many arguments. ")
            break

    return ok

def inserire_stroke():
    stroke = input("Inserire corsa: ")
    while True:
        ok = controllo_stroke(stroke)
        if ok == False:
            new_stroke = input("Inserire nuovamente corsa: ")
            stroke = new_stroke
            True
        else:
            False
            break
    with open("sequenza.txt","w") as f:
        try:
            if '/' not in stroke[0]:
                print(stroke)
                f.write(stroke)
                f.flush()
                f.close()
            else:
                print("We can proceed with the analysis. ")
                f.flush()
                f.close()
        except IOError as e:
            print(e)
    return stroke

class FluidPy:
    def __init__(self, args):
        self.args = args
    def run(self):
        if self.args.loop:
            self.loop()
        else:
            self.normal()

    def normal(self):
        try:
            while True:
                stroke = inserire_stroke()
                if '/' in stroke:
                    break
        except KeyboardInterrupt:
            print("User terminated the sequence.\n")
            sys.exit()
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='FluidPy Tool',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''Example:
    fluid.py -f=mysequence.txt #lettura sequenza da file
    fluid.py -l -f=mysequence.txt #lettura sequenza con loop da file
    '''))
    parser.add_argument('-f', '--file', type=argparse.FileType('r'))
    parser.add_argument('-l','--loop',help='sequence with loop in it')
    args = parser.parse_args()
    #print(args.file.readlines())
    fp = FluidPy(args)
    fp.run()
