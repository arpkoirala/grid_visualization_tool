import pandas as pd
import pandapower as pp
# from pandapower.plotting.plotly import pf_res_plotly
import pandapower.plotting as pplt
import pandapower.topology as top
import pandapower.networks as nw
import matplotlib.pyplot as plt
import numpy as np

import networkx as nx
import seaborn as sns
colors = sns.color_palette("bright")
#colors = ["b", "g", "r", "c", "y"]

from create_net import createLVnet, createMVnet

##### creating MV net #####
pathMV = 'data/MV_benchmarks/'
netMV = createMVnet(pathMV+'bus33.json')
    
##### creating LV net #####
pathLV = 'data/spanish_LV_net/'

bus_df = pd.read_excel(pathLV+'bus_df.xlsx')
bus_df= bus_df.drop(columns={'Unnamed: 0'}) 

ext_grid_df = pd.read_excel(pathLV+'ext_grid_df.xlsx')

line_df = pd.read_excel(pathLV+'line_df.xlsx')
line_df = line_df.drop(columns={'Unnamed: 0'})


load_per_bus_df = pd.read_excel(pathLV+'load_per_bus_df.xlsx')

netLV = createLVnet(bus_df, line_df, ext_grid_df, load_per_bus_df)


##### Run Powerflows #####
#pp.runpp(netMV) 
pp.runpp(netLV)

###########################################################################

##### different built in plots #####
# pplt.simple_plot(netMV)
# pplt.simple_plotly(netMV)
# pplt.pf_res_plotly(netMV)


###### networkx #####
#mg = top.create_nxgraph(netMV)
#path = nx.shortest_path(mg, 4, 17)
#print(path)
#print(netMV.bus.loc[path])


############# custom plot met matplotlib #############

# bc = pplt.create_bus_collection(netLV, netLV.bus.index, size=0.1, color=colors[0], zorder=10) #create buses
# lc = pplt.create_line_collection(netLV, netLV.line.index, color="grey", zorder=1) #create lines


# ## labels
# #buses = netLV.bus.index.tolist() # list of all bus indices
# #coords = zip(netLV.bus_geodata.x.loc[buses].values, netLV.bus_geodata.y.loc[buses].values) # tuples of all bus coords
# #bic = pplt.create_annotation_collection(size=20, texts=np.char.mod('%d', buses), coords=coords, zorder=3, color=colors[3])

# ## long lines highlighted
# long_lines = netLV.line[netLV.line.length_km > 0.1].index
# lcl = pplt.create_line_collection(netLV, long_lines, color="g", zorder=2)

# ## low voltage buses highlighted
# #low_voltage_buses = netLV.res_bus[netLV.res_bus.vm_pu < 0.98].index
# #bch = pplt.create_bus_collection(netLV, low_voltage_buses, size=5, color=colors[3], zorder=11)

# # slack buses rectangular
# sc = pplt.create_bus_collection(netLV, netLV.ext_grid.bus.values, patch_type="rect", size=1, color=colors[1], zorder=12) # highlight slack busses

# ## buses close to a slack bus/external grid highlighted #### not all are highlighted??
# close_buses = set()
# for slack in netLV.ext_grid.bus:
#     d = top.calc_distance_to_bus(netLV, slack)
#     close_buses |= set(d[d < 0.07].index)
# bch = pplt.create_bus_collection(netLV, close_buses, size=3, color=colors[3], zorder=11)

# pplt.draw_collections([lc, bc, lcl, bch, sc], figsize=(80,60))

# ##### direct line connections + comparison --> comparison doesnt do anything on this grid??
# bc = pplt.create_bus_collection(netLV, netLV.bus.index, size=1, color=colors[0], zorder=10)
# lcd = pplt.create_line_collection(netLV, netLV.line.index, use_bus_geodata=True, color="grey",alpha=0.8,linewidths=2.)
# lc = pplt.create_line_collection(netLV, netLV.line.index, color="red",alpha=0.8, linestyles="dashed",linewidths=2.)

# sc = pplt.create_bus_collection(netLV, netLV.ext_grid.bus.values, patch_type="rect", size=1, color=colors[1], zorder=11)
# pplt.draw_collections([lcd, bc, sc, lc])


############ color maps ###########################


cmap_list=[(10, "green"), (25, "yellow"), (40, "red")]
cmap, norm = pplt.cmap_continuous(cmap_list)
lc = pplt.create_line_collection(netLV, netLV.line.index, zorder=1, cmap=cmap, norm=norm)

cmap_list_bus=[(0.975, "blue"), (1.0, "green"), (1.025, "red")]
cmap_bus, norm_bus = pplt.cmap_continuous(cmap_list_bus)
bc = pplt.create_bus_collection(netLV, netLV.bus.index, size=0.5, zorder=2, cmap=cmap_bus, norm=norm_bus)

pplt.draw_collections([lc, bc], figsize=(8,6))

#### using custom colormaps
# from matplotlib.pyplot import get_cmap
# from matplotlib.colors import Normalize

# cmap = get_cmap('PuBu_r')
# norm = Normalize(vmin=10, vmax=30)

# lc = pplt.create_line_collection(netLV, netLV.line.index, zorder=1, linewidths = 1.5,cmap=cmap, norm=norm)
# bc = pplt.create_bus_collection(netLV, netLV.bus.index, size=2, zorder=2)

# from matplotlib.pyplot import colorbar

# pplt.draw_collections([lc, bc], figsize=(8,6), plot_colorbars=False)
# cbar = colorbar(lc, extend="max")
# cbar.set_ticks([10, 17, 24])
# cbar.ax.set_ylabel("custom text")

plt.show()