import os
import sys

path = sys.argv[1]

for root, dirs, files in os.walk(path):
    count = 0
    for file in files:
        
        # 去除后缀
        name = file[:file.index(".dot")]
        # name = name[:name.index(":")]
        index_ = len(name)
        if name.find(":") != -1:
            index_ = name.index(":")
        name = name[:index_]
        print(name)

        index__ = name.rfind(".")
        # print(name[:name.rfind(".")])
        # name = name.replace(".", "-")
        if index__ != -1:
            os.rename(path + "/" + file, path + "/" + name[:name.rfind(".")].replace(".", "-") + "_" + str(count) + ".dot")
        else:
            os.rename(path + "/" + file, path + "/" + name.replace(".", "-") + "_" + str(count) + ".dot")
        count = count + 1