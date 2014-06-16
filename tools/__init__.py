#!/usr/bin/env python
import os
import sys
import urllib2
import urlparse

from subprocess import Popen
from subprocess import PIPE
from collections import namedtuple

__all__ = ['EXIT_SUCCESS', 'EXIT_FAILURE', 'ULINE', 'init', 'system', 
           'query_yes_no', 'ask', 'download']

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def ULINE(n):
    return '-'*n

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

def ask(question, default=''):
    print question,
    input = raw_input().lower()
    if not input:
        return default
    return input

def download(url, destination=None):
    if not destination:
        destination = os.getcwd()
    try:
        dl = urllib2.urlopen(url)
        url = urlparse.urlparse(dl.geturl())
        _file = os.path.basename(url.path)
        _abs_file = os.path.join(destination, _file)
        redl = "" # so that redl == "yes" doesn't throw an error
        if os.path.exists(_abs_file):
            redl = query_yes_no("Do you want to download and overwrite {0}? ".format(_file), "no")
        if redl == "yes" or not os.path.exists(_abs_file):
            print "Downloading {0} from {1}, please be patient...".format(_file, url.netloc)
            dlFile = open(_abs_file, 'w')
            chunk_read(dl, dlFile, 8192, chunk_report)
            dlFile.close()
    except urllib2.HTTPError as e:
        print e
        print "HTTP Error(%s): %s"%(e.errno, e.strerror)
        sys.exit(EXIT_FAILURE)

def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    print "Downloaded %0.2f of %0.2f MiB (%0.2f%%)\r"% \
          (float(bytes_so_far)/1048576, float(total_size)/1048576, percent)
    if bytes_so_far >= total_size:
        print "\n"

def chunk_read(response, file, chunk_size, report_hook):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0
    while 1:
        chunk = response.read(chunk_size)
        file.write(chunk)
        bytes_so_far += len(chunk)
        if not chunk:
            break
        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)
    return bytes_so_far

