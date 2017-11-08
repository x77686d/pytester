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
