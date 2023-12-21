import pandas as pd
from classifier import classifier
import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import ast

import re

# PROJECT_PATH = ".\\project"
PROJECT_PATH = "./PythonC_Sample"
GITCLONE_URL = "https://github.com/"

def exe_command(command):
    print("command: "+command)
    process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
    result = ""
    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            try:
                result = result + line.decode().strip() + "$#$"
                print(line.decode().strip())
            except Exception as e:
                pass
    exitcode = process.wait()
    return result, process, exitcode

def loadCommitSHA_and_repoName():
    # data1 = pd.read_csv(path + './Cpp+Python_issues_closed.csv')
    # data2 = pd.read_csv(path + './Cpp+Python_issues_open.csv')
    # sha_list1 = list(data1['commit_sha'])
    # sha_list2 = list(data2['commit_sha'])
    # repo_list1 = list(data1['repo_fullname'])
    # repo_list2 = list(data2['repo_fullname'])
    # return sha_list1 + sha_list2, repo_list1+repo_list2:q
    data = pd.read_csv('./tagged_commit.csv')
    sha_list = list(data['commit_sha'])
    repo_list = list(data['repo_fullname'])
    return sha_list, repo_list

def findAllFile(path):
    for root, ds, fs in os.walk(path):
        for f in fs:
            # yield f
            yield os.path.join(root, f)


def downloadProject(git_url,repo_name,sha):
    if not os.path.exists(PROJECT_PATH+"/"+repo_name):
        exe_command("cd " + PROJECT_PATH + " && git clone "+ git_url)
    exe_command("cd " + PROJECT_PATH  + "/" + repo_name + " && git fetch origin "+ sha)
    exe_command("cd " + PROJECT_PATH  + "/" + repo_name + "&& git reset --hard " + sha)

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print("folder create success")
    else:
        print("folder already exist")

def rmdir(path):
    shutil.rmtree(path, onerror=remove_readonly)
    folder = os.path.exists(path)
    if not folder:
        print("folder removed")
    else:
        print("folder remove failed")



def checkProject(path):
# mkdir(PROJECT_PATH)
# sha_list, repo_list = loadCommitSHA_and_repoName()
# with open("inter_project_index.txt", "a+", encoding="utf8", errors="ignore") as f:
    # for i in range(0,len(repo_list)):
        # git_url = GITCLONE_URL + repo_list[i] + ".git"
        # repo_name = repo_list[i].split('/')[1]
        # downloadProject(git_url,repo_name,sha_list[i])
    # repo_name = "c_extension"
    clf = classifier(".c .py .i .pyx")
    clf.creatCPYClassifier()
    # clf.printStates()
    c_func_list = []
    inter_type_list = []
    # for file in findAllFile(PROJECT_PATH+ "/" + repo_name+"/"):
    for file in findAllFile(path):
        #if file == "./tensorflow/tensorflow/lite/python/interpreter.py":
            #import pdb
            #pdb.set_trace()
        is_inter, state = clf.Match(file)
        if is_inter:
            # f.write(str(i)+"-"+repo_name+"-"+str(file)+"\\n")
            # f.write(repo_name + "-" + str(file) + " \n")
            ################################
            # cffi
            ################################
            if state == "10":
                inter_type_list.append("cffi")

            ################################
            # ctypes
            ################################
            if state == "21":
                inter_type_list.append("ctypes")

            ################################
            # cython
            ################################
            if state == "60":
                inter_type_list.append("cython")

            ################################
            # SWIG
            ################################
            if state == "51":
                inter_type_list.append("SWIG")

            ################################
            # C_extension
            ################################
            if state == "41":
                inter_type_list.append("CE")
                with open(file, 'r', encoding="utf8", errors="ignore") as f:
                    file_content = f.read()
                #step1: find the PyMethodDef function
                py_method_def_pattern = r'PyMethodDef\s+\w+\s*\[\s*\]\s*=\s*\{(.*?\};)'
                py_method_defs = re.findall(py_method_def_pattern, file_content, re.DOTALL)
                #step2: find python-c function mapping
                ml_name_pattern = r'\{\s*"([^"]+)"\s*,\s*([^,]+),'
                ml_names = []
                for method_def in py_method_defs:
                    ml_names.extend(re.findall(ml_name_pattern, method_def))

                func_mapping=[]
                for tup in ml_names:
                    func_mapping.append(tup+(file,))

                c_func_list.extend(func_mapping)

            ################################
            # CPython
            ################################
            if state == "31":
                inter_type_list.append("CPY")
    
    #print("c_func_list:",c_func_list)
    #print("inter_type_list:",inter_type_list)
    return c_func_list, inter_type_list

        
