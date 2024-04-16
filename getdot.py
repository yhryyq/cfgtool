import re
import os
import keyword

def read_dot_files(folder_path):
    funcs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".dot"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if len(lines) > 5:
                    function_name = extract_function_name(lines[0]) 
                    if is_valid_function_name(function_name):
                        line_flows, callsites, node_code, return_lines = process_dot_file(lines, filename)
                        funcs.append([filename, function_name, line_flows, callsites, node_code, return_lines])
                    else:
                        continue
    return funcs

def process_dot_file(lines, filename):
    function_name = extract_function_name(lines[0])
    node_info, callsites, node_code, return_lines, method_returns = extract_node_info(lines)
    control_flows = extract_control_flows(lines,method_returns)
    line_flows = reconstruct_line_flows(node_info, control_flows)
    #print(f"Function: {function_name}, Line Flows: {line_flows}")
    #print(f"Callsites: {callsites}")
    #print(f"Node Code: {node_code}")
    #print(f"Return Lines: {return_lines}")
    return line_flows, callsites, node_code, return_lines

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
    return_lines = set()
    record = ""
    sign1 = 0
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
            if callsite:
                callsites.setdefault(int(line_number), []).append(callsite)
            return_line = is_return_line(node_label)
            if return_line:
                return_lines.add(int(line_number))
            method_return = is_method_return(node_label)
            if method_return:
                method_returns.append(int(node_id))
    return node_info, callsites, node_code, return_lines, method_returns

def is_return_line(label):
    return re.match(r'^RETURN,', label) is not None

def is_callsite(label):
    first_part = label.split(',')[0].strip()
    return first_part if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', first_part) and not first_part.isupper() else None

def is_method_return(label):
    return re.match(r'^METHOD_RETURN,', label) is not None

def extract_control_flows(lines,return_node_id):
    control_flows = []
    for line in lines:
        match = re.search(r'"(\d+)"\s+->\s+"(\d+)"', line)
        if match:
            source, target = match.groups()
            if int(target) not in return_node_id:
                control_flows.append((source, target))
    return control_flows

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

#folder_path = './outdir'
#read_dot_files(folder_path)

