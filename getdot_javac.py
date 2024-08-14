import re
import os
import keyword

# 添加DDG信息
def read_dot_files(folder_path, imports_data):
    funcs = []
    avaiable_function = {}

    # 用于记录当前函数是否属于某文件，并加上相应的文件标识符
    for filename in os.listdir(folder_path):
        if filename.endswith(".dot"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if len(lines) > 5:
                    function_name = extract_function_name(lines[0]) 
                    if is_valid_function_name(function_name):
                        line_flows, data_finder, callsites, node_code, return_lines, params, return_type, c_java_mapping_vertexs = process_dot_file(lines, filename)
                        # 找到第二个"_"的位置，然后化简文件名称
                        filename = filename[:filename.index("_", filename.index("_") + 1)]
                        if return_type != "" and not filename.startswith("c_"): # 标识当前函数在该文件被定义或声明
                            avaiable_function.setdefault(filename, set()).add(function_name)
                            function_name = filename[filename.index("_") + 1:] + ":" + function_name
                        
                        # 将文件名和函数名组合，以便后续的识别
                        # 当返回值为ANY的时候，证明该函数并没有在当前文件中定义或声明，所以大概率是引入的
                        funcs.append([filename, function_name, line_flows, callsites, node_code, return_lines, data_finder, params, return_type, c_java_mapping_vertexs])
                    else:
                        continue
    
    # 这里可能还需要对import的部分进行映射，指定import的目标，然后搜索指定的filename并搜索指定函数，有则插入
    for func in funcs:
        if func[0].startswith("c_"):
            continue
        table = avaiable_function[func[0]]
        for key, value_list in func[3].items():
            for i in range(len(value_list)):
                callsite = value_list[i]
                if callsite in table: # 证明当前调用的函数属于文件，所以添加标识
                    filename = func[0]
                    value_list[i] = filename[filename.index("_") + 1:] + ":" + callsite
        
        if func[0][func[0].index("_") + 1:] in imports_data.keys():
            imports = imports_data[func[0][func[0].index("_") + 1:]]
            for im in imports:
                if ("java_" + im in avaiable_function.keys()):
                    for key, value_list in func[3].items():
                        for i in range(len(value_list)):
                            callsite = value_list[i]
                            if callsite in avaiable_function["java_" + im]:
                                value_list[i] = im + ":" + callsite 





    


    return funcs

def process_dot_file(lines, filename):
    function_name = extract_function_name(lines[0])
    node_info, callsites, node_code, return_lines, method_returns, params, return_type, c_java_mapping_vertexs, start_id = extract_node_info(lines)
    control_flows, data_dependence = extract_control_flows(lines,method_returns,start_id)
    line_flows = reconstruct_line_flows(node_info, control_flows)
    data_finder = reconstruct_data_dependence(node_info, data_dependence)
    #print(f"Function: {function_name}, Line Flows: {line_flows}")
    #print(f"Callsites: {callsites}")
    #print(f"Node Code: {node_code}")
    #print(f"Return Lines: {return_lines}")
    return line_flows, data_finder, callsites, node_code, return_lines, params, return_type, c_java_mapping_vertexs

def is_valid_function_name(name):
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return re.match(pattern, name) and not keyword.iskeyword(name)

def extract_function_name(first_line):
    match = re.search(r'digraph\s+"([^"]+)"', first_line)
    return match.group(1) if match else None

def extract_node_info(lines):
    node_info = {}
    callsites = {}
    node_code = {}
    method_returns = []
    params = []
    # record c call java function 
    c_java_mapping_vertexs = []
    return_lines = set()
    return_type = ""
    record = ""
    sign1 = 0
    start_id = -1
    for line in lines:
        if (line[0] == '\"' and line[-2] != ']' and sign1 == 0) or (sign1 == 1):
            if line[-2] == ']':
                record += line[0:-1]
                line = record
                record = ""
                sign1 = 0
            else:
                sign1 = 1
                record += line[0:-1]
                continue
        match = re.search(r'"(\d+)"\s+\[label\s+=\s+<\((.*?)\)<SUB>(\d+)</SUB>>\s*\]', line)
        if match:
            node_id, node_label, line_number = match.groups()
            node_info[node_id] = int(line_number)
            node_code.setdefault(int(line_number), []).append(node_label)
            callsite = is_callsite(node_label)
            parameter = is_parameter(node_label)
            if callsite:
                if "CallObjectMethod" == callsite:
                    c_java_mapping_vertexs.append(node_id)
                callsites.setdefault(int(line_number), []).append(callsite)
                
            return_line = is_return_line(node_label)
            if return_line:
                return_lines.add(int(line_number))
            
            if parameter:
                k = re.search(r'^PARAM,(.*)', node_label).groups()[0]
                params.append(k)
            method_return = is_method_return(node_label)
            if method_return:
                method_returns.append(int(node_id))
                return_type = re.search(r'^METHOD_RETURN,(.*)', node_label).groups()[0]
            method_start = is_method_start(node_label)
            if method_start:
                start_id = int(node_id)
            
            # 可能还需要判断是否为static的类型
    return node_info, callsites, node_code, return_lines, method_returns, params, return_type, c_java_mapping_vertexs, start_id

def is_method_start(label):
    return re.match(r'^METHOD,', label) is not None

def is_return_line(label):
    return re.match(r'^RETURN,', label) is not None

def is_callsite(label):
    first_part = label.split(',')[0].strip()
    return first_part if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', first_part) and not first_part.isupper() else None

def is_method_return(label):
    return re.match(r'^METHOD_RETURN,', label) is not None

def extract_control_flows(lines,return_node_id,start_id):
    control_flows = []
    data_dependence = []
    for line in lines:
        match = re.search(r'"(\d+)"\s+->\s+"(\d+)"\s+\[\s+label\s+=\s+"(\w+:\s+\S*)"', line)
        if match:
            source, target, data = match.groups()
            if int(target) not in return_node_id:
                if data.startswith("DDG") and int(source) != start_id:
                    data_dependence.append((source, target, data))
                elif data.startswith("CFG"):
                    control_flows.append((source, target))
                else:
                    continue
    return control_flows, data_dependence

def is_parameter(label):
    return re.search(r'^PARAM,(.*)', label) is not None

# def extract_data_dependence():
    

def reconstruct_line_flows(node_info, control_flows):
    line_flows = {}
    for source, target in control_flows:
        source_line = node_info.get(source)
        target_line = node_info.get(target)
        if source_line != target_line:
            line_flows.setdefault(source_line, set()).add(target_line)
    
    for line in line_flows:
        line_flows[line] = list(line_flows[line])

    return line_flows


def reconstruct_data_dependence(node_info, data_dependence):
    data_finder = {}
    for source, target, data in data_dependence:
        if source != target:
            data_finder.setdefault(int(target), {}).update({data: int(source)})
    
    return data_finder


#folder_path = './outdir'
#read_dot_files(folder_path)

