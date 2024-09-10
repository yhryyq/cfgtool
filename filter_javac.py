import pandas as pd
from classifier_javac import classifier
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

def find_nth_rindex(text, sub, n):
    current_pos = len(text)
    for _ in range(n + 1):
        current_pos = text.rfind(sub, 0, current_pos)
    return current_pos

def checkProject(path):
# mkdir(PROJECT_PATH)
# sha_list, repo_list = loadCommitSHA_and_repoName()
# with open("inter_project_index.txt", "a+", encoding="utf8", errors="ignore") as f:
    # for i in range(0,len(repo_list)):
        # git_url = GITCLONE_URL + repo_list[i] + ".git"
        # repo_name = repo_list[i].split('/')[1]
        # downloadProject(git_url,repo_name,sha_list[i])
    # repo_name = "c_extension"
    clf = classifier(".c .h")
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
            ################################
            # JNI
            ################################
            if state == "0":
                inter_type_list.append("JNI")
                with open(file, 'r', encoding="utf8", errors="ignore") as f:
                    file_content = f.read()
                #step1: find the PyMethodDef function
                #pattern = r"JNIEXPORT\s+\w+\s+JNICALL\s+(Java_[\w_]+)_(\w+)\(JNIEnv\s+\*\w+, jobject\s+\w+"
                #pattern = r"JNIEXPORT\s+\w+\s+JNICALL\s+(Java_[\w_]+)_([\w_]+)\(JNIEnv\s+\*\w+, jobject\s+\w+"
                #pattern = r"JNIEXPORT\s+\w+\s+JNICALL\s+(Java_[\w_]+)_([\w_]+)"
                # 可能还需要区分动态绑定和静态绑定，动态绑定主要是RegisterNatives函数中得JNINativeMethod结构体中进行绑定，原理与CPython类似
                # pattern = r"JNIEXPORT\s+\w+\s+JNICALL\s+(Java_[\w_]+)_(_[\w_]+)"
                # 静态绑定
                pattern = r"JNIEXPORT\s+\w+\s+JNICALL\s+(Java_[\w_]+)_([\w_]+)"

            
                matches = re.finditer(pattern, file_content, re.DOTALL)

                func_mapping=[]
                for match in matches:
                    full_name = match.group(1) + "_" + match.group(2)
                    name1 = match.group(1)
                    name1 = name1[name1.index("_") + 1:].replace("_", "-") + ":" + match.group(2)
                    
                    ori_full_name = full_name
                    # delete __[para]
                    index = full_name.rfind("__")
                    if index != -1:
                        full_name = full_name[:index]
                    
                    #handle _1 in function name
                    count_under = full_name.count("_1")
                    full_name = full_name.replace("_1","_")


                    
                    # index = find_nth_rindex(full_name, '_', count_under)
                    # func_name = full_name[index + 1:]
                    func_name = name1


                    #underscore_positions = [pos for pos, char in enumerate(full_name) if char == '_']
                    #print(len(underscore_positions))                   
                    #if len(underscore_positions) <= 2:
                    func_mapping.append((func_name,file[file.rfind("/") + 1:file.index(".")] + ":" + ori_full_name,file))
                    #else:
                        #for pos in underscore_positions[1:]:
                            #first_part = full_name[:pos]
                            #second_part = full_name[pos + 1:]
                            #print(second_part)
                            #func_mapping.append((second_part,full_name,file))

                # 动态绑定
                pattern = r"JNINativeMethod\s+\w+_\w+\[[\d\s]*\]\s+=\s+\{(.*?\};)"
                jv_method_defs = re.findall(pattern, file_content, re.DOTALL)

                if len(jv_method_defs) != 0:
                    pattern2 = r"\{\"(.*)\",\s*\"(.*)\",\s*\(.*?\)\s*(\w+)\}"
                    matches = re.findall(pattern2, jv_method_defs[0])
                    for match in matches:
                        func_mapping.append((matches[0], matches[2], file))


                c_func_list.extend(func_mapping)

    
    #print("c_func_list:",c_func_list)
    #print("inter_type_list:",inter_type_list)
    return c_func_list, inter_type_list

        
