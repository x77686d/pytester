"""
"""

from pathlib import Path
import difflib
import os
import re
import subprocess
import sys
import urllib.request
import argparse
        

CONFIG={
    'a3': ["rhymes.py"],
    'a4': ["abundance.py", "biodiversity.py"]
    }

DIFF_TYPE=difflib.unified_diff
DIFF_TYPE=difflib.context_diff

TEST_FILE_URL="http://www2.cs.arizona.edu/~whm/120/"

def find_python():
    """Return a command that will run Python 3"""
    python_commands = ["python3","python"]

    #
    # Only look for pythonw if running on Windows
    #
    if os.name == "nt":
        python_commands.insert(0, "pythonw")
        
    for command in python_commands:
        try:
            rc = subprocess.call([command, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if rc == 0:
                return command
        except:
            pass

    print("Oops! Can't figure out how to run Python 3!")

def print_dot():
    print(".", end="")
    sys.stdout.flush()


def build_test_dir(url):
    """Build the test directory, if needed.
        Cases:
            Doesn't exist: make directory and populate it
            Exists: do nothing
            Exists but is a file: tell the user
    """
    test_dir = Path("test")
    if test_dir.is_dir():
        return

    if test_dir.is_file():
        print("""Oops!  The tester needs to create a directory named 'test'
but you've got a file named 'test'.  Remove it and run me again.""")
        sys.exit(1)

    print("Building test directory", end="")
    sys.stdout.flush()
    try:
        try:
            test_dir.mkdir()
        except Exception as e:
            print("Oops!  Tried to create directory 'test' but failed with this:")
            print(e)
            sys.exit(1)
        
        with urllib.request.urlopen(url) as f:
            s = f.read()
            #print(s)
            for m in re.finditer(r'>(\w+)-input-([0-9]+)\.txt<',str(s)):
                program = m.group(1)
                testnum = m.group(2)
                for fname in ["{}-{}-{}.txt".format(program, name, testnum) for name in ["input","expected"]]:
                    #print(fname)
                    copy_test_file(url, test_dir, fname)
                    print_dot()

        with urllib.request.urlopen(url + "/" + "testfiles.txt") as f:
            for fname in f.readlines():
                if fname[0] == "#":
                    continue
                copy_test_file(url, test_dir, fname.decode().strip())
                print_dot()
    
        print("Done!")
    except urllib.error.HTTPError as e:
        print("Oops! HTTPError, url='{}', code='{}', message='{}'".format(e.geturl(),e.getcode(),e.msg))

def copy_test_file(url, test_dir, fname):
    with urllib.request.urlopen(url + "/" + fname) as testurl:
        testfilepath = test_dir / fname
        testfile = testfilepath.open(mode="wb")
        testfile.write(testurl.read())
        testfile.close()



def show_file(fname):
    print("----- Contents of file '{}' -----".format(fname))
    try:
        f = open(fname, "r")
        print(f.read(), end="")
        f.close()
    except Exception as e:
        print(e)

def get_tests(program):
    result = []
    for input_file in Path("test").glob(program + "-input-*.txt"):
        #print(str(input_file))
        match = re.match(r'test[/\\].*-input-([0-9]+).txt', str(input_file))
        result.append(match.group(1))

    return sorted(result)

def run_tests(program, python_command):
    for testnum in get_tests(program):
        print("\n{}: Running test {}...".format(program, testnum), end="")
        stdin_fname = "test/{}-input-{}.txt".format(program, testnum)
        actual_fname = "test/{}-actual-{}.txt".format(program, testnum)
        stdin = open(stdin_fname,"r")
        actual_file = open(actual_fname,"w")
        rc = subprocess.call([python_command, program + ".py"], stdin=stdin, stdout=actual_file, stderr=subprocess.STDOUT)
        stdin.close()
        actual_file.close()
        expected_fname = "test/{}-expected-{}.txt".format(program, testnum)
        expected_file = open(expected_fname, "r")
        actual_file = open(actual_fname,"r")
        expected_lines = expected_file.readlines()
        actual_lines = actual_file.readlines()
        expected_file.close()
        actual_file.close()
        diff = DIFF_TYPE(expected_lines, actual_lines, fromfile=expected_fname, tofile=actual_fname)
        diff_str = ""
        for line in diff:
            diff_str += line
            
        if len(diff_str) == 0:
            print("PASSED")
        else:
            print("FAILED")
            print(diff_str)
        
        
def main():
    assignment=re.split(r'[/\\]',sys.argv[0])[-1].split("-")[0]  # todo: switch to os-independent path handling

    if assignment not in CONFIG:
        print("Oops! Can't figure out assignment number for tester named '{}'".format(sys.argv[0]))
        sys.exit(1)
        
    build_test_dir(TEST_FILE_URL + assignment)
    python_command = find_python()
    for program in CONFIG[assignment]:
        program = program.split(".")[0]
        run_tests(program, python_command)

main()
