import subprocess
import sys

def main():
    print(sys.version)
    infile = open("in.1","r")
    out = open("out.1","w")
    rc = subprocess.call(["python3","test_seq.py"], stdin=infile, stdout=out, stderr=subprocess.STDOUT)
    print("rc =", rc)   

main()
