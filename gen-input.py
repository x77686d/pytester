#
# Generate input files
#   cb | egrep "File:|N:" | xfield 2 | py3 gen-input.py a8 fake-news fl
#
# Assignment 9:
#   cb | egrep "Input file:|Name .:" | xfield 3 > std-cases
#   cat std-cases extra-cases error-cases | py3 gen-input.py a9 friends fll
#   scp test-a9/friends-[ie]* lec:www120a/assg09/tester/.
#   lec chmod 664 www120a/assg09/tester/*
#   (cd test-a9; rename -f s/actual/expected/ friends-actual-*)
#   scp test-a9/friends-* lec:www120a/assg09/tester/.
#
# Assignment 11:
#   put text of https://www2.cs.arizona.edu/classes/cs120/fall17/ASSIGNMENTS/assg11/street-examples.html on clipboard
#   cb | grep Street: | sed 's/Street: //' > std-cases
#   Added cases from https://www2.cs.arizona.edu/classes/cs120/fall17/ASSIGNMENTS/assg11/street.html  to std-cases
#   < std-cases py3 ~/120/tester/gen-input.py a11 street l
#   (cd test-a11; rename -f s/actual/expected/ street-actual-*)
#   scp test-a11/street-[ie]* lec:www120a/assg11/tester/.
#   lec chmod 664 www120a/assg11/tester/*
#
# Assignment 12:
#   Edited https://piazza.com/class/j6bfy03k6bf5bb?cid=687 down to piazza-cases.txt
#   Wrote gen-huffman-nn.py
"""
   py3 gen-huffman-nn.py  < piazza-cases.txt
   (cd test-a12; ls huffman.??) | py3 ~/120/tester/gen-input.py a12 huffman f
   py3 a12-tester.py
   (cd test-a12; rename -f s/actual/expected/ huffman-actual-*)
   scp test-a12/{huffman-[ie]*,huffman.*} $(cat www)/assg12/tester
   lec chmod 664 www-120-hidden/assg12/tester/*
"""
#
import sys
def main():
    args = sys.argv[1:]
    if len(args) != 3:
        print("Usage: aN PROGRAM-NAME LINE-DESCRIPTORS")
        print("   LINE-DESCRIPTORS -- f: input file (prepend 'test-aN/'), l: input line -- unchanged")
    test_num = 0
    line_num = 1
    file = None
    assignment, program_name, descriptors = args
    program_name = program_name.split(".")[0]
    while True:
        line = sys.stdin.readline()
        if line == "":
            break

        if line[0] == "#":
            continue

        if (line_num - 1) % len(descriptors) == 0:
            print("line_num", line_num, "-- opening file")
            if file:
                file.close()
            test_num += 1
            file = open("test-{}/{}-input-{:02d}.txt".format(assignment, program_name, test_num),"w")
            open("test-{}/{}-expected-{:02d}.txt".format(assignment, program_name, test_num),"w").close()
        
        descriptor = descriptors[(line_num-1) % len(descriptors)]
        print("desc",descriptor)

        if descriptor == "f":
            file.write("test-" + assignment + "/" + line)
        elif descriptor == "l":
            file.write(line)

        line_num += 1
        
    file.close()

main()
