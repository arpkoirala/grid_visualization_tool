from numpy import floor, isnan
import networkx as nx
from pandapower import topology



def generate_nodes(pandanet,vlevel,colorgradient1,colorgradient2,v_cuttoff_under,v_cuttoff_over):
    # this auxilary function generates all the nodes to be displayed on the network map
    # the function return a list containing all nodes; this is the input of the elements-property of the network map.
    all_nodes =[] 
    ext_grid = pandanet.ext_grid.bus.values
    if vlevel: # if vlevel is True, nodes will be colorscaled according to their vlevel
        vlevels = pandanet.res_bus.vm_pu.values
        for node in pandanet.bus.index:
            x_coord = int(pandanet.bus_geodata.x[node]*10) # COORDINATES ARE x 10 on the network map 
            y_coord = int(pandanet.bus_geodata.y[node]*10) # this is done because otherwise the nodes and lines are to close and it becomes impossible to select the one you want
            if node in ext_grid:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'ext_grid'})
            elif isnan(vlevels[node]):
                print('bus ' + str(node) + '= nan')
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'bus-nan'})
            else:
                if vlevels[node] <=1:
                    diff = (1-vlevels[node])/(1 - v_cuttoff_under)*len(colorgradient1) # transformation that projects the range of undervoltage (v_cuttoff - 1) onto the amount of colors in the colorgradient
                    colorindex = floor(diff)
                    colorindex = colorindex.astype(int)
                    if colorindex < len(colorgradient1):
                        all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': colorgradient1[colorindex][1:]})
                    else:
                        all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord},'classes': colorgradient1[len(colorgradient1) -1][1:]})
                
                else:
                    diff = (vlevels[node]-1)/(v_cuttoff_over - 1)*len(colorgradient2) # transformation that projects the range of overvoltage (v_cuttoff - 1) onto the amount of colors in the colorgradient
                    colorindex = floor(diff)
                    colorindex = colorindex.astype(int)
                    if colorindex < len(colorgradient2):
                        all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': colorgradient2[colorindex][1:]})  
                    else:
                        all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord},'classes': colorgradient2[len(colorgradient2) -1][1:]})
                colorindex = int()
    else:
        for node in pandanet.bus.index:
            x_coord = int(pandanet.bus_geodata.x[node]*10)
            y_coord = int(pandanet.bus_geodata.y[node]*10)
            if node in ext_grid:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'ext_grid'})
            else:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'busstandard'})
    return all_nodes

def generate_edges(pandanet,Loading,colorgradient):
    # this auxilary function generates all the liens to be displayed on the network map
    # the function return a list containing all lines; this is the input of the elements-property of the network map
    open_lines = pandanet.switch[pandanet.switch.closed == False].element.values.tolist()
    all_edges =[]
    if Loading:

        loading_levels = pandanet.res_line.loading_percent.values
        colorindex = floor(loading_levels*len(colorgradient)/100) # transformation that projects the range of loading values (0-100) onto the amount of colors in the colorgradient
        colorindex = colorindex.astype(int)  

        for edge in pandanet.line.index:
            edge_class=''
            if edge in open_lines:
                edge_class='open-switch'
            elif isnan(loading_levels[edge]):
                edge_class='line-nan'
                print('line ' + str(edge) + '= nan')
            elif colorindex[edge] > len(colorgradient) - 1:  
                edge_class='line-overloaded'
            else: 
                edge_class=colorgradient[colorindex[edge]][1:] + 'line' 
            all_edges.append({'data': {'label': str(edge), 'source': str(pandanet.line.from_bus[edge]), 'target': str(pandanet.line.to_bus[edge])},'selectable': True,'classes': edge_class})
        return all_edges
    else:
        for edge in pandanet.line.index:
            if edge in open_lines:
                all_edges.append({'data': {'label': str(edge),'source': str(pandanet.line.from_bus[edge]), 'target': str(pandanet.line.to_bus[edge])},'selectable': True,'classes': 'open-switch'})
            else:
                all_edges.append({'data': {'label': str(edge),'source': str(pandanet.line.from_bus[edge]), 'target': str(pandanet.line.to_bus[edge])},'selectable': True,'classes': 'line-black'})
        return all_edges

def is_radial(net):
    # check the radiality of the network in its current configuration

    graph = topology.create_nxgraph(net)
    
    for i in range(len(net.ext_grid.bus)-1): # connect the reference buses for radiality check
        graph.add_edges_from([(net.ext_grid.bus[i],net.ext_grid.bus[i+1])])

    if not len(graph.nodes())==len(graph.edges())+1:
        return False
    
    elif not nx.is_connected(graph):
        return False

    # Note: checking if (nr of nodes = nr of edges + 1) and connectivity is enough to deterimine if a network is radial and connected.
    # It therefore also implies that there are no loops in the network
    # However it is also possible to determine if there are loops directly by running the following lines of code:
    # graph = nx.Graph(graph) # change type from Multigraph to Graph to use number_of_selfloops() method
    # nx.number_of_selfloops(graph) # this should be 0 for radial networks
    else:
        return True