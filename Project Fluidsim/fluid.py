#!/usr/bin/env python3

import argparse

import sys
import string
import textwrap
 
def insert_correct_stroke():
    stroke = input("Error. Insert the correct stroke: ")
    return stroke


def check_stroke(stroke):                                                                  
    correct_stroke = False
    while not correct_stroke:                                                                          
        if len(stroke) > 2:                                                                 
            print("Too many arguments. ")
            correct_stroke = False
            break

        elif stroke[0] in string.ascii_lowercase or stroke[0] in string.ascii_uppercase:      
            
            if stroke[1] == '+' or stroke[1] == '-':                                       
                correct_stroke = True

            else:
                correct_stroke = False                                                                  
                

        elif '/' in stroke[0]:                                                             
            correct_stroke = True
            print("The sequence is terminated.\n")
        
        else:
            print("A letter must be the name of the actuator")
        
    return correct_stroke

def insert_stroke(sequence):
    stroke = input("Insert stroke: ")
    continue_insert = False
    while not continue_insert:
        correct_stroke = check_stroke(stroke)
        if correct_stroke != True:
            if '/' not in stroke:
                stroke = insert_correct_stroke()
            else:
                print("We can proceed with the analysis")
        else:
            continue_insert = True

    sequence.append(stroke)
    '''with open("sequence.txt","w") as f:
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
            print(e)'''
    return stroke, sequence

class FluidPy:
    def __init__(self, args):
        self.args = args
    def run(self):
        if self.args.loop:
            self.loop()
        else:
            self.normal()
    
    #def sequence(self, sequence, args):

    def normal(self):
        sequence = []
        try:
            while True:
                stroke, sequence = insert_stroke(sequence)
                if '/' in stroke:
                    del sequence[-1]
                    break
        except KeyboardInterrupt:
            print("User terminated the sequence.\n")
            sys.exit()
        print(sequence)
        #check_sequence()
    

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
