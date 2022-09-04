#!/usr/bin/env python3

import argparse

import sys
import string
import textwrap                 
#ask to insert the correct stroke if the check returns false
def insert_correct_stroke():
    stroke = input("Error. Insert the correct stroke: ")
    return stroke

def assign_blocks(stroke, sequence):
    with sequence as s:
        get_index = s.index(stroke)

#check piston position, if the piston is already in the position of the new stroke, then ask again for the correct stroke   
def check_piston_position(stroke, s, correct_stroke):
    correct_stroke = True
    for i in reversed(range(len(s))):
        if s[i][0] == stroke[0]:
            last_position = i 
            if s[last_position] == stroke:
                print("The piston is already in that position.")
                correct_stroke = False
                break
            else:
                correct_stroke = True
                break
    
    return correct_stroke

#check the input from the user

def check_stroke(stroke, sequence):                                                                  
    correct_stroke = False
    while not correct_stroke:                                                                          
        if len(stroke) > 2:     #limit input buffer                                         
            print("Too many arguments. ")
            correct_stroke = False
            break
        elif stroke[0] in string.ascii_lowercase or stroke[0] in string.ascii_uppercase:        #the name of the piston is the first letter to check      
            if stroke[1] == '+' or stroke[1] == '-':                                            #the stroke can only be positive or negative
                correct_stroke = check_piston_position(stroke, sequence, correct_stroke)
                if correct_stroke == False:
                    break
            else:
                correct_stroke = False                                                                  
                break
        elif '/' in stroke[0]:                                                             
            correct_stroke = True
            print("The sequence is terminated.\n")

        else:
            print("A letter must be the name of the actuator")
        
    return correct_stroke

#function that ask the user to insert the strokes, if the stroke is correct, add it to the sequence array
def insert_stroke(sequence):
    stroke = input("Insert stroke: ")
    continue_insert = False
    while not continue_insert:
        correct_stroke = check_stroke(stroke, sequence)
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
        stop_sequence = False
        try:
            while not stop_sequence:
                stroke, sequence = insert_stroke(sequence)

                if '/' in stroke:
                    del sequence[-1]
                    stop_sequence = True
                    check_for_loop(sequence)
                else:
                    stop_sequence = False
            

        except KeyboardInterrupt:
            print("\nUser has terminated the sequence.\n")
        
'''        sequence = []
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
        #check_sequence()'''
    

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
