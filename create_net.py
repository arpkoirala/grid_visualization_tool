
import pandapower as pp
import json

def createLVnet(bus_df, line_df, ext_grid_df, load_per_bus_df):
    # S.K.: parser for creating a pandapower-network from the bus/ line/ extgrid and load dataframes
    net = pp.create_empty_network() # creates an empty pandapower network
    geodata = [[bus.x, bus.y] for _, bus in bus_df.iterrows()] # get the geodata from the bus-dataframe
    pp.create_buses(net, len(bus_df), vn_kv = bus_df.vn_kv, geodata = geodata) # adds the bus-information to the pp network
    for _,feeder in ext_grid_df.iterrows(): pp.create_ext_grid(net, feeder.bus, name=feeder.feeder_id) # adds the feeder-heads to a virtual external grid
    pp.create_loads(net, load_per_bus_df.bus, load_per_bus_df.p_mw_tot, q_mvar = load_per_bus_df.q_mvar_tot, name=load_per_bus_df.index) # adds the loads to the right buses
    pp.create_lines_from_parameters(net, line_df.from_bus, line_df.to_bus, line_df.length_km, line_df.r_ohm_per_km, line_df.x_ohm_per_km, 0, line_df.max_i_ka )
    for _, line in line_df.iterrows():
        if line.is_switch==True:
            pp.create_switch(net, line.to_bus, line.name, 'l', closed=line.closed, name=line.name_switch, type = line.type_switch)
    return net

def createMVnet(jsonfile_with_net_info):
    # S.K.: the medium voltage benchmark networks are stored in the data in 2 formats, one I made myself (bus33.json, bus70.json, bus83.json,...) which can be transformed into
    # a pandapower network using this createMVnet() parser. The other format (ppbus33.json, ppbus70.json, ppbus83.json,...) is pandapowers way of storing a pandapower network
    # in a json file which can be opened using pandapowers built-in method: pp.from_json('ppbus33.json')
    
    with open(jsonfile_with_net_info) as file:
        data = json.load(file)
  
    net = pp.create_empty_network()
    # net = pp.create_empty_network(sn_mva = data['sn_mva'])
    pp.create_buses(net, data['buses']['nr'], vn_kv = data['vn_kv'], geodata = data['buses']['geodata'])
    for bus_id in data['ext_grid']['buses']: pp.create_ext_grid(net, bus_id)
    pp.create_loads(net, data['loads']['buses'], data['loads']['p_mw'], q_mvar = data['loads']['q_mvar'])
    if data['shunts']['buses'] != None:
        for i, bus_id in enumerate(data['shunts']['buses']): pp.create_shunt(net, bus_id, data['shunts']['q_mvar'][i])
    pp.create_lines_from_parameters(net, data['lines']['from_buses'], data['lines']['to_buses'], 1, data['lines']['rs_ohm'], data['lines']['xs_ohm'], 0, data['max_i_ka'])
    
    pp.create_switches(net, data['switches']['buses'], data['switches']['lines'], 'l', closed=data['switches']['status'])


    return net
