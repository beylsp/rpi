#!/usr/bin/env python
###############################################################################
#
# Script to create u-bootable SD card.
#
################################################################################
import os
import sys

from __init__ import *

UBOOT_DIR = os.path.join(os.path.dirname(os.getcwd()), 'u-boot')

def ask(question):
    print question,
    return raw_input().lower()

def create_env():
    ip_addr = ask("Enter Raspberry Pi static IP: ")
    server_ip = ask("Enter TFTP Server IP: ")
    env = "optargs=quiet\n" + \
          "uenvcmdx=echo Booting the Raspberry Pi from LAN (TFTP)...; " + \
          "env set ipaddr {0}; " + \
          "env set serverip {1}; " + \
          "tfptboot ${{kloadaddr}} /BI/${{bootfile}}; " + \
          "tfptboot ${{fdtaddr}} /BI/${{fdtfile}}; " + \
          "setenv bootargs console=${{console}} ${{optargs}} " + \
                 "root=${{}} rootfstype=${{}} optargs=quiet; " + \
          "bootm ${{kloadaddr}} - ${{fdtaddr}}\n" + \
          "uenvcmd=run uenvcmdx\n"
    write_env(env.format(ip_addr, server_ip))

def write_env(env):
    print "\n%s"%env
    answer = query_yes_no("Do you want to write this environment to 'uEnv.txt'? ")
    if answer == 'no':
        create_env()
    else:
        f = open(os.path.join(UBOOT_DIR, 'uEnv.txt'), 'w')
        f.write(env)
        f.close()

###############################################################################
#
# EXECUTION STARTS HERE
#
###############################################################################
try:
    create_env()
except KeyboardInterrupt:
    print
    sys.exit(EXIT_FAILURE)

