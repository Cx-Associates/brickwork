"""simple script for reading .ttl files and deploying them locally for SPARQL queries

"""
from brickschema import Graph

g = Graph(load_brick=True)
g.load_file('models/msl.ttl')
g.serve()