#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, subprocess
from argparse import ArgumentParser

"""
Will clean the topology that uses the iron sulfur clusters from
Smith, D. M. A., Xiong, Y., Straatsma, T. P., Rosso, K. M. & Squier, T. C. Force-Field Development and Molecular Dynamics of [NiFe] Hydrogenase. J. Chem. Theory Comput. 8, 2103–2114 (2012)
The topology needs to be cleaned because the dihedrals within the clusters aren't modeled (nor needed)
Usage: ./clean_topology.py -f topol.top -n F4O_F3O_FHO
"""

######################## Parsing stuff ########################

parser = ArgumentParser(description=""" Will clean the topology that uses the iron sulfur clusters from
Smith, D. M. A., Xiong, Y., Straatsma, T. P., Rosso, K. M. & Squier, T. C. Force-Field Development and Molecular Dynamics of [NiFe] Hydrogenase. J. Chem. Theory Comput. 8, 2103–2114 (2012)
The topology needs to be cleaned because the dihedrals within the clusters aren't modeled (nor needed)""")

# Named arguments
parser.add_argument("-f", "--file", help="The name of the input topology, usually topol.top", required=True)
parser.add_argument("-n", "--names", help="The resnames of the clusters, separated by an underscore _", required=True)

args = parser.parse_args()

######################## Functions and miscellaneous ########################

# Input and output
input_file = args.file
names = args.names.split("_")

print "Cluster resnames are %s, if this is not correct remember to separate the different names by an underscore and retry\n" % " ".join(names)

# A list of the atom numbers of each cluster
clusters = []

# Two switches to know where we are in the topology
atoms = False
dihedrals = False

# One small count to know how many dihedrals are in the selection
dih_count = 0

######################## Main ########################

if __name__ == '__main__':

    # Opening the outfile
    out = open("topol_clean.top", "w")

    # Loop
    with open(input_file, "r") as openfileobject:
        for line in openfileobject:

            # comment is the first character of the line
            comment = line[0]

            if comment == ";" or comment == "\n" or comment == "#":
                # That's a comment, an empty line or an include. Just write the line
                out.write(line)
                # And go to the next line
                continue
                # It works

            # Every line should have at least 3 words by now, so split it
            lline = line.split()
            # If the lline is too short, write out and continue
            if len(lline) <= 1:
                out.write(line)
                continue

            # To know where we are within the topology - and write and go to the next line
            if lline[1] == "atoms":
                atoms = True
                out.write(line)
                continue
            if lline[1] == "bonds":
                atoms = False
            if lline[1] == "dihedrals":
                dihedrals = True
                out.write(line)
                continue
            if lline[1] == "position_restraints":
                dihedrals = False

            # Treat the topology
            if atoms == True:
                # Find the atoms to watch out for
                if lline[3] in names:
                    # Append the atom number to the residue
                    clusters.append(lline[0])
            elif dihedrals == True:
                # Do stuff and especially remove the bad dihedrals
                for atom in clusters:
                    if atom in lline:
                        dih_count += 1
                if dih_count == 1 or dih_count == 4:
                    # Don't write this line
                    dih_count = 0
                    continue
                elif dih_count > 4:
                    # there's a problem
                    print "OOPPS"
                else:
                    # That's ok, just pass
                    dih_count = 0
                    pass

            # The rest of the file - surprise ! Write the line
            out.write(line)





















