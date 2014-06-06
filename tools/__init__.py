#!/usr/bin/env python
import os
import sys

from subprocess import Popen
from subprocess import PIPE
from collections import namedtuple

__all__ = ['EXIT_SUCCESS', 'EXIT_FAILURE', 'init', 'system', 'query_yes_no']

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

Response = namedtuple('Response', 'returncode value')

def init():
    check_os()
    sudo()
    check_system()

def check_os():
    # only posix supported
    if os.name != 'posix':
        print "This script only supports posix OS family"
        sys.exit(EXIT_FAILURE)

def sudo():
    # check if root with geteuid and re-launch as sudo if not
    if os.geteuid() != 0:
        SUDO = "sudo"
        try:
            os.execvp(SUDO, [SUDO] + sys.argv)
        except OSError as e:
            print "OS Error(%s): %s"%(e.errno, e.strerror)
            sys.exit(EXIT_FAILURE)

def check_system():
    # check if all necessary system utilities are installed
    requirements=["which", "clear", "parted", "grep", "umount", "mount", "cut", "unzip", "dd"]
    missing = []
    for requirement in requirements:
        response = system("which " + requirement)
        if response.returncode != 0:
            missing.append(requirement)
    if missing:
        print "Error: your operating system does not include all the necessary utilities to continue."
        print "Missing utilities: " + ' '.join(missing)
        print "Please install them."
        sys.exit(EXIT_FAILURE)

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

