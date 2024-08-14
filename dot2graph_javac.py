from getdot_javac import read_dot_files
from pybgl.graph import DirectedGraph
from collections import namedtuple,deque
from filter_javac import checkProject
# sys.setrecursionlimit(3000)
from tqdm import tqdm
import sys
import os
import pickle

buildinfunc = []
"""
def dfs(graph, start_vertex, vertex_map):
    visited = set()
    stack = deque([start_vertex])

    while stack:
        v = stack.pop()
        if v not in visited:
            visited.add(v)
            for e in graph.out_edges(v):
                target = graph.target(e)
                if target not in visited:
                    stack.append(target)

    # 将访问过的顶点转换为 line_number
    return [line_number for line_number, vertex in vertex_map.items() if vertex in visited]
"""
def dfs(graph, start_vertex, visited=None, global_node_data=None):
    if visited is None:
        visited = set()
    if global_node_data is None:
        global_node_data = {}

    visited.add(start_vertex)
    print(f"当前顶点: {start_vertex}, 行号: {global_node_data[start_vertex].line_number}, 函数名: {global_node_data[start_vertex].function_name}")
    
    for edge in graph.out_edges(start_vertex):
        target = graph.target(edge)
        #if global_node_data[start_vertex].line_number ==19:
            #print(target)
        if target not in visited:
            dfs(graph, target, visited, global_node_data)

def dfs_path(graph, start_vertex,  global_node_data):
    visited = set()  # 用于跟踪已访问的顶点
    stack = [(start_vertex, [start_vertex])]

    while stack:
        current_vertex, path = stack.pop()
        if current_vertex in visited:
            continue  # 如果已访问过此顶点，则跳过
        visited.add(current_vertex)  # 标记当前顶点为已访问
        current_line_number = global_node_data[current_vertex].line_number
        #print(f"current_line_number:{current_line_number}")
        out_edges = list(graph.out_edges(current_vertex))
        if len(out_edges) == 0:
            print("Path:", " -> ".join(str(global_node_data[v].line_number) for v in path))
        else:
            for edge in out_edges:
                target_vertex = graph.target(edge)
                stack.append((target_vertex, path + [target_vertex]))

def dfs_all_paths(graph, start_vertex, visited_edges, path, global_node_data,only_cross=False):
    path.append(start_vertex)  # 将当前顶点添加到路径中

    current_function_name = global_node_data[start_vertex].function_name
    node_info = f"{global_node_data[start_vertex].line_number} ({current_function_name})"
    #print(f"=====current vertex ID: {start_vertex}, line number: {node_info}")

    out_edges = list(graph.out_edges(start_vertex))
    #print(f"out_edges:{out_edges}")
    
    if len(path)>1:
        previous_vertex = path[-2]
        previous_function_name = global_node_data[previous_vertex].function_name
        #if previous_function_name != current_function_name:
            #visited_edges = set()
    else:
        previous_function_name = ""

    #In case re-enter a function when it just return
    for edge in out_edges[:]:
        target_vertex = graph.target(edge)
        target_function_name = global_node_data[target_vertex].function_name
        if current_function_name != previous_function_name and current_function_name != target_function_name and previous_function_name == target_function_name:
            out_edges.remove(edge)
            #break
    #print(f"out_edges1:{out_edges}")

    #other function go first
    other_function_edges = [e for e in out_edges if global_node_data[graph.target(e)].function_name != current_function_name]
    unvisited_other_function_edges = [e for e in other_function_edges if graph.target(e) not in path]

    if unvisited_other_function_edges and len(out_edges) > len(unvisited_other_function_edges):
        out_edges = unvisited_other_function_edges
    #print(f"out_edges3:{out_edges}")
     
    #if return, match the correct return function
    is_return_line = global_node_data[start_vertex].is_return_line
    if is_return_line:
        for v in reversed(path[:-1]):
            if global_node_data[v].function_name != current_function_name:
                out_edges = [e for e in out_edges if graph.target(e) == v]
                break

    if not out_edges:
        if only_cross:
            if check_path(path):
                path_info = "\n -> ".join(f"{global_node_data[v].line_number}({global_node_data[v].file_name}) ({global_node_data[v].function_name})" for v in path)
                func_count = 0
                for v in path:
                    #print(f"callsites:{global_node_data[v].callsites}")
                    if global_node_data[v].callsites != []:
                        func_count += sum(1 for callsit in global_node_data[v].callsites if callsit not in buildinfunc)
                print(f"func_count:{func_count}")
                print(f"len:{len(path)}")
                print("Path:\n", path_info)
                print("====================")
                return
                #with open('paths.txt', 'a') as file:
                    #file.write(path_info + '\n')
        else:
            path_info = "\n -> ".join(f"{global_node_data[v].line_number}({global_node_data[v].file_name}) ({global_node_data[v].function_name})" for v in path)
            print("Path:\n", path_info)
            print("====================")
            #with open('paths.txt', 'a') as file:
                #file.write(path_info + '\n')
    else:
        for edge in out_edges:
            if edge not in visited_edges:
                target_vertex = graph.target(edge)
                target_info = f"{global_node_data[target_vertex].line_number}({global_node_data[target_vertex].file_name}) ({global_node_data[target_vertex].function_name})"
                if is_return_line:
                    filtered_edges = []
                    for edge in visited_edges:
                        source_vertex = graph.source(edge)
                        if (global_node_data[source_vertex].function_name == current_function_name):
                            filtered_edges.append(edge)
                    try:
                        dfs_all_paths(graph, target_vertex, set(filtered_edges), path.copy(), global_node_data,only_cross)
                    except RecursionError:
                        print("RecursionError detected")
                else:
                    try:
                        dfs_all_paths(graph, target_vertex, visited_edges.union({edge}), path.copy(), global_node_data,only_cross)
                    except RecursionError:
                        print("RecursionError detected")

    path.pop()


def dfs_all_paths_backf(graph, start_vertex, visited_edges, path, global_node_data,only_cross=False):
    path.append(start_vertex)  # �~F�~S�~I~M顶�~B�添�~J| �~H�路�~D中

    current_function_name = global_node_data[start_vertex].function_name
    node_info = f"{global_node_data[start_vertex].line_number}({global_node_data[start_vertex].file_name}) ({current_function_name})"
    #print(f"=====current vertex ID: {start_vertex}, line number: {node_info}")

    in_edges = [edge for edge in graph.edges() if graph.target(edge) == start_vertex]
    #in_edges = list(graph.in_edges(start_vertex))
    #print(f"in_edges:{in_edges}")

    if len(path)>1:
        previous_vertex = path[-2]
        previous_function_name = global_node_data[previous_vertex].function_name
        #if previous_function_name != current_function_name:
            #visited_edges = set()
    else:
        previous_function_name = ""
    #In case re-enter a function when it just return
    for edge in in_edges[:]:
        source_vertex = graph.source(edge)
        source_function_name = global_node_data[source_vertex].function_name
        if current_function_name != previous_function_name and current_function_name != source_function_name and previous_function_name == source_function_name:
            in_edges.remove(edge)
            #break
    #print(f"in_edges1:{in_edges}")

    #if start of function, match the correct call function
    start_line_number = global_node_data[start_vertex].line_number
    # find the start line num of function
    min_line_number = min(global_node_data[v].line_number for v in global_node_data if global_node_data[v].function_name == current_function_name)
    is_first_line = start_line_number == min_line_number
    if is_first_line:
        func_name_edges = [global_node_data[graph.source(e)].function_name for e in in_edges]
        for v in reversed(path[:-1]):
            if global_node_data[v].function_name != current_function_name and global_node_data[v].function_name in func_name_edges:
                in_edges = [e for e in in_edges if graph.source(e) == v]
                break
    #print(f"in_edges2:{in_edges}")
    
    #other function go first
    other_function_edges = [e for e in in_edges if global_node_data[graph.source(e)].function_name != current_function_name]
    unvisited_other_function_edges = [e for e in other_function_edges if graph.source(e) not in path]

    if unvisited_other_function_edges and len(in_edges) > len(unvisited_other_function_edges):
        in_edges = unvisited_other_function_edges
    #print(f"final in_edges:{in_edges}")

    if not in_edges:
        if only_cross:
            if check_path_backf(path):
                path_info = "\n -> ".join(f"{global_node_data[v].line_number}({global_node_data[v].file_name}) ({global_node_data[v].function_name})" for v in path)
                func_count = 0
                for v in path:
                    #print(f"callsites:{global_node_data[v].callsites}")
                    if global_node_data[v].callsites != []:
                        func_count += sum(1 for callsit in global_node_data[v].callsites if callsit not in buildinfunc)
                print(f"func_count:{func_count}")
                print(f"len:{len(path)}")
                print("Path\n:", path_info)
                print("====================")
                return
                #with open('paths_4.txt', 'a') as file:
                    #file.write(path_info + '\n')
        else:
            path_info = "\n -> ".join(f"{global_node_data[v].line_number}({global_node_data[v].file_name}) ({global_node_data[v].function_name})" for v in path)
            print("Path:\n", path_info)
            print("====================")
            #with open('paths_4.txt', 'a') as file:
                #file.write(path_info + '\n')
            #print(f"cross:{check_path_backf(path)}")
    else:
        for edge in in_edges:
            if edge not in visited_edges:
                source_vertex = graph.source(edge)
                source_info = f"{global_node_data[source_vertex].line_number}({global_node_data[source_vertex].file_name}) ({global_node_data[source_vertex].function_name})"
                if is_first_line:
                    filtered_edges = []
                    for edge in visited_edges:
                        target_vertex = graph.target(edge)
                        if (global_node_data[target_vertex].function_name == current_function_name):
                            filtered_edges.append(edge)
                    try:
                        dfs_all_paths_backf(graph, source_vertex, set(filtered_edges), path.copy(), global_node_data, only_cross)
                    except RecursionError:
                        print("RecursionError detected")
                else:
                    try:
                        dfs_all_paths_backf(graph, source_vertex, visited_edges.union({edge}), path.copy(), global_node_data,only_cross)
                    except RecursionError:
                        print("RecursionError detected")

    path.pop()


def check_path(path):
    for i in range(len(path) - 1):
        if (path[i], path[i + 1]) in cross_lan_map or (path[i + 1], path[i]) in cross_lan_map:
            return True
    ''' 
    f = open("./APIList.txt")
    apis = f.readlines()
    f.close()
    api_list = []
    for api in apis:
        api=api.split('(')[0]
        api=api.strip('\n')
        if len(api)>1:
            api_list.append(api)
    for v in path:
        for api in api_list:
            if api in global_node_data[v].node_code:
                return True
    '''
    return False


def check_path_backf(path):
    for i in range(len(path) - 1):
        if (path[i+1], path[i]) in cross_lan_map or (path[i], path[i+1]) in cross_lan_map:
            return True
    ''' 
    f = open("./APIList.txt")
    apis = f.readlines()
    f.close()
    api_list = []
    for api in apis:
        api=api.split('(')[0]
        api=api.strip('\n')
        if len(api)>1:
            api_list.append(api)
    for v in path:
        for api in api_list:
            for code in global_node_data[v].node_code:
                if api in code:
                    return True
    '''
    return False

def edge_exists(graph, source_vertex, target_vertex):
    for edge in graph.edges():
        if graph.source(edge) == source_vertex and graph.target(edge) == target_vertex:
            return True
    return False

print("========getting the function info")
NodeData = namedtuple('NodeData', ['line_number', 'line_flows', 'node_code', 'callsites', 'is_return_line', 'function_name', 'file_name', 'params', 'return_type'])

dot_dir=sys.argv[1]
global_graph = DirectedGraph()
cross_lan_map=[]
global_node_data = {}
functions_data = {}
imports_data = {}
#funcs = read_dot_files("./outdir_cpython_pyc")
#funcs: filename, function_name, line_flows, callsites, node_code, return_lines

graph_file_path = f"{dot_dir}/global_graph.pkl"
node_data_file_path = f"{dot_dir}/global_node_data.pkl"
cross_lan_map_path = f"{dot_dir}/cross_lan_map.pkl"
vertex_maps_path = f"{dot_dir}/vertex_maps.pkl"
imports_data_path = f"/home/kali/桌面/cfgtool/cfgtool/cfgtool_new/cfgtool/imports_data"
graph_file_exists = os.path.exists(graph_file_path)
node_data_file_exists = os.path.exists(node_data_file_path)
cross_lan_map_exists = os.path.exists(cross_lan_map_path)
vertex_maps_exists = os.path.exists(vertex_maps_path)

if graph_file_exists and node_data_file_exists and cross_lan_map_exists and vertex_maps_exists:
    with open(graph_file_path, 'rb') as f:
        global_graph = pickle.load(f)

    with open(node_data_file_path, 'rb') as f:
        global_node_data = pickle.load(f)

    with open(cross_lan_map_path, 'rb') as f:
        cross_lan_map = pickle.load(f)

    with open(vertex_maps_path, 'rb') as f:
        vertex_maps = pickle.load(f)
else:
    print(os.getcwd())
    if os.path.exists(imports_data_path):
        for root, dirs, files in os.walk(imports_data_path):
            for file in files:
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    if "import" in line:
                        imports_data.setdefault(file[:file.index(".")], []).append(line[line.index(" ") + 1:len(line) - 1].replace(".", "-"))

    funcs = read_dot_files(dot_dir, imports_data)
    vertex_maps = {}
    graphs = {}
    data_finders = {}

    print("========initializing the graphs")
    for func in funcs:
        g = DirectedGraph()
        keys = func[2].keys()
        values = [item for sublist in func[2].values() for item in sublist]
        function_data = {
            'line_numbers': list(set(keys) | set(values)),
            'line_flows': func[2],
            'node_code': func[4],
            'callsites': func[3],
            'function_name': func[1],
            'return_lines': func[5],
            'file_name': func[0],
            'data_finder': func[6],
            'params': func[7],
            'return_type': func[8]
            # 可能需要记录一下函数的返回类型
        }
        functions_data[function_data['function_name']] = function_data
        local_vertex_map = {}  # Local vertex to line number map
        func_node_data = {}

        for line_number in function_data['line_numbers']:
            v = global_graph.add_vertex()
            return_line = line_number in function_data['return_lines']
            node_data = NodeData(
                line_number=line_number,
                line_flows=function_data['line_flows'].get(line_number, []),
                node_code=function_data['node_code'].get(line_number, ''),
                callsites=function_data['callsites'].get(line_number, []),
                is_return_line=return_line,
                function_name=function_data['function_name'],
                file_name=function_data['file_name'],
                params=function_data['params'],
                return_type=function_data['return_type']
            )
            global_node_data[v] = node_data
            func_node_data[v]= node_data
            local_vertex_map[line_number] = v

        for line_number, flows in function_data['line_flows'].items():
            source_vertex = local_vertex_map[line_number]
            for target_line_number in flows:
                target_vertex = local_vertex_map[target_line_number]
                global_graph.add_edge(source_vertex, target_vertex)

        graphs[function_data['function_name']] = {'graph': g, 'node_data_map': func_node_data, 'vertex_map': local_vertex_map}
        if len(local_vertex_map) != 0:
            vertex_maps[function_data['function_name']] = local_vertex_map
        # 增加数据流查找方式
        data_finders[function_data['function_name']] = function_data['data_finder']

    #with open("vertex_maps.txt", "w") as file:
        #file.write(str(vertex_maps))

    print("========getting javac mapping")
    #get the rule-based mapping
    proj_dir=sys.argv[2]
    cfunc, ctype = checkProject(proj_dir)
    seen = set()
    func_mapping = []
    for item in cfunc:
        key = (item[0], item[1])
        if key not in seen:
            func_mapping.append(item)
            seen.add(key)
    print(func_mapping)

    cross_lan_map=[]
    print("========linking the graphs")
    count = 0
    #for func_name, func_data in tqdm(graphs.items()):
    # 这里需要优先完成Java对C的映射，获取参数的类型，然后再完成C对Java的映射
    for func_name, func_data in graphs.items():
        count+=1
        print(f"{count}/{len(graphs)}")
        local_graph = func_data['graph']
        local_vertex_map = func_data['vertex_map']
        node_data_map = func_data['node_data_map']
        for vertex, node_data in node_data_map.items():
            #print(f"vertex, node_data:{vertex, node_data}")
            if node_data.callsites:
                #print(node_data.callsites)
                for callsite in node_data.callsites:
                    if callsite in vertex_maps:
                        called_vertex_map = vertex_maps[callsite]
                        if called_vertex_map:
                            if called_vertex_map.keys():
                                entry_line_number = min(called_vertex_map.keys())
                            else:
                                print(f"r_callsite:{r_callsite} is empty")
                        else:
                            print(f"func_name:{func_name},callsite:{callsite} cannot found")
                            continue
                        entry_vertex = called_vertex_map[entry_line_number]
                        #print(vertex, entry_vertex)
                        global_graph.add_edge(vertex, entry_vertex)
                        for ret_line, ret_vertex in called_vertex_map.items():
                            if global_node_data[ret_vertex].is_return_line:
                                global_graph.add_edge(ret_vertex, vertex)

                    for mapping in func_mapping:
                        r_callsite=mapping[1].strip(' ')
                        if '(' in r_callsite and ')' in r_callsite:
                            r_callsite = r_callsite.split(')')[-1].strip(' ')
                        print(f"mapping[0]:{mapping[0]},callsite:{callsite},r_callsite:{r_callsite}")
                        print(f"r_callsite in vertex_maps:{r_callsite in vertex_maps}")
                        print(f"vertex_maps:{vertex_maps}")
                        # if mapping[0] == callsite and r_callsite in vertex_maps:
                        if mapping[0] == callsite:
                            print(callsite,r_callsite)
                            try:
                                called_vertex_map = vertex_maps[r_callsite]
                            except:
                                print(f"mapping error,r_callsite:{r_callsite}")
                                continue
                            if called_vertex_map.keys():
                                entry_line_number = min(called_vertex_map.keys())
                            else:
                                print(f"r_callsite:{r_callsite} is empty")
                                continue
                            # 成功映射上后，可以进行参数的替换将C的参数中除了env外的所有参数贴上表示符，
                            # 首先根据被映射的函数名获取函数的node_data，然后修改其返回值和参数
                            for i in range(len(functions_data[r_callsite]["params"])):
                                # 排除第一个参数，第一个一般是env
                                if i == 0:
                                    continue
                                elif i == 1:
                                    # 第二个参数代表当前类的实例对象或类型
                                    arg = functions_data[r_callsite]["params"][i]
                                    target = functions_data[callsite]["function_name"]
                                    argtype = target[target.rfind("-") + 1:target.rfind(":")]
                                    argobj = arg[arg.index(" ") + 1:]
                                    functions_data[r_callsite]["params"][i] = argtype + " " + argobj
                                else:
                                    arg = functions_data[r_callsite]["params"][i]
                                    target = functions_data[callsite]["params"][i - 1]
                                    argtype = target[:target.index(" ")]
                                    argobj = arg[arg.index(" ") + 1:]
                                    functions_data[r_callsite]["params"][i] = argtype + " " + argobj


                            # 替换返回值
                            functions_data[r_callsite]["return_type"] = functions_data[callsite]["return_type"]


                            
                            entry_vertex = called_vertex_map[entry_line_number]
                            #print(vertex, entry_vertex)
                            if not edge_exists(global_graph, vertex, entry_vertex):
                                global_graph.add_edge(vertex, entry_vertex)
                            cross_lan_map.append((vertex, entry_vertex))
                            print(vertex, entry_vertex)
                            for ret_line, ret_vertex in called_vertex_map.items():
                                if global_node_data[ret_vertex].is_return_line:
                                    if not edge_exists(global_graph, ret_vertex, vertex):
                                        global_graph.add_edge(ret_vertex, vertex)
                                    cross_lan_map.append((ret_vertex, vertex))
                            


                            # 还需要考虑import的数据

    print("========linking done")
    """
    for func_name, data in graphs.items():
        graph = data['graph']
        node_data_map = data['node_data_map']
        vertex_map = data['vertex_map']
    
        for v, node_data in node_data_map.items():
            for callsite in node_data.callsites:
                if callsite in graphs:
                    called_func_data = graphs[callsite]
                    called_graph = called_func_data['graph']
                    called_node_data_map = called_func_data['node_data_map']
                    called_vertex_map = called_func_data['vertex_map']
    
                    entry_line_number = min(called_vertex_map.keys())
                    entry_vertex = called_vertex_map[entry_line_number]
    
                    graph.add_edge(v, entry_vertex)
    
                    for rv, rnode_data in called_node_data_map.items():
                        if rnode_data.is_return_line:
                            called_graph.add_edge(rv, v)
    
    """
function_name=sys.argv[3]
start_line_number=int(sys.argv[4])

#scipy
#function_name = "convert_datetime_divisor_to_multiple"
#start_line_number = 975


#cpython
#function_name = "frozenset_new"
#start_line_number = 1007

#py2
#function_name = "sum_of_three_numbers"
#start_line_number = 14

#rec
#function_name = "sum_of_three_numbers"
#start_line_number = 20

#py
#function_name = "sum_of_two_numbers"
#start_line_number = 2

#pyc
#function_name = "sum_of_three_numbers"
#start_line_number = 11

#pyc backf
#function_name = "squareNumber"
#start_line_number = 7
print("========starting traverse")
print(f"function name:{function_name}, start_line_number:{start_line_number}")
if function_name in vertex_maps and start_line_number in vertex_maps[function_name]:
    start_vertex = vertex_maps[function_name][start_line_number]
    #dfs(global_graph, start_vertex, global_node_data=global_node_data)
    #dfs_path(global_graph, start_vertex,global_node_data)
    if sys.argv[5] == 'b':
        dfs_all_paths_backf(global_graph, start_vertex, set(), [], global_node_data,True)
    elif sys.argv[5] == 'f':
        dfs_all_paths(global_graph, start_vertex, set(), [], global_node_data,True)
        print("=============Done=============")
else:
    print(f"function({function_name}):{vertex_maps[function_name]}")
    print(f"function_name:{function_name} or line number:{start_line_number} cannot be found")
