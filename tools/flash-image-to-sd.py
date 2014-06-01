#!/usr/bin/env python
###############################################################################
#
# Script to flash the latest Raspbian image (Debian Linux distribution for 
# Raspberry Pi) onto an SD card.
#
################################################################################
import os
import sys
import urllib2
import urlparse

from subprocess import Popen
from subprocess import PIPE
from collections import namedtuple
from getopt import getopt
from getopt import GetoptError

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

def unmount(drive):
    print "\nUnmounting all partitions..."
    # check if partitions are mounted; if so, unmount
    if system("mount | grep %s"%drive).returncode == 0:
	exitcode = system("umount `mount | grep %s | cut -f1 -d ' '`"%drive).returncode
    else:
	# partitions were not mounted; must pass error check
	exitcode = 0
    if exitcode != 0:
        print 'Error: the drive %s could not be unmounted, exiting...'%drive
        sys.exit(EXIT_FAILURE)

def image_device(drive, imagefile):
    unmount(drive)
    # use the system's built in imaging and extraction facilities
    print "\nPlease wait while the Raspbian image is installed to your SD card..."
    print "This may take some time and no progress will be reported until it has finished."
    name, extension = os.path.splitext(imagefile)
    if extension == '.zip':
        # extract zip file to pipe
        r = system("unzip -p %s | dd of=%s bs=1M"%(imagefile, drive))
    elif extension == '.img':
        r = system("dd if=%s of=%s bs=1M"%(imagefile, drive))
    else:
        print "Bad image file type: %s"%imagefile
        sys.exit(EXIT_FAILURE)
    if r.returncode:
        print "Error extracting image: %s"%r.value
        sys.exit(EXIT_FAILURE)
    # flush the write cache
    r = system("sync")
    if r.returncode:
        print "Error flushing the cache: %s"%r.value
        sys.exit(EXIT_FAILURE)
    print "Installation complete!"

def download(url):
    dl = urllib2.urlopen(url)
    # download and extract?
    url = urlparse.urlparse(dl.geturl())
    _file = os.path.basename(url.path)
    redl = "" # so that redl == "yes" doesn't throw an error
    if os.path.exists(_file):
        redl = query_yes_no("\nIt appears that the latest Raspbian image (%s) has already been downloaded. \nWould you like to re-download it?"%_file, "no")
    if redl == "yes" or not os.path.exists(_file):
        print "Downloading, please be patient..."
        dlFile = open(_file, 'w')
        chunk_read(dl, dlFile, 8192, chunk_report)
        dlFile.close()

    return _file

def list_devices():
    return system('fdisk -l | grep -E "Disk /dev/"').value

def device_input():
    # they must know the risks!
    verified = "no"
    while verified is not "yes":        
        print "\nSelect the 'Disk' you would like the image being flashed to:"
        print list_devices()
        device = raw_input("Enter your choice here (e.g. 'mmcblk0' or 'sdd'): ")
        # Add /dev/ to device if not entered
        if not device.startswith("/dev/"):
            device = "/dev/" + device
        if os.path.exists(device) == True:
            print "\nIt is your own responsibility to ensure there is no data loss!" 
            print "Please backup your system before creating the image."
            cont = query_yes_no("Are you sure you want to install Raspbian to '\033[31m" + device + "\033[0m'?", "no")
            if cont == "no":
                sys.exit(EXIT_FAILURE)
            else:
                verified = "yes"
        else:
            print "Device '%s' doesn't exist"%device
            # and thus we are not 'verified'
            verified = "no"
    return device

def install_raspbian(_file):
    # configure the device to image
    disk = device_input()
    if not _file:
        # download first
        _file = download("http://downloads.raspberrypi.org/raspbian_latest")
    # now we can image
    image_device(disk, _file)
    print "\nRaspbian is now loaded on your SD card.\n"

def welcome():
    text = "----------------------------------\n" + \
           "Welcome to Raspbian SD Card Setup.\n" + \
           "----------------------------------\n" + \
           "Please insert your SD card and press ENTER to continue..."
    raw_input(text)

def usage():
   print "Usage: ./%s [-i|--image file] | [-h|--help]"%os.path.basename(__file__)

###############################################################################
#
# EXECUTION STARTS HERE
#
###############################################################################
if os.name != 'posix':
    print "This script only supports posix OS family"
    sys.exit(EXIT_FAILURE)

# check if root with geteuid and re-launch as sudo if not
if os.geteuid() != 0:
    SUDO = "sudo"
    try:
        os.execvp(SUDO, [SUDO] + sys.argv)
    except OSError as e:
        print "OS Error(%s): %s"%(e.errno, e.strerror)
        sys.exit(EXIT_FAILURE)

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

system("clear")

# parse command-line options and arguments
try:
    image_file = None
    opts, args = getopt(sys.argv[1:], "hi:", ["help", "image"])
    if args:
        usage()
        sys.exit(EXIT_FAILURE)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(EXIT_SUCCESS)
        elif opt in ("-i", "--image"):
            image_file = arg
except GetoptError as e:
    print "Error: %s"%e
    usage()
    sys.exit(EXIT_FAILURE)

# flash the image file
try:
    welcome()
    install_raspbian(image_file)
except KeyboardInterrupt:
    print
    sys.exit(EXIT_FAILURE)