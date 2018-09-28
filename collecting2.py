#!/home/glodia/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import os
import glob
import re
import pexpect
import linecache

#作業用ルートディレクトリが書かれたファイルがあるかチェック
def check_work_dir():
    pwd = os.getcwd()
    file_name = "working_path.txt"
    file_path = pwd + '/' + file_name
    if os.path.isfile(file_path):
        work_path = linecache.getline(file_path, 1)
        work_path = work_path.strip()
    else:
        work_path = pwd
    return work_path

def check_dir_exsist(dir_path):
    if os.path.isdir(dir_path):
        pass
    else:
        os.mkdir(dir_path)
            
pwd = os.getcwd()
LOG_FILE   = 'log.txt'
LIST_FILE  = "config_list.txt"
target_dir = check_work_dir()
result_dir = target_dir + "/result"
list_path  = target_dir + "/" + LIST_FILE
log_path   = target_dir + "/" + LOG_FILE

check_dir_exsist(result_dir)

open_file = open(list_path, 'r')

first_message = "Are you sure you want to continue connecting"

for line in open_file:
    info = re.split(" ", line)
    HOST_NAME   = info[0]
    HOST_IP     = info[1]
    PASSWORD    = info[2]
    TARGET_PATH = info[3]
    OUTPUT_DIR  = result_dir + "/" + HOST_NAME + "_" + HOST_IP
    check_dir_exsist(OUTPUT_DIR)
    if PASSWORD == '-':
        scp = pexpect.spawn('scp  %s@%s:%s %s' % (HOST_NAME, HOST_IP, TARGET_PATH, OUTPUT_DIR))
        scp.expect(pexpect.EOF)
    else:
        scp = pexpect.spawn('scp  %s@%s:%s %s' % (HOST_NAME, HOST_IP, TARGET_PATH, OUTPUT_DIR))
        ret = scp.expect([first_message, 'assword:*', pexpect.EOF, pexpect.TIMEOUT])
        if ret == 0:
            scp.sendline("yes")
            scp.expect('assword:*')
            scp.sendline(PASSWORD)
            scp.expect(pexpect.EOF)
        if ret == 1:
            scp.expect('assword:*')
            scp.sendline(PASSWORD)
            scp.expect(pexpect.EOF)
open_file.close()
