#!/usr/bin/python
import time
import sys


# YOUR FUNCTIONS GO HERE -------------------------------------
listA = []
listB = []
max_score = []
num_alignments = 0

# ------------------------------------------------------------
# function align
#   @param - seqALeft = sequence left in A
#   @param - seqANow = sequence written out
#   @param - seqBLeft = sequence left in B
#   @param - seqBNow = sequence written out
#   @param - score = current score of sequence
def align(seqALeft,seqANow,seqBLeft,seqBNow, score):
#   base case if both sequence left is zero
    global num_alignments
    if seqALeft == '' and seqBLeft == '':
        num_alignments = num_alignments + 1
#   adds both NowSequences to lists with highest scores
        if len(max_score) == 0 or score > max_score[-1]:
            max_score.append(score)
            listA.append(seqANow)
            listB.append(seqBNow)
        return
#   if one of the sequences ends it adds '-' to the front of the other sequence
    elif seqALeft == '':
        B = len(seqBLeft)
        score = score + (-4 * B)
        align(seqALeft, ('-' * B) + seqANow, '', seqBLeft + seqBNow, score)
    elif seqBLeft == '':
        A = len(seqALeft)
        score = score + (-4 * A)
        align('', seqALeft + seqANow, seqBLeft, ('-' * A) + seqBNow, score)
#   finds last character of the each sequence
    else:
        al = seqALeft[-1]
        bl = seqBLeft[-1]
        if al != bl:
            ad = -3
        elif al == 'A':
            ad = 3
        elif al == 'C':
            ad = 2
        elif al == 'G':
            ad = 1
        #last is 'T'
        else:
            ad = 2
        #returns with both letters lined up, with seqALeft[-1] lined up with '-' on seqBNow, with seqBLeft[-1] lined up with '-' on seqBNow
        align(seqALeft[0:-1],al + seqANow,seqBLeft[:-1],bl + seqBNow, score + ad)
        align(seqALeft[:-1], al + seqANow, seqBLeft, '-' + seqBNow, score - 4)
        align(seqALeft, '-' + seqANow, seqBLeft[:-1], bl + seqBNow, score - 4)
        
        
        


# DO NOT EDIT ------------------------------------------------
# Given an alignment, which is two strings, display it

def displayAlignment(alignment):
    string1 = alignment[0]
    string2 = alignment[1]
    string3 = ''
    for i in range(min(len(string1),len(string2))):
        if string1[i]==string2[i]:
            string3=string3+"|"
        else:
            string3=string3+" "
    print('Alignment ')
    print('String1: '+string1)
    print('         '+string3)
    print('String2: '+string2+'\n\n')

# ------------------------------------------------------------


# DO NOT EDIT ------------------------------------------------
# This opens the files, loads the sequences and starts the timer
file1 = open(sys.argv[1], 'r')
seq1=file1.read()
file1.close()
file2 = open(sys.argv[2], 'r')
seq2=file2.read()
file2.close()
start = time.time()

#-------------------------------------------------------------


# YOUR CODE GOES HERE ----------------------------------------
# The sequences are contained in the variables seq1 and seq2 from the code above.
# Call any functions you need here, you can define them above.
# To work with the printing functions below the best alignment should be called best_alignment and its score should be called best_score. 
# The number of alignments you have checked should be stored in a variable called num_alignments.
#   initialize listA and listB and max_score

#   calls align
align(seq1,'',seq2,'',0)
best_score = max_score[-1]
best_alignment = [listA[-1],listB[-1]]
num_alignments = num_alignments


#-------------------------------------------------------------


# DO NOT EDIT ------------------------------------------------
# This calculates the time taken and will print out useful information 
stop = time.time()
time_taken=stop-start

# Print out the best
print('Alignments generated: '+str(num_alignments))
print('Time taken: '+str(time_taken))
print('Best (score '+str(best_score)+'):')
displayAlignment(best_alignment)

#-------------------------------------------------------------
