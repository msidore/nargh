#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, subprocess, os
from argparse import ArgumentParser

"""
pdb2gmx with a propka file ? Hell yeah !
"""

######################## Parsing stuff ########################

parser = ArgumentParser(description="""pdb2gmx with a propka file ? Hell yeah !

Automatization of pdb2gmx with propka/pqr data.
You will need a propka file (use the software), a pdb2pqr file (use the web server
with the right forcefield) and a pdb file (that has been handled appropriately - 
that means putting the different chains together and reordering). 


Usage: somethng like this
./pka2gmx.py -f1 ordered.pka -f2 ../build/NarGH.pqr -c ordered.pdb -o special.sh
""")

# Named arguments
parser.add_argument("-f1", "--file1", help="The name of the input propka file", required=True)
parser.add_argument("-f2", "--file2", help="The name of the input pdb2pqr file", required=True)
parser.add_argument("-c", "--pdb", help="The name of the input pdb file", required=True)
parser.add_argument("-o", "--output", help="The name of the output file, which is a bash script", required=True)

args = parser.parse_args()

######################## Functions and miscellaneous ########################

# Which forcefield ? 1 is the first forcefield of the list
ff = 1

# Input
input_file1 = args.file1
input_file2 = args.file2
inpdb = args.pdb
outsh = args.output

# Reference values
pka_dict = {"ARG" : 12.50,
"LYS" : 10.50,
"TYR" : 10.00,
"CYS" : 9.00,
"HIS" : 6.50,
"GLU" : 4.50,
"ASP" : 3.80}

# Two classes to handle the pka values
class Pka_mol:
    """ Wrapper class for the pkas of the molecule """

    def __init__(self, pka=None, pqr=None, verbose=False, **kwargs):
        """ the __init___ """

        # A few default (and empty) attributes
        self.title = 'Friandise'
        self.residues = []
        self.name = None
        self.id = 0
        self.verbose = verbose
        # Converts all the arguments called from AtomHandler(a=A, b=B), passed into kwargs {'a': 'A', 'b': 'B'} into attributes of the class
        # Calling class.a will return A
        for key, val in kwargs.items():
            setattr(self, key, val)

        if pka!=None:
            self.read_pka(pka)
        if pqr!=None:
            self.read_pqr(pqr)

    def read_pka(self, pka_name):
        """ Reads the pka file - only the summary """

        with open(pka_name) as openfileobject:

            # Switch which marks the beginning of the summary
            switch = False

            for line in openfileobject:
                if switch != False:
                    if line.startswith("-------------------------") == True:
                        break
                    a = Pka_res().read_pka_line(line)
                    if a.race == "HIS": continue
                    self.residues.append(a)
                else:
                # The start of the summary
                    if line == "       Group      pKa  model-pKa   ligand atom-type\n":
                        switch = True

        return self

    def read_pqr(self, pqr_name):
        """ Reads the pqr file - only the histidins """

        with open(pqr_name) as openfileobject:
            for line in openfileobject:
                if line[17:21].strip() in ["HID", "HIE", "HIP"]:
                    if int(line[22:27]) not in [x.number for x in self.residues]:
                        a = Pka_res().read_pqr_line(line)
                        self.residues.append(a)
        return self

    def get_pka(self, number):
        """ Find a residue with its number """

        for residue in self.residues:
            if self.verbose == True:
                print "Checking residue {:s}{:s} ...".format(residue.race, residue.number)
            if residue.number == number:
                return residue.pka

        print "Error: couldn't find residue {:s}. Exiting now ..".format(number)
        sys.exit()

    def get_list(self, race):
        """ Get a list of residues """

        ll = []

        for residue in self.residues:
            if residue.race == race:
                ll.append(residue)

        return ll

class Pka_res(Pka_mol):

    def __init__(self, **kwargs):
        self.race = None
        self.number = None
        self.pka = None
        self.type = None
        for key, val in kwargs.items():
            setattr(self, key, val)

    def read_pka_line(self, line):
        """ propka line to fill the Pka_res class, the pkas """

        self.race = line[3:6]
        self.number = int(line[6:10])
        self.pka = float(line[16:21])

        return self

    def read_pqr_line(self, line):
        """ PQR line to fill the Pka_res class, the his types """

        self.type = line[17:21].strip()
        self.number = int(line[22:27])
        self.race = "HIS"

        return self

######################## Main ########################

# Load all the pkas !
all_the_pkas = Pka_mol(pka=input_file1, pqr=input_file2)

# Manufacture the bash script
out = open(outsh, "w")

# Write the bash header
out.write("#!/bin/bash\n\n")

# The beginning of the script
out.write("""cat << EOF | gmx pdb2gmx -f {:s} -o processed.gro -water tip3p -merge all -lys -arg -asp -glu -his
{:d}\n""".format(inpdb, ff))

# Now loop through the residues, one by one, in the order pdb2gmx sees them
for race in ["LYS", "ARG", "ASP", "GLU"]:
    res_list = all_the_pkas.get_list(race)
    for res in res_list:
        if res.pka < 7:
            out.write("0\n")
            #~ print "Residue {:s}{:d}, pka {:f}, compared to 7, which means a 0, unprotonated".format(res.race, res.number, res.pka)
        else:
            out.write("1\n")
            #~ print "Residue {:s}{:d}, pka {:f}, compared to 7, which means a 1, protonated".format(res.race, res.number, res.pka)

# Now histidines ...! For that, use PDB2PQR
his_list = all_the_pkas.get_list("HIS")
for res in his_list:
    if res.type == "HID":
        out.write("0\n")
        print "Residue {:s}{:d}, type {:s}".format(res.race, res.number, res.type)
    elif res.type == "HIE":
        out.write("1\n")
        print "Residue {:s}{:d}, type {:s}".format(res.race, res.number, res.type)
    elif res.type == "HIP":
        out.write("2\n")
        print "Residue {:s}{:d}, type {:s}".format(res.race, res.number, res.type)
    else:
        print "Problem problem, HIS not recognized !"
        print "Residue {:s}{:d}, type {:s}".format(res.race, res.number, res.type)

# Close the file
out.write("EOF")
out.close()








