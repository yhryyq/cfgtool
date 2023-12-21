from getdot import read_dot_files
from pybgl.graph import DirectedGraph
from collections import namedtuple,deque
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
def dfs(graph, start_vertex, visited=None):
    if visited is None:
        visited = set()

    stack = [start_vertex]

    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            current_data = node_data_map[current]
            print(f"当前顶点: {current}, 行号: {current_data.line_number}, 函数名: {current_data.function_name}")
            print(current_data)
            if current_data.callsites:
                print(f"  - Callsites: {current_data.callsites}")

            for e in graph.out_edges(current):
                target = graph.target(e)
                stack.append(target)

    return visited

NodeData = namedtuple('NodeData', ['line_number', 'line_flows', 'node_code', 'callsites', 'is_return_line', 'function_name'])

funcs = read_dot_files("./outdir")
#funcs: function_name, line_flows, callsites, node_code, return_lines

graphs = {}

for func in funcs:

    g = DirectedGraph()

    function_data = {
        'line_numbers': list(func[1].keys()),
        'line_flows': func[1],
        'node_code': func[3],
        'callsites': func[2],
        'function_name': func[0],
        'return_lines': func[4]
    }

    node_data_map = {}
    vertex_map = {}  #vertex to lineNumber


    #create node for each line
    for line_number in function_data['line_numbers']:
        v = g.add_vertex()
        if line_number in function_data['return_lines']:
            return_line = True
        else:
            return_line = False
        node_data = NodeData(
            line_number=line_number,
            line_flows=function_data['line_flows'].get(line_number, []),
            node_code=function_data['node_code'].get(line_number, ''),
            callsites=function_data['callsites'].get(line_number, []),
            is_return_line = return_line,
            function_name=function_data['function_name']
        )
        #print(node_data)
        node_data_map[v] = node_data
        vertex_map[line_number] = v



    #create edge
    for line_number, flows in function_data['line_flows'].items():
        source_vertex = vertex_map[line_number]
        for target_line_number in flows:
            target_vertex = vertex_map[target_line_number]
            g.add_edge(source_vertex, target_vertex)


    graphs[function_data['function_name']] = {'graph': g, 'node_data_map': node_data_map, 'vertex_map': vertex_map}



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



function_name = "main"
start_line_number = 11

start_graph = graphs[function_name]['graph']
start_vertex = vertex_map[start_line_number]

reachable_vertices = dfs(start_graph, start_vertex)

reachable_info = [(node_data_map[v].line_number, node_data_map[v].function_name) for v in reachable_vertices]
print(f"从函数 {function_name} 的行号 {start_line_number} 可达的行号和函数名: {reachable_info}")


