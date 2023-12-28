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
        S0 = State (0, "JNIEXPORT.*JNICALL.*JNIEnv")
        self.AddState(S0)

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
