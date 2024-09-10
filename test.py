import re
# s = '"52" -> "48"  [ label = "DDG: mid"]'
# # match = re.search(r'"(\d+)"\s+->\s+"(\d+)"\s+\[\s+label\s+=\s+"(\s+)"\]', s)
# match = re.search(r'"(\d+)"\s+->\s+"(\d+)"\s+\[\s+label\s+=\s+"(\w+:\s+\w*)"', s)
# # print(match)
# if match:
#     source, target, data = match.groups()
#     print(data)
# a = {"123": {"fuck": 123}}
# a.update({"456": {"shit": 456}})
# for i, j in a.items():
#     print(i)
#     print(j)
# a.setdefault("123", {}).
# pattern = r"JNINativeMethod\s+\w+_\w+\[[\d\s]*\]\s*=\s*\{(.*\};)"
# s = '''JNINativeMethod methods_MainActivity[] = {
#             {"stringFromJNI", "()Ljava/lang/String;", (void *) stringFromJNI},
#             {"add",           "(II)I",                (void *) add}
#     };'''
# match = re.search(pattern, s)
# first = match.group()
# print(first)
s = "123."
print(s.rfind("-"))

# jv_method_defs = re.findall(pattern, s, re.DOTALL)
# print(jv_method_defs)

# pattern2 = r"\{\"(.*)\",\s*\"(.*)\",\s*\(.*?\)\s*(\w+)\}"
# matches = re.findall(pattern2, jv_method_defs[0])
# for match in matches:
#     print(match)
# print(jv_method_defs[0])
# print(match)
# if match:
#     first, second, third = match.groups()
#     print(first)
#     print(second)
#     print(third)
#           JNIEXPORT jobject JNICALL Java_com_example_string2CStr(JNIEnv env, jstring jstr)