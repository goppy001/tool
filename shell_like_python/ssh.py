#!/home/hogehoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import sys,os
import glob
import re
import subprocess
import pexpect
from pathlib import Path

def ssh_connect(user, hostname, password, command):
    FIRST_MESSAGE = "Are you sure you want to continue connecting"
    if password == '-':
        ssh = pexpect.run('ssh %s@%s %s' % (user, hostname, command))
        res = ssh.strip()
        res = res.decode('utf-8')
    else:
        ssh = pexpect.spawn('ssh %s@%s %s' % (user, hostname, command))
        ret = ssh.expect([FIRST_MESSAGE, 'assword:*', pexpect.EOF, pexpect.TIMEOUT])
        if ret == 0:
            ssh.sendline("yes")
            ssh.expect('assword:*')
            ssh.sendline(password)
        if ret == 1:
            ssh.sendline(password)
        ssh.expect(pexpect.EOF)
        res = ssh.before
        res = res.strip()
        res = res.decode('utf-8')
    return res



user =""
hostname = ""
password = ''
cmd =''


ssh = ssh_connect(user, hostname, password, cmd)
print(ssh)