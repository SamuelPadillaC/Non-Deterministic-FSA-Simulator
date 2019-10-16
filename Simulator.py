########################################
# Created by Samuelito Perro #
########################################
# This is a NON-DETERMINISTIC Finite State Automata Simulator
# This program takes 3 parameters: An NFSA detinition file,
# A file holding strings, An output file name.
# check description document for the format of these files

from collections import deque
import time, sys
import numpy as np
import pandas as pd

start = time.time()
#################################
#           CLASSES             #
#################################

class Machine:
    #Initialize values for the Machine
    def __init__(self, Path):
        self.vector_lines = []
        self.Alphabet = []
        self.States = []
        self.Accepting_States = []
        self.Transition_Function = []
        self.Possible = []
        self.Impossible = []
        self.Redundant = []

        self.ReadNFSA(Path)
        
    def ReadNFSA (self, NFSA_Description):
        # Opening the file #
        file_object = open(NFSA_Description, 'r')
        self.vector_lines = (file_object.readlines()) # Reads all the lines into the vector vector_lines
        file_object.close()
        
        #Define variables
        self.Alphabet = ''
        for i in self.vector_lines[0]: #This for loop is to get rid of the extra \n at the end of the alphabet line
            if i is not '\n':
                self.Alphabet += i       
        self.States = int(self.vector_lines[1])
        self.Accepting_States = self.vector_lines[2].split() #Split the string by ' '

        # Check if the amount of lines in the file matches the amount of states #
        if self.States + 3 != len(self.vector_lines):
            print("\nThe FSA description file does not have the correct amount of lines.")
            print("The file should have ", self.States + 3, "lines and it has ", len(self.vector_lines), "lines.")
            exit()

        # Transforming items in Accepting_States to ints and checking if they are in the proper range 0 - (States - 1) #
        for i in range(0, len(self.Accepting_States)):
            if not self.Accepting_States[i].isdigit(): #If it is not a number
                print("\n The line 3 - Accepting States - contains invlid characters")
                exit()
            else: #Else transform into a number
                self.Accepting_States[i] = int(self.Accepting_States[i]) #Transform to int
            
            if self.Accepting_States[i] < 0 or self.Accepting_States[i] >= self.States: #If out of range
                print("\nAt least one of the Accepted states is off range")
                exit() 

    def Create_Table (self):
        # Interpreting the string #
        for row in range(3, len(self.vector_lines)):
            #Create a new row in the table
            self.Transition_Function.append([])
            
            #Creating len(alphabet)+1 sets in the row
            for i in range (0, len(self.Alphabet)+1):
                self.Transition_Function[row-3].append([])   

            newrow = '' #Initializing a new row
            
            #Checking for empty sets and building new row
            for char in range(0, len(self.vector_lines[row])):
                #If finding subsequent '{}'
                if self.vector_lines[row][char] == '{':
                    if self.vector_lines[row][char+1] == '}':
                        newrow += '{x' #add an x for interpretation later
                else: #Else append to newrow
                    newrow += self.vector_lines[row][char]

            #Getting rid of the '{}'
            newrow = newrow.replace('{', '')
            newrow = newrow.replace('}', ' ')
            
            #Splitting the sets by spaces
            sets = newrow.split()
            
            #Check elemts of new row
            if len(sets) != len(self.Alphabet) + 1: #If the length of row does not match the size of len(alphabet) + 1 (accounting for lambda) there is something wrong.
                print("\nERROR: At least one of the last n lines doesn\'t have the right number of sets")
                exit()
            
            #Looping through each set
            for y in range (0, len(sets)):                 
                #Checking for empty sets - signled by 'x'
                if sets[y] == 'x': 
                    pass #Leave the set empty
                
                else:
                    states = sets[y].split(',') #Split the states by comma
                    
                    # Trasform items in states into ints and append#
                    for z in range(0, len(states)):
                        #Checking if it is a number
                        if not states[z].isdigit():
                            print("\n At least one of the last n lines contains an invalid character")
                            exit()
                        else: #Else transform into a number and append
                            self.Transition_Function[row-3][y].append(int(states[z]))
        
        return self.Transition_Function

##########################################
#            DRIVER FUNCTION             #
##########################################

def main():
    # Checking for the amount of parameters #
    if len(sys.argv) != 4:
        print("\n USAGE: Please enter 3 parameters in the following order:")
        print("1. A NFSA descrption file\n2. An Input File \n3. An Output File")
        exit()


    # Reading file and creating machine #
    M1 = Machine(sys.argv[1])
    
    # Transforming Table to a Pandas Dataframe #
    Transition_Table = Make_Pandas_DataFrame(M1.Create_Table(), M1.States, M1.Alphabet)
    
    # Read and Verify Input File #
    Input_lines = Read_Input (sys.argv[2], M1.Alphabet)

    # Building Lambda Closure #
    Lambda_Closure = Build_Lambda_Closure(Transition_Table["lamb"], M1.States)
    
    # Check Input Lines #
    Check_Input (Input_lines, Lambda_Closure, Transition_Table, M1.Accepting_States, sys.argv[3]) 

    #################################################

    # Final Message #
    print("\n\nSuccesful run. Check", sys.argv[3], "file.")
    print ("\nExecution time was: ", time.time() - start)

#################################
#           FUNCTIONS           #
#################################

def Make_Pandas_DataFrame(Transition_Function, States, Alphabet):

    # Creating DataFrame
    Table = pd.DataFrame(Transition_Function)

    # Manipulating Column Labels #
    cols = ['lamb'] 
    for i in Alphabet:
        cols.append(i)
    
    Table.columns = cols    
    
    return Table

#################################################
#################################################

def Build_Lambda_Closure(Lambda, States):
    
    # Initialize Lambda Closure #
    l_closure = []

    # Looping through all states #
    for i in range (0, States):
        #Initialize the lambda closure of the state to include itself
        State_closure = [i]
        #Initialize queue with all states in the states Lambda transition
        CheckingQ = deque(Lambda[i])
        
        #Loop while the Q is not empty
        while (CheckingQ): #An Empty Q is false
            popped = CheckingQ.popleft() #Pop the first element 

            if popped not in State_closure:
                State_closure.append(popped) #Append to closure
                CheckingQ.extend(Lambda[popped]) #Extend Popped l-transitions to Q

        # Append State_Closure #
        l_closure.append(State_closure)

    # Transforming l_closure to a Pandas Series #
    Lambda_Closure = pd.Series(l_closure)
    Lambda_Closure.name = "Lambda Closure"

    return Lambda_Closure

#################################################
#################################################

def Read_Input (Path, Alphabet):
    # Open and Read File #
    file_object = open(Path, 'r')
    Input_lines = (file_object.readlines()) # Reads all the lines into Input_lines
    file_object.close()

    # Check that all Lines are valid #
    Return_list = []
    for line in Input_lines: #Loop through each line
        invalid = 0

        if line != '\n': #Only check non empty lines
            for char in line: #Check each character
                
                #If char is the last '\n'
                if char == '\n' and line.index(char) == len(line)-1:
                    line = line.rstrip('\n') #Strip the last '\n' from line
                
                #If invalid char, print error but still append.
                elif char not in Alphabet:
                    invalid = 1

        if invalid == 0: #Only for valid words
            #Append line to return list
            if line == '\n': #Empty lines are valid, they are empty strings
                Return_list.append('')
            else:
                Return_list.append(line)
        else:
            print ("\n-----\nERROR READING INPUT FILE: The word", line, "contains an invalid character.\nThe program will",
                    "still run, but check output file\n-----")
            Return_list.append("\n%s" % line)

    return Return_list

#################################################
#################################################

def Check_Input (Input, Lambda_Closure, Transition_Table, accepting, Output_File):
    #Opening the output file
    Output = open(Output_File, 'w')
    
    #Looping through each input
    for word in Input:
        looking_at = [0] #Initialize looking_at
        is_valid = 0 #Initialize boolean for valid checking
        
        #Check for invalid words
        if len(word) > 0 and word[0] == '\n':
            #Write to output file without the initial '\n'
            Output.write("%s|Contains at least one invalid char\n" % word[1:])
            is_valid = -1 #Make bool out of range to avoid writing the word again
        
        else: #With Valid words only
            #Looping through each char in the word
            for char in word:
                #Get lambda closure of each element in looking_at
                looking_at = get_lambda_closuer(looking_at, Lambda_Closure)

                #Follow the letter for each element in looking_at
                looking_at = follow_character(looking_at, char, Transition_Table)
                if not looking_at: #An empty list gets evaluated to false
                    #Word is not valid. Change bool and break
                    is_valid = 0
                    break
                
                #Get lambda closure of each element in lookin_at again
                looking_at = get_lambda_closuer(looking_at, Lambda_Closure)
                #print (looking_at)

        #Checking for a valid word 
        if is_valid != -1: #Accounting for the corner case of state 0 being an accepting state. Only consider valid words
            for i in accepting:
                if i in looking_at:
                    #Word is valid. Change bool and break
                    is_valid = 1
                    break

        if is_valid == 1: #If valid
            Output.write("%s|+\n" % word)
        elif is_valid == 0: #If not valid
            Output.write("%s|-\n" % word)
            
    return

#################################################
#################################################

def get_lambda_closuer(current_list, Lambda_Closure):
    #Initialize closure
    closure = []
    
    #Looping through each element in current_list
    for element in current_list:
        #Looking at each element in the lamb-closure of the element
        for state in Lambda_Closure.loc[element]:
            #append only if the element doesn't exist in the closure yet
            if state not in closure:
                closure.append(state)
    
    return closure

#################################################
#################################################

def follow_character(current_list, char, Table):
    #Initialize new list
    new_list = []

    #Looping through each element in current_list
    for element in current_list:
        #Looping through each state in the char transition of element
        for state in Table.loc[element,char]:
            #Append only if the new state does not exist in new_list yet
            if state not in new_list:
                new_list.append(state)

    return new_list

#################################################
#################################################

# Calling the main function first #
if __name__ == "__main__":
    main ()
#####################