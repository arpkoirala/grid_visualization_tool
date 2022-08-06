from pandapower.plotting.plotly.mapbox_plot import set_mapbox_token
set_mapbox_token('pk.eyJ1IjoiaGFycmlld2lnZXJpbmNrIiwiYSI6ImNsNmY3dHN1ejA0N2gzY3A4NmUyaTI0bTYifQ.fMddcDHleSnFqG4emL1Hxg')

from pandapower.plotting.plotly import simple_plotly, pf_res_plotly, vlevel_plotly
from pandapower.networks import mv_oberrhein

net = mv_oberrhein()

net = mv_oberrhein()
simple_plotly(net, on_map=True, projection='epsg:31467');