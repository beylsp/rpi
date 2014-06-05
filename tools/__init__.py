#!/usr/bin/env python

from subprocess import Popen
from subprocess import PIPE
from collections import namedtuple

__all__ = ['query_yes_no', 'system', 'EXIT_SUCCESS', 'EXIT_FAILURE']

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

Response = namedtuple('Response', 'returncode value')

def system(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    return Response(p.returncode, out.rstrip())

def query_yes_no(question, default="yes"):
    valid = {"yes":"yes", "y":"yes", "ye":"yes", "no":"no", "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while 1:
        print "%s %s"%(question, prompt),
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            print "Please respond with 'yes' or 'no' (or 'y' or 'n').\n"

