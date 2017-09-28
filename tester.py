

from pathlib import Path
import difflib
import os
import re
import subprocess
import sys
import urllib.request
import argparse
import shutil        

class Program:
    def __init__(self, name, sort=False):
        self._name = name
        self._sort = sort

    def get_name(self):
        return self._name;
        
    def get_sort(self):
        return self._sort;

def get_configs():
    return {
        'a3': [Program("rhymes.py")],
        'a4': [Program("abundance.py"), Program("biodiversity.py")],
        'a5': [Program("ngrams.py", sort=True), Program("bball.py", sort=True)],
        'ver': [Program("version.py")]
        }

#
# Swap these to get a unified diff
DIFF_TYPE=difflib.unified_diff
DIFF_TYPE=difflib.context_diff

TESTER_URL_ROOT="http://www2.cs.arizona.edu/~whm/120/"

def print_dot():
    print(".", end="")
    sys.stdout.flush()

def ensure_test_dir_current(assignment):
    """Build the test directory, if needed.
        Cases:
            Doesn't exist: make directory and populate it
            Exists: do nothing
            Exists but is a file: tell the user
    """

    test_dir = Path("test-" + assignment)
    assignment_url = TESTER_URL_ROOT + assignment + "/"
    
    if test_dir.exists() and not test_dir.is_dir():
        print("""Oops!  The tester needs to create a directory named '{0}' but you've got a file (or something else) named '{0}'.  Remove it or rename it and run me again.""".format(test_dir))
        sys.exit(1)

    if test_dir.is_dir() and test_dir_current(test_dir, assignment_url):
        #print("up to date!")
        return
    else:
        build_test_directory(test_dir, assignment_url)

def test_dir_current(test_dir, assignment_url):
    try:
        my_version = (test_dir / "version.txt").open().read().strip()
    except FileNotFoundError:
        return False

    expected_version = get_remote_file_contents(assignment_url + "version.txt").decode().strip()

    #print("my_version",my_version,"expected_version",expected_version)

    return my_version == expected_version

def get_remote_file_contents(url):
    try:
        contents = urllib.request.urlopen(url).read()
        return contents
    except urllib.error.HTTPError as e:
        print("Oops! HTTPError, url='{}', code='{}', message='{}'".format(e.geturl(),e.getcode(),e.msg))
        sys.exit(1)

def build_test_directory(test_dir, assignment_url):
    print("Building test directory", end="")
    sys.stdout.flush()

    if test_dir.is_dir():
        shutil.rmtree(test_dir.as_posix())
    
    # If test directory exists, remove it.  Then build it.

    try:
        test_dir.mkdir()
    except Exception as e:
        print("Oops!  Tried to create directory '{}' but failed with this:".format(test_dir))
        print(e)
        sys.exit(1)

    try:
        f = urllib.request.urlopen(assignment_url)
        s = f.read()
        #print(s)
        for m in re.finditer(r'>(\w+)-input-([0-9]+)\.txt<',str(s)):
            program = m.group(1)
            testnum = m.group(2)
            for fname in ["{}-{}-{}.txt".format(program, name, testnum) for name in ["input","expected"]]:
                #print(fname)
                copy_test_file(assignment_url, test_dir, fname)
                print_dot()
        f.close()

        f = urllib.request.urlopen(assignment_url + "testfiles.txt")
        for fname in f.readlines():
            fname = fname.decode().strip()
            if len(fname) == 0 or fname[0] == "#":
                continue
            copy_test_file(assignment_url, test_dir, fname)
            print_dot()

        copy_test_file(assignment_url, test_dir, "version.txt")
        print("Done!")
        
    except urllib.error.HTTPError as e:
        print("Oops! HTTPError, url='{}'".format(e.geturl()))
        print(e)
        sys.exit(1)

def copy_test_file(url, test_dir, fname):
    with urllib.request.urlopen(url + fname) as testurl:
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

def get_tests(program, assignment):
    result = []
    test_dir = "test-" + assignment
    for input_file in Path(test_dir).glob(program + "-input-*.txt"):
        #print(str(input_file))
        match = re.match(test_dir + r'[/\\].*-input-([0-9]+).txt', str(input_file))
        result.append(match.group(1))

    return sorted(result)

def run_tests(program_spec, assignment):
    program = program_spec.get_name().split(".")[0]

    test_dir = "test-" + assignment
    for testnum in get_tests(program, assignment):
        print("\n{}: Running test {}...".format(program, testnum), end="")
        stdin_fname = "{}/{}-input-{}.txt".format(test_dir, program, testnum)
        actual_fname = "{}/{}-actual-{}.txt".format(test_dir, program, testnum)
        stdin = open(stdin_fname,"r")
        actual_file = open(actual_fname,"w")
        rc = subprocess.call([sys.executable, program + ".py"], stdin=stdin, stdout=actual_file, stderr=subprocess.STDOUT)
        stdin.close()
        actual_file.close()
        expected_fname = "{}/{}-expected-{}.txt".format(test_dir, program, testnum)
        expected_file = open(expected_fname, "r")
        actual_file = open(actual_fname,"r")
        expected_lines = expected_file.readlines()
        actual_lines = actual_file.readlines()
        expected_file.close()
        actual_file.close()
        if program_spec.get_sort():
            expected_lines = sorted(expected_lines)
            actual_lines = sorted(actual_lines)
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
    print("tester.py, version 1.1")
    print("Python version:")
    print(sys.version)
    assignment=re.split(r'[/\\]',sys.argv[0])[-1].split("-")[0]  # todo: switch to os-independent path handling

    configs = get_configs()
    if assignment not in configs:
        print("Oops! Can't figure out assignment number for tester named '{}'".format(sys.argv[0]))
        sys.exit(1)
        
    ensure_test_dir_current(assignment)
    for program in configs[assignment]:
        run_tests(program, assignment)

main()
