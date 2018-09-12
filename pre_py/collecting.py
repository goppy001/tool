#!/home/hogehoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import os
import glob
import re
import paramiko
import scp

targetdir = "/home/param/work/collecting"
EXCLUSIONWORD = '#'
listfile = "targetfile.txt"
listpath = targetdir + "/" + listfile

openfile = open(listpath, 'r')

for line in openfile:
    info = re.split(" ", line)
    HOSTNAME = info[0]
    HOSTIP   = info[1]
    TARGETPATH = info[2]
    TARGETFILE = re.sub(r'\\', '_', TARGETPATH)
    TARGETDIR  = targetdir + "/" + HOSTNAME + "_" + HOSTIP + "/"
    os.mkdir(TARGETDIR)
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(username=HOSTNAME, port=22, hostname=HOSTIP, password="pass", timeout=10.0, look_for_keys=False)

    scp = scp.SCPClient(ssh.get_transport())
    scp.get(TARGETPATH, TARGETDIR)
    ssh.close()

openfile.close()
