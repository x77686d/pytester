#
# Settings that students might want to adjust are below.
#
# The list TEST specifies which of this assignment's programs(s) to test.  Don't forget
# the .py suffix!
#
TEST = ["dates.py"]

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

VERSION = "1.10"

from pathlib import Path
import argparse
import os
import platform
import re
import shutil        
import subprocess
import sys
import urllib.request

class Program:
    """
    Instances of this class represent a program that is to be tested
    """
    def __init__(self, name, post_process=None):
        self._name = name
        if post_process:
            self._post_process = post_process.split(",")
        else:
            self._post_process = []

    def get_name(self):
        return self._name
        
    def get_post_process(self):
        """Return list of output post-processing operations, in the user-specified order"""
        return self._post_process

def get_configs():
    return {
        'a3': [Program("rhymes.py")],
        'a4': [Program("abundance.py"), Program("biodiversity.py")],
        'a5': [Program("ngrams.py", post_process="sort"), Program("bball.py", post_process="sort")],
        'a6': [Program("battleship.py"), Program("rhymes-oo.py", post_process="sort,uniq")],
        'a7': [Program("dates.py")],
        'ver': [Program("version.py")]
        }

class DiffFile:
    def __init__(self, assignment):
        self._assignment = assignment
        self._file = open("diff.html", "w")
        self._write_file_header()
        self._had_a_diff = False

    def add_diff(self, program_fname, test_num, expected_fname, expected_lines, actual_fname, actual_lines, stdin_fname):
        LIMIT_INPUT_FILE_TEXT = 5000
        self._had_a_diff = True
        self._file.write("""
            <h1>Difference on <code>{0}</code> test {1}</h1>
            <h2>Input: (<code><a href='{2}'>{2}</a></code>)</h2>
            <table class="diff" rules="groups">
            <colgroup></colgroup>
            <tbody>""".format(program_fname, int(test_num), stdin_fname))

        test_files = []
        test_file_headers = []
        for line in open(stdin_fname):
            line = line.rstrip()
            if re.match("test-" + self._assignment + r"/.*$", line) and Path(line).is_file():
                test_files.append(line.strip("\n"))
                line = "<a href={0}>{0}</a>".format(line)
                test_file_headers.append(line)
            self._file.write("<tr><td>" + line + "\n")

        self._file.write(""" 
            </tbody>
            </table>
            """)

        for i in range(len(test_files)):
            open_file = open(test_files[i])
            file_text = open_file.read()
            if (len(file_text) > LIMIT_INPUT_FILE_TEXT): 
                file_text = file_text[:LIMIT_INPUT_FILE_TEXT] + "..." 
            self._file.write(""" 
            <div style="display: inline-block; position: relative; margin-top: 20px; margin-left: 20px;"><div style="background-color: white; border:3px solid black; position: relative; height: 30px; width:100%; top:2px; z-index:9; text-align: center; left: 50%; transform: translate(-50%, 0);"><span style="position: relative; top: 5px; font-family: Courier; font-weight: 600;">{0}</span></div>
            <textarea spellcheck="false" autocapitalize="off" autocorrect="off" autocomplete="off" style="overflow: scroll; background-color: #e0e0e0; position: relative; white-space: pre; left: 50%; transform: translate(-50%, 0); width:93%; height: 200px; box-shadow: inset 0px 2px 5px 5px #888888; z-index:8; top:-20px; outline: none; font-family: Courier; border: none; resize: none; padding: 3%" readonly>{1}</textarea></div>
            """.format(test_file_headers[i], "\n\n\n" + file_text))
            open_file.close()

        self._file.write("""
            <h2>Diff:</h2>""")

        htmldiff = difflib.HtmlDiff().make_table(expected_lines, actual_lines, fromdesc=expected_fname, todesc=actual_fname)

        self._file.write(self._add_file_links(htmldiff, expected_fname, actual_fname))

        self._file.write("<br><br>")
        
    def close(self):
        self._write_html_footer()
        self._file.close()
            
    def _add_file_links(self, htmldiff, fname1, fname2):
        for fname in [fname1, fname2]:
            htmldiff = htmldiff.replace(fname, "<a href='{0}'>{0}</a>".format(fname))
    
        return htmldiff
    
    def _write_file_header(self):
        self._file.write("""
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
    
    
    def _write_file_footer(self):
        if (self._had_a_diff):
            self._file.write('<table class="diff" summary="Legends"> <tr> <th colspan="2"> Legends </th> </tr> <tr> <td> <table border="" summary="Colors"> <tr><th> Colors </th> </tr> <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr> <tr><td class="diff_chg">Changed</td> </tr> <tr><td class="diff_sub">Deleted</td> </tr> </table></td> <td> <table border="" summary="Links"> <tr><th colspan="2"> Links </th> </tr> <tr><td>(f)irst change</td> </tr> <tr><td>(n)ext change</td> </tr> <tr><td>(t)op</td> </tr> </table></td> </tr> </table>')
        else:
            self._file.write('<h1>No differences!</h1>')
        self._file.write('</body></html>')

    def finish(self):
        self._write_file_footer()
        self._file.close()
    

TESTER_URL_ROOT="http://www2.cs.arizona.edu/classes/cs120/fall17/ASSIGNMENTS/"
#TESTER_URL_ROOT="http://www2.cs.arizona.edu/~whm/120/ASSIGNMENTS/"


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
    assignment_url = TESTER_URL_ROOT + "assg{:02d}".format(int(assignment[1:])) + "/tester/"
    #print(assignment_url)
    
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
    print("Building '{}' directory".format(test_dir), end="")
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
    for m in re.finditer(r'>([-\w]+)-input-([0-9]+)\.txt<',str(s)):
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

def run_tests(program_spec, assignment, diff_file):
    program_fname = program_spec.get_name()
    program_basename = program_fname.split(".")[0]

    #print("fname, basename", program_fname, program_basename)

    if not Path(program_fname).is_file():
        print("Oops! I can't find the file '{}'.  Did you use the right name for your solution?".format(program_fname))
        sys.exit(1)

    test_dir = "test-" + assignment
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

        expected_lines = post_process(expected_lines, program_spec.get_post_process())
        actual_lines = post_process(actual_lines, program_spec.get_post_process())
            
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

            diff_file.add_diff(program_fname, test_num,
                expected_fname, expected_lines, actual_fname, actual_lines, stdin_fname)
                
            if STOP_ON_FIRST_DIFF:
                break

def post_process(lines, operations):
    for op in operations:
        if op == "sort":
            lines = sorted(lines)
        elif op == "uniq":
            lines = uniq(lines)
        elif op == "upper":
            lines = list(map(str.upper, lines))
        elif op == "lower":
            lines = list(map(str.lower, lines))
        else:
            print("\nOops! Tester configuration error: no such operation as '{}'".format(op))
            print("Tell Dr. O'Bagy about this!")
            sys.exit()

    return lines

def uniq(L):
    result = []
    prev = None
    for e in L:
        if e != prev:
            result.append(e)
            prev = e

    return result
            
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
        
def main():
    print_header()
    assignment=re.split(r'[/\\]',sys.argv[0])[-1].split("-")[0]  # todo: switch to os-independent path handling

    diff_file = DiffFile(assignment)
    
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
                    run_tests(program, assignment, diff_file)
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

    diff_file.finish()

main()

"""
Fix:
    Have links and such for no differences cases

    Add an "Update in Progress" message via version.txt?
        Just swap in a new directory?  (why the spaces? -- whm)
            Need a way to test with the new directory
                --exp -- experimental directory

    Warn if name is not of the form "aN-tester".

    Look for empty sys.argv[0] and ask if Wing 101

    Print warning if running in testerx mode
        Add an option for that mode

    Add option to override source file: -s dates.py=dates-whm.py

    Test for git experimentation.

Discuss:
    aN naming convention
        aN-tester.py and test-aN directory
    Understanding diffs
    Show test input when there's a diff
    

"""
