import re
import os


class State():
    def __init__(self, id, signature, next=None):
        self.id = id
        self.signature = signature
        self.next = []
        if next != None:
            self.next.append(next)


    def AddNext(self, next):
        self.next.append(next)

    def Match(self, String):
        if len(self.signature) == 0:
            return True

        # print ("\tMatchState=>", self.signature, " -> ", String, ":", len (String))
        if re.search(self.signature, String) != None:
            return True
        else:
            return False

class classifier():
    def __init__(self,fileType):
        self.filetype = fileType.split()
        self.States = []

    def creatCPYClassifier(self):
        S10 = State (10, "import cffi|from cffi")
        self.AddState(S10)
        S20 = State (20, "import ctypes|from ctypes")
        S21 = State (21, "cdll|CDLL")
        self.AddState(S20)
        S20.AddNext(S21)
        S30 = State (30, "#include <Python.h>")
        S31 = State (31, "Py_Initialize")
        S41 = State (41, "PyMethodDef")
        self.AddState(S30)
        S30.AddNext(S31)
        S30.AddNext(S41)

    # def printStates(self):
    #     for state in self.States:
    #         print(state.id)

    def AddState(self, state):
        self.States.append(state)

    def Match(self, File):
        if not os.path.exists(File):
            return False, ""

        StateStack = self.States
        if len(StateStack) == 0:
            return False, ""

        Ext = os.path.splitext(File)[-1].lower()
        if Ext not in self.filetype:
            return False, ""
        elif Ext == '.i':
            S51 = State(51, "#define SWIG_FILE_WITH_INIT")
            StateStack.append(S51)
        elif Ext == '.pyx':
            S60 = State(60, "ext is .pyx")
            StateStack.append(S60)
            return True, "60"

        with open(File, "r", encoding="utf8", errors="ignore") as sf:
            for line in sf:
                if len(line) < 4:
                    continue
                for state in StateStack:
                    isMatch = state.Match(line)
                    if isMatch == False:
                        continue

                    if len(state.next) == 0:
                        return True, str(state.id)
                    for next in state.next:
                        StateStack.append(next)
        return False,""
