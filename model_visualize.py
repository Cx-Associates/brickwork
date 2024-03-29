"""Exports a .png image of a .ttl graph

"""

import io
import pydotplus
import rdflib
from IPython.display import display, Image
from rdflib.tools.rdf2dot import rdf2dot

# specify filepath
ttl_filepath = "F:/PROJECTS/1297 MMC Bramhall Campus Cx/MBCx EMIS Development/mapping/MMC VAV Boxes.ttl"

# create RDF graph and load data from ttl
g = rdflib.Graph()
g.parse(ttl_filepath, format='ttl')

def visualize(g):
    stream = io.StringIO()
    rdf2dot(g, stream, opts={display})
    dg = pydotplus.graph_from_dot_data(stream.getvalue())
    png = dg.create_png()
    display(Image(png))

    return dg

dg = visualize(g)

png = dg.create_png()
with open("Riaz_MMC_VAV.png", "wb") as f:
    f.write(png)