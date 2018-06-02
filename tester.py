#
# Settings that students might want to adjust are below.
#
# The list TEST specifies which of this assignment's programs(s) to test.  Don't forget
# the .py suffix!
#
TEST = ["phylo.py"]

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

VERSION = "1.25"
TAG_INDICATOR = "#!"

from pathlib import Path
import argparse
import math
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
        'a1': [Program("word-grid.py"), Program("word-search.py")],
        'a2': [Program("pokemon.py")],
        'a3': [Program("rhymes.py", post_process="sort")],
        'a4': [Program("abundance.py", post_process="sort"), Program("biodiversity.py", post_process="sort")],
        'a5': [Program("ngrams.py", post_process="sort"), Program("bball.py", post_process="sort")],
        'a6': [Program("dates.py"), Program("rhymes-oo.py", post_process="sort,uniq")],
        'a7': [Program("battleship.py")],
        'a8': [Program("fake-news.py", post_process="fake_news_sort")],
        'a9': [Program("friends.py", post_process="friends_sort")],
        'a10': [Program("fake-news-ms.py"), Program("street.py")],
        'a11': [Program("huffman.py")],
        'a12': [Program("phylo.py")],
        'ver': [Program("version.py")]
        }

class DiffFile:
    def __init__(self, assignment):
        self._assignment = assignment
        self._file = open("diff.html", "w")
        self._write_file_header()

    def add_message(self, program_fname, test_num, msg):
        self._file.write("<h1>Difference on <code>{0}</code> test {1}</h1><br>".format(program_fname, int(test_num)))
        self._file.write("{}<br><br>".format(msg))


    def add_diff(self, program_fname, test_num, expected_fname, expected_lines, actual_fname, actual_lines, stdin_fname, passed):
        LIMIT_INPUT_FILE_TEXT = 5000
        PASSED_VARIANTS = ["Difference", "Success", "inline-block", "none"]
        self._file.write("""
            <h1 onclick="output_view(this)">{0} on <code>{1}</code> test {2}</h1>
            {3}
            <br>
            <div class="test-display" style="display: {4};">
            <h2>Input: (<code><a href='{5}'>{5}</a></code>)</h2>
            <table class="diff" rules="groups">
            <colgroup></colgroup>
            <tbody>""".format(PASSED_VARIANTS[passed], program_fname, int(test_num), ('<div class="arrow" onclick="output_view(this)"></div>' * passed), PASSED_VARIANTS[passed + 2], stdin_fname))

        test_files = []
        test_file_headers = []
        for line in open(stdin_fname):
            line = line.rstrip()
            if re.match("test-" + self._assignment + r"/.*$", line) and Path(line).is_file():
                test_files.append(line.strip("\n"))
                line = "<a href={0}>{0}</a>".format(line)
                test_file_headers.append(line)
            self._file.write("<tr><td><pre style='margin:0;'>" + line + "</pre>\n")

        self._file.write(""" 
            </tbody>
            </table>
            """)

        for i in range(len(test_files)):
            open_file = open(test_files[i])
            file_text = open_file.read()
            file_len = len(file_text)
            if (file_len > LIMIT_INPUT_FILE_TEXT):
                #
                # truncate at the end of a whole line, if possible
                #
                last_newline = file_text.rfind("\n", 0, LIMIT_INPUT_FILE_TEXT)
                if last_newline >= 0:
                    file_text = file_text[:last_newline+1]
                    discarded = file_len - last_newline - 1
                else:
                    file_text = file_text[:LIMIT_INPUT_FILE_TEXT]
                    discarded = file_len - LIMIT_INPUT_FILE_TEXT

                file_text += "[...{} additional characters not shown...]".format(discarded)

            self._file.write(""" 
            <div style="display: inline-block; position: relative; margin-top: 20px; margin-left: 5%; width: {0}%;"><div style="background-color: white; border:3px solid black; position: relative; height: 30px; width:100%; top:2px; z-index:9; text-align: center; left: 50%; transform: translate(-50%, 0); overflow: hidden;"><span style="position: relative; top: 5px; font-family: Courier; font-weight: 600;">{1}</span></div>
            <textarea spellcheck="false" autocapitalize="off" autocorrect="off" autocomplete="off" style="overflow: auto; background-color: #e0e0e0; position: relative; white-space: pre; left: 50%; transform: translate(-50%, 0); width:97%; height: 200px; box-shadow: inset 0px 2px 5px 5px #888888; z-index:8; top:-20px; outline: none; font-family: Courier; border: none; resize: none; padding-left: 1%; box-sizing: border-box; -webkit-box-sizing: border-box;" readonly>{2}</textarea></div>
            """.format(((95 - (5 * len(test_files))) / len(test_files)), test_file_headers[i], "\n\n\n" + file_text))
            open_file.close()

        self._file.write("""
            <h2>Output:</h2>""")

        htmldiff = difflib.HtmlDiff().make_table(expected_lines, actual_lines, fromdesc=expected_fname, todesc=actual_fname)

        self._file.write(self._add_file_links(htmldiff, expected_fname, actual_fname))

        self._file.write("</div><br><br>")
        
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
                table.diff {font-family:Courier; border:1px solid black; margin-left: 3em}
                .diff_header {background-color:#e0e0e0}
                td.diff_header {text-align:right}
                .diff_next {background-color:#c0c0c0}
                .diff_add {background-color:#aaffaa}
                .diff_chg {background-color:#ffff77}
                .diff_sub {background-color:#ffaaaa}
                h1 { font-size: 1.2em; text-decoration: underline; display: inline-block;}
                h1:hover {cursor: pointer;}
                h2 { font-size: 1.1em; margin-left: 1em }
                pre { margin-left: 3em }
                .notice { color: red; font-size: 2em; text-decoration underline; font-weight: bold }
                .disclaimer { font-size: 1.2em; border: solid 1px; padding: .5em; font-family: sans-serif }
                .arrow {height: 0px; width: 0px; border-top: 10px solid black; border-left: 6px solid transparent; border-right: 6px solid transparent; transform: rotate(270deg); display:inline-block;}
                .arrow:hover {cursor: pointer;}
            </style>
            <script>
            var output_view = function(elem) {
                arrow_elem = elem;
                if (arrow_elem.className != "arrow") {
                    arrow_elem = elem.nextElementSibling;
                    if (arrow_elem.className != "arrow") {
                        return;
                    }
                }
                if (arrow_elem.style.transform != "rotate(0deg)") {
                    arrow_elem.nextElementSibling.nextElementSibling.style.display = "inline-block";
                    arrow_elem.style.transform = "rotate(0deg)"
                } else {
                    arrow_elem.nextElementSibling.nextElementSibling.style.display = "none";
                    arrow_elem.style.transform = "rotate(270deg)"
                }
            }
            </script>
        <body>
            """)
    
    def _write_file_footer(self):        
        self._file.write('<table class="diff" summary="Legends"> <tr> <th colspan="2"> Legends </th> </tr> <tr> <td> <table border="" summary="Colors"> <tr><th> Colors </th> </tr> <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr> <tr><td class="diff_chg">Changed</td> </tr> <tr><td class="diff_sub">Deleted</td> </tr> </table></td> <td> <table border="" summary="Links"> <tr><th colspan="2"> Links </th> </tr> <tr><td>(f)irst change</td> </tr> <tr><td>(n)ext change</td> </tr> <tr><td>(t)op</td> </tr> </table></td> </tr> </table>')

    def note_interrupted(self):
        self._file.write("<p class=notice>NOTE: Tester execution interrupted; not all tests were completed.")

    def finish(self):
        self._write_file_footer()
        disc = get_disclaimer()
        self._file.write("<br><br><div class=disclaimer><b>{}</b> {} <u>{}</u></div>".format(*disc))

        self._file.close()
    
TESTER_URL_ROOT="http://www2.cs.arizona.edu/classes/cs120/spring18/ASSIGNMENTS/"

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

        tags = []
        expected_lines = expected_file.readlines()

        #Check expected output for tag line, create tags if it exists.
        if len(expected_lines) > 0 and expected_lines[0].startswith(TAG_INDICATOR):
            tags = expected_lines[0].lstrip(TAG_INDICATOR + " ").rstrip().split()
            expected_lines = expected_lines[1:]
        
        actual_lines = actual_file.readlines()
        #TODO: Add trailing newline check here
        
        expected_file.close()
        actual_file.close()

        expected_lines = post_process(expected_lines, program_spec.get_post_process())
        actual_lines = post_process(actual_lines, program_spec.get_post_process())

        #Post process based on tags
        expected_lines = post_process(expected_lines, tags)
        actual_lines = post_process(actual_lines, tags)
            
        diff = DIFF_TYPE(expected_lines, actual_lines, fromfile=expected_fname, tofile=actual_fname)
        diff_str = ""
        for line in diff:
            diff_str += line
            
        if len(diff_str) == 0:
            print("PASSED")
            diff_file.add_diff(program_fname, test_num,
                expected_fname, expected_lines, actual_fname, actual_lines, stdin_fname, True)
        else:
            print("FAILED")

            #
            # Special case quick fix for 120.f17 a12: If actual_lines is only missing a final newline,
            # state that.
            if "".join(expected_lines) == "".join(actual_lines) + "\n":
                msg = "NOTE: Your output is identical to the expected output EXCEPT that your output is missing a newline at the very end."
                print(msg)
                diff_file.add_message(program_fname, test_num, msg)
            else:
                show_input(stdin_fname)
                print(diff_str)

                diff_file.add_diff(program_fname, test_num,
                    expected_fname, expected_lines, actual_fname, actual_lines, stdin_fname, False)
                    
                
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
        elif op == "fake_news_sort":
            lines = fake_news_sort(lines)
        elif op == "friends_sort":
            lines = friends_sort(lines)
        else:
            print("\nOops! Tester configuration error: no such operation as '{}'".format(op))
            print("Tell Dr. O'Bagy about this!")
            sys.exit()

    return lines


def fake_news_sort(lines):
    prefix = "File: N: "
    if lines[0].startswith(prefix):
        line = lines[0]
        lines.pop(0)
        lines.insert(0,line[:len(prefix)] + "\n")
        lines.insert(1,line[len(prefix):])

    result = []
    last_count = None
    batch = []
    for line in lines:
        try:
            count = int(line.split()[-1])
        except:
            count = "x"

        #print(line, count, last_count)
        if last_count == None or count == last_count:
            batch.append(line)
        else:
            #print(batch)
            result += sorted(batch)
            batch = [line]

        last_count = count

    result += sorted(batch)

    #print(result)
        
    return result

def friends_sort(lines):
    if len(lines) == 0:
        return lines
    else:
        return [lines[0]] + sorted(lines[1:])

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
    print("os.name: {}, platform: {}, bits: {}".format(os.name, platform.platform(), int(math.log(sys.maxsize,2))+1))
    print()

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

def get_assignment(argv):
    aN_pattern = r'(a\d+)-.*'

    if len(argv) != 0:
        program = Path(argv[0]).name
    else:
        program = ""

    match = re.match(aN_pattern, program)
    if len(argv) == 0 or not match:
        print("Note: Determining assignment based on first program in TEST list...", end="")
        assignment = get_assignment_based_on_tests()
        print("looks like '{}'".format(assignment))
    else:
        assignment = match.groups(0)[0]

    return assignment

def get_assignment_based_on_tests():
    for aname, programs in get_configs().items():
        for testprog in TEST:
            for program in programs:
                if testprog == program.get_name():
                    return aname

    print("\nSorry! I can't figure out which assignment you're trying to test.")
    print("Either the tester must have a name like aN-tester.py or the variable TEST")
    print("in the tester source code (near the top) must specify a known program name.")
    sys.exit(1)

def get_disclaimer():
    return ["NOTE:",
            "This tester gives you an automated way to confirm that your programs are producing the expected output for the examples shown in the assignment specifications, including error cases.",
            "Passing the test cases does not guarantee any particular grade: additional and/or different test cases will be included when grading."
            ]

f=get_assignment_based_on_tests
        
def main():
    print_header()
    assignment = get_assignment(sys.argv)

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

    except KeyboardInterrupt:
        print("Interrupted!")
        diff_file.note_interrupted()

    finally:
        print("\n\n" + " ".join(get_disclaimer()))
        diff_file.finish()

main()

"""
Fix:
    If files only differ by a final newline, diff.html shows no evidence of the difference.
        Look for difference being missing newline in actual
        See https://mail.python.org/pipermail/python-dev/2010-October/104501.html

        Note: This was partially addressed by e3a9ce.
    
    Add an "Update in Progress" message via version.txt?
        Just swap in a new directory?  (why the spaces? -- whm)
            Need a way to test with the new directory
                --exp -- experimental directory
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
