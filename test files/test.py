import pandas as pd
import pandapower as pp
from pandapower.plotting.plotly import pf_res_plotly


from create_net import createMVnet, createLVnet

pathMV = 'data/MV_benchmarks/'
netMV = createMVnet(pathMV+'bus33.json')  # alternatively: netMV = pp.from_json(pathMV+'ppbus33.json')
netMV # print the pandapower network and its dataframes

pp.runpp(netMV) # run powerflow on the network
netMV # additional dataframes containing the powerflow results are added to the pandapower network object

netMV.bus.head(), netMV.res_bus.head() # print some of the dataframes in netMV
# the '.head() method allows to only print the first few lines of the dataframe

fig = pf_res_plotly(netMV) # plot the power flow results

netMV.switch # let's look at the network switches

netMV.switch.closed[32]=True # close switch 32
netMV.switch.closed[12]=False # and open switch 12 (conserves radiality)

pp.runpp(netMV) # re-run the powerflow 
fig = pf_res_plotly(netMV) # plot the power flow results

