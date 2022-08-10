import pandas as pd
import pandapower as pp
import pandapower.plotting as pplt
import pandapower.topology as top
import networkx as nx
import plotly as plot
import pandapower.plotting.plotly as pplotly

import plotly.graph_objects as go
from pandas import Series
import numpy as np
from pandapower.plotting.plotly import get_plotly_color_palette

from pandapower.plotting.plotly.mapbox_plot import set_mapbox_token
set_mapbox_token('pk.eyJ1IjoiaGFycmlld2lnZXJpbmNrIiwiYSI6ImNsNmY3dHN1ejA0N2gzY3A4NmUyaTI0bTYifQ.fMddcDHleSnFqG4emL1Hxg')

from create_net import createLVnet, createMVnet

##### creating MV net #####
#pathMV = 'data/MV_benchmarks/'
#netMV = createMVnet(pathMV+'bus33.json')

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
#.runpp(netMV)
pp.runpp(netLV)

###########################################################################


#pplt.simple_plot(netMV)
#pplt.simple_plotly(netMV)
#pplt.vlevel_plotly(netMV)
#pplt.pf_res_plotly(netMV, aspectratio=(1,0.5),figsize=2)

###########################################################################


# lc = pplotly.create_line_trace(netLV,netLV.line.index, width=1.5, color='black')
# bc = pplotly.create_bus_trace(netLV, netLV.bus.index, size=20, color="orange", infofunc=Series(index=netLV.bus.index, data='Bus '+ netLV.bus.index.astype(str) + '<br>' + netLV.bus.vn_kv.astype(str) + ' kV'))
# sc = pplotly.create_bus_trace(netLV, netLV.ext_grid.bus.values, size=22,patch_type="square", color='blue')
# pplotly.draw_traces(lc + bc + sc, figsize=1.5, aspectratio=(8,6))

#### highlighting long lines and low voltages,
# long_lines = netLV.line[netLV.line.length_km > 0.1].index
# lcl = pplotly.create_line_trace(netLV, long_lines, color='green', width=2, infofunc=Series(index=netLV.line.index, data=netLV.line.name[long_lines] + '<br>' + netLV.line.length_km[long_lines].astype(str) + ' km'))

# low_voltage_buses = netLV.res_bus[netLV.res_bus.vm_pu < 0.98].index
# bch = pplotly.create_bus_trace(netLV, low_voltage_buses, size=5, color="red")


##### splitting up different feeders
mg = pp.topology.create_nxgraph(netLV, nogobuses=set(netLV.ext_grid.bus.values) | set(netLV.trafo.hv_bus.values))
collections = []
ai = 0
islands = list(pp.topology.connected_components(mg)) # getting connected components of a graph
colors = get_plotly_color_palette(len(islands)) # getting a color for each connected component
for color, area in zip(colors, islands):
    collections += pplotly.create_bus_trace(netLV, area, size=5, color=color, infofunc=Series(index=netLV.bus.index, data='Bus '+ netLV.bus.index.astype(str) + '<br>' + netLV.bus.vn_kv.astype(str) + ' kV'), trace_name='feeder {0}'.format(ai))
    ai += 1
collections += pplotly.create_line_trace(netLV, netLV.line.index, color="grey",infofunc=Series(index=netLV.line.index, data='Line ' + netLV.line.index.astype(str) +'<br>' + netLV.res_line.i_to_ka.astype(str) + '?' + '<br>' + "Loading: " ))
collections += pplotly.create_bus_trace(netLV, netLV.ext_grid.bus.values, patch_type="square", size=6, color="yellow")

pplotly.draw_traces(collections, figsize=2);

##### plotting on a map

# pplotly.geo_data_to_latlong(netLV, projection='epsg:31467')
# lc = pplotly.create_line_trace(netLV,netLV.line.index, width=1.5, color='black')
# bc = pplotly.create_bus_trace(netLV, netLV.bus.index, size=5, color="orange", infofunc=Series(index=netLV.bus.index, data=netLV.bus.name + '<br>' + netLV.bus.vn_kv.astype(str) + ' kV'))
# sc = pplotly.create_bus_trace(netLV, netLV.ext_grid.bus.values, size=6,patch_type="square", color='blue')
# pplotly.draw_traces(lc + bc + sc, figsize=1.5, on_map=True, aspectratio=(8,6));

