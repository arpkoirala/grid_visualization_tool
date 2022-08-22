from numpy import floor, isnan



def generate_nodes(pandanet,vlevel,colorgradient1,colorgradient2):
    all_nodes =[]
    ext_grid = pandanet.ext_grid.bus.values
    max_difference = 0.05 ## HARDCODED  max difference that will be shown on the map. Difference higher will have the same color. Used to normalize the vlevels
    if vlevel:
        vlevels = pandanet.res_bus.vm_pu.values
        #diff = (1-vlevels)/max_difference*len(colorgradient1)
        #colorindex = floor(diff)
        #colorindex = colorindex.astype(int)
        for node in pandanet.bus.index:
            x_coord = int(pandanet.bus_geodata.x[node]*10) # !!! COORDINATES ARE x 10, 
            y_coord = int(pandanet.bus_geodata.y[node]*10)
            if node in ext_grid:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'ext_grid'})
            elif isnan(vlevels[node]):
                print('bus ' + str(node) + '= nan')
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'bus-nan'})
            else:
                if vlevels[node] <=1:
                    diff = (1-vlevels[node])/max_difference*len(colorgradient1)
                    colorindex = floor(diff)
                    colorindex = colorindex.astype(int)
                    if colorindex < len(colorgradient1):
                        all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': colorgradient1[colorindex][1:]})
                    else:
                        all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord},'classes': colorgradient1[len(colorgradient1) -1][1:]})
                
                else:
                    diff = (vlevels[node]-1)/max_difference*len(colorgradient2)
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
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'buswhite'})
    return all_nodes

def generate_edges(pandanet,Loading,colorgradient):

    open_lines = pandanet.switch[pandanet.switch.closed == False].element.values.tolist()
    all_edges =[]
    if Loading:

        loading_levels = pandanet.res_line.loading_percent.values
        colorindex = floor(loading_levels*len(colorgradient)/100)  #### hmmm
        colorindex = colorindex.astype(int)

        for edge in pandanet.line.index:
            edge_class=''
            if edge in open_lines:
                edge_class='open-switch'
            elif isnan(loading_levels[edge]):
                edge_class='line-nan'
                print('line ' + str(edge) + '= nan')
            elif colorindex[edge] > len(colorgradient) - 1:  #pandanet.res_line.loading_percent[edge] > 100:
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