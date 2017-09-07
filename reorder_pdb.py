#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, subprocess
from argparse import ArgumentParser

"""
To reorder the atoms of a pdb file
./reorder_pdb.py -f pdb.pdb -o ordered.pdb
"""

######################## Parsing stuff ########################

parser = ArgumentParser(description=""" Reorders the atoms of a pdb file 

Usage: something like that
./reorder_pdb.py -f pdb.pdb -o ordered.pdb""")

# Named arguments
parser.add_argument("-f", "--file", help="The name of the input pdb file", required=True)
parser.add_argument("-o", "--output", help="The name of the output ordered pdb file", required=True)

args = parser.parse_args()

######################## Functions and miscellaneous ########################

# Input and output
input_file = args.file
output_file = args.output

######################## Main ########################

if __name__ == '__main__':

    # Opening the outfile
    out = open(output_file, "w")

    # The numbering starts at 1
    n = 1

    # Loop
    with open(input_file, "r") as openfileobject:
        for line in openfileobject:

            # Split the line
            lline = line.split()

            # Unwraps the line
            race = lline[0]

            # If it's not an ATOM declaration, write the line
            if "ATOM" not in race and "TER" not in race:
                out.write(line)
            # Else ... Write the same line with the numbers
            else:
                out.write("{:6s}{:5d}{:s}".format(race, n, line[11:]))

                # Next atom
                n += 1




