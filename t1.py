import subprocess
import sys

def find_python():
    """Return a command that will run Python 3"""
    for command in ["python3","python"]:
        rc = subprocess.call([command, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc == 0:
            return command

    print("OOPS! Can't figure out how to run Python 3!")

def show_file(fname):
    print("----- Contents of file '{}' -----".format(fname))
    try:
        f = open(fname, "r")
        print(f.read(), end="")
        f.close()
    except Exception as e:
        print(e)

def main():
    python_command = find_python()
    print(sys.version)
    infile = open("in.1","r")
    out = open("out.1","w")
    rc = subprocess.call([python_command,"test_seq.py"], stdin=infile, stdout=out, stderr=subprocess.STDOUT)
    print("rc =", rc)
    show_file("out.1")

main()
