
# -*- coding: utf-8 -*-

import os
import re
import shutil

target_dir = "./data/"


def find(arg_file_path):
    for root, dirs, csvs in os.walk(arg_file_path):
        yield root
        for csv in csvs:
            yield os.path.join(root, csv)


for csvfile in find(target_dir):
    name, ext = os.path.splitext(os.path.basename(csvfile))
    if ext == ".csv":
        status_name = name.split("_")[3]
        status_val = name.split("_")[4]
        status_list = [status_name, status_val]
        status = "_".join(status_list)
        if os.path.isdir(status):
            shutil.copy2(csvfile, status + "/")
        else:
            os.mkdir(status)
            shutil.copy2(csvfile, status + "/")
