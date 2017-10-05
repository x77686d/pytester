#
# Settings that students might want to adjust are below.
#
# The list TEST specifies which of this assignment's programs(s) to test.  Don't forget
# the .py suffix!
#
TEST = ["ngrams.py"]
#TEST = ["ngrams.py","bball.py"]  # uncomment to test both

#
# If STOP_ON_FIRST_DIFF is True the tester stops after the the first difference is encountered.
#
STOP_ON_FIRST_DIFF = False

import difflib
#
# DIFF_TYPE controls the format of "diffs".  Try swapping the following two assignments with a
# run that produces differences.
#
DIFF_TYPE=difflib.context_diff
DIFF_TYPE=difflib.unified_diff

####### End of commonly adjusted settings for students #######

VERSION = "1.7"

from pathlib import Path
import argparse
import os
import platform
import re
import shutil        
import subprocess
import sys
import urllib.request

global html_file
html_file = None

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
    contents = urllib.request.urlopen(url).read()
    return contents

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
    
def copy_test_file(url, test_dir, fname):
    with urllib.request.urlopen(url + fname) as testurl:
        testfilepath = test_dir / fname
        testfile = testfilepath.open(mode="wb")
        testfile.write(testurl.read())
        testfile.close()

def get_tests(program, assignment):
    result = []
    test_dir = "test-" + assignment
    for input_file in Path(test_dir).glob(program + "-input-*.txt"):
        #print(str(input_file))
        match = re.match(test_dir + r'[/\\].*-input-([0-9]+).txt', str(input_file))
        result.append(match.group(1))

    return sorted(result)

def run_tests(program_spec, assignment):
    global html_file

    program_fname = program_spec.get_name()
    program_basename = program_fname.split(".")[0]

    if not Path(program_fname).is_file():
        print("Oops! I can't find the file '{}'.  Did you use a different name?".format(program_fname))
        sys.exit(1)

    test_dir = "test-" + assignment
    html_fname = "diff-" + assignment + ".html"
    for test_num in get_tests(program_basename, assignment):
        print("\n{}: Running test {}...".format(program_basename, test_num), end="")
        stdin_fname = "{}/{}-input-{}.txt".format(test_dir, program_basename, test_num)
        actual_fname = "{}/{}-actual-{}.txt".format(test_dir, program_basename, test_num)
        stdin = open(stdin_fname,"r")
        actual_file = open(actual_fname,"w")
        rc = subprocess.call([sys.executable, program_fname], stdin=stdin, stdout=actual_file, stderr=subprocess.STDOUT)
        stdin.close()
        actual_file.close()
        expected_fname = "{}/{}-expected-{}.txt".format(test_dir, program_basename, test_num)
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

            show_input(stdin_fname)
            print(diff_str)
            if not html_file:
                html_file = open(html_fname, "w")
                write_html_header(html_file)

            write_diff_header(html_file, program_fname, test_num, stdin_fname)
                        
            htmldiff = difflib.HtmlDiff().make_table(expected_lines, actual_lines, fromdesc=expected_fname, todesc=actual_fname)
            html_file.write(add_file_links(htmldiff, expected_fname, actual_fname))
            html_file.write("<br><br>")
                
            if STOP_ON_FIRST_DIFF:
                break

def write_diff_header(html_file, program, test_num, stdin_fname):
    html_file.write("""
        <h1>Difference on <code>{0}</code> test {1}</h1>
        <h2>Input: (<code><a href='{2}'>{2}</a></code>)</h2>
        <table class="diff" rules="groups">
        <colgroup></colgroup>
        <tbody>""".format(program, int(test_num), stdin_fname))

    for line in open(stdin_fname):
        html_file.write("<tr><td>" + line + "\n")
        
    html_file.write(""" 
        </tbody>
        </table>
        <h2>Diff:</h2>""")
        
            
def print_header():
    print("CSC 120 Tester, version {}".format(VERSION))
    print("Python version:")
    print(sys.version)
    print("os.name: {}, platform: {}".format(os.name, platform.platform()))

def show_input(fname):
    print("Input: (in {})".format(fname))
    try:
        f = open(fname)
        for line in f:
            print("   ", line.rstrip())
        print()
        f.close()
    except Exception as e:
        print(e)
        
def add_file_links(htmldiff, fname1, fname2):
    for fname in [fname1, fname2]:
        htmldiff = htmldiff.replace(fname, "<a href='{0}'>{0}</a>".format(fname))

    return htmldiff

def write_html_header(f):
    f.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>

<head>
    <meta http-equiv="Content-Type"
          content="text/html; charset=utf-8" />
    <title></title>
    <style type="text/css">
        table.diff {font-family:Courier; border:medium; margin-left: 3em}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#aaffaa}
        .diff_chg {background-color:#ffff77}
        .diff_sub {background-color:#ffaaaa}
        h1 { font-size: 1.2em; text-decoration: underline }
        h2 { font-size: 1.1em; margin-left: 1em }
        pre { margin-left: 3em }
    </style>
</head>

<body>
    """)


def write_html_footer(f):
    f.write('<table class="diff" summary="Legends"> <tr> <th colspan="2"> Legends </th> </tr> <tr> <td> <table border="" summary="Colors"> <tr><th> Colors </th> </tr> <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr> <tr><td class="diff_chg">Changed</td> </tr> <tr><td class="diff_sub">Deleted</td> </tr> </table></td> <td> <table border="" summary="Links"> <tr><th colspan="2"> Links </th> </tr> <tr><td>(f)irst change</td> </tr> <tr><td>(n)ext change</td> </tr> <tr><td>(t)op</td> </tr> </table></td> </tr> </table></body></html>')

def main():
    print_header()
    assignment=re.split(r'[/\\]',sys.argv[0])[-1].split("-")[0]  # todo: switch to os-independent path handling

    try:
        configs = get_configs()
        if assignment not in configs:
            print("Oops! Can't figure out assignment number for tester named '{}'".format(sys.argv[0]))
            sys.exit(1)
            
        ensure_test_dir_current(assignment)
        for test_name in TEST:
            found_test = False
            for program in configs[assignment]:
                if program.get_name() == test_name:
                    run_tests(program, assignment)
                    found_test = True
            if not found_test:
                print("Oops! Looks like TEST is incorrect: '{}' is not a program in this assignment."
                    .format(test_name))
                sys.exit(1)
                
    except urllib.error.HTTPError as e:
        print("Oops! HTTPError, url='{}'".format(e.geturl()))
        print(e)
        sys.exit(1)

    except urllib.error.URLError as e:
        print(e)
        print("Are you perhaps off the net?")
        #print(dir(e),e.args,e.reason,e.strerror,e.with_traceback)

    if html_file:
        write_html_footer(html_file)
        html_file.close()

main()

"""
Fix:
    At minimum, write "No differences" to diff-a5.html
    Have a way to link to input files? (could key on string like "test-aN/.txt")
    
Discuss:
    aN naming convention
        aN-tester.py and test-aN directory
    Understanding diffs
    Show test input when there's a diff
    

"""
