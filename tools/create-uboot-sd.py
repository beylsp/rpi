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
UENV = 'uEnv.txt'

def ask(question, default=''):
    print question,
    input = raw_input().lower()
    if not input:
        return default
    return input

def create_env():
    DEFAULT_KERNEL_IMG = 'kernel.img'
    ip_addr = ask("Enter Raspberry Pi (fixed) IP: ")
    server_ip = ask("Enter TFTP/NFS Server IP: ")
    nfs_root = ask("Enter NFS absolute root path: ")
    boot_file = ask("Enter kernel boot file (default: '{0}'): ".format(DEFAULT_KERNEL_IMG), 			 DEFAULT_KERNEL_IMG)
    gw_ip = ask("Enter default gateway IP (if any): ")
    mask = ask("Enter network mask: ")
    env = "optargs=quiet\n" + \
          "uenvcmdx=echo Booting the Raspberry Pi from LAN (TFTP)...; " + \
          "env set ipaddr {0}; " + \
          "env set serverip {1}; " + \
          "tfptboot ${{kloadaddr}} /BI/${{bootfile}}; " + \
          "tfptboot ${{fdtaddr}} /BI/${{fdtfile}}; " + \
          "setenv bootargs console=${{console}} ${{optargs}} " + \
                 "root=/dev/nfs rootfstype=nfs nfsroot={2},udp,vers=3 " + \
                 "ip={0}:{1}:{3}:{4}:rpi:eth0:off smsc95xx.turbo_mode=N optargs=quiet; " + \
          "bootm ${{kloadaddr}} - ${{fdtaddr}}\n" + \
          "uenvcmd=run uenvcmdx\n"
    write_env(env.format(ip_addr, server_ip, nfs_root, gw_ip, mask))

def write_env(env):
    print "\n%s"%env
    path = os.path.join(UBOOT_DIR, UENV)
    answer = query_yes_no("Do you want to write this environment to '{0}'? ".format(path))
    if answer == 'no':
        create_env()
    else:
        f = open(path, 'w')
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

