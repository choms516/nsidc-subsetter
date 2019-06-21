#!/usr/bin/env python
u"""
read_kml_file.py
Written by Tyler Sutterley (06/2019)
Reads polygons from keyhole markup language (.kml or .kmz) files

INPUTS:
	input .kml or .kmz file

OUTPUT:
	shapely multipolygon object of input file

OPTIONS:
	KMZ: input file is compressed

PYTHON DEPENDENCIES:
	numpy: Scientific Computing Tools For Python
		http://www.numpy.org
		http://www.scipy.org/NumPy_for_Matlab_Users
	fiona: Python wrapper for vector data access functions from the OGR library
		https://fiona.readthedocs.io/en/latest/manual.html
	geopandas: Python tools for geographic data
		http://geopandas.readthedocs.io/
	shapely: PostGIS-ish operations outside a database context for Python
		http://toblerity.org/shapely/index.html

UPDATE HISTORY:
	Written 06/2019
"""
from __future__ import print_function

import os
import io
import zipfile
import fiona
import geopandas
import numpy as np
#-- enable kml driver for geopandas
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
from shapely.geometry import Polygon, MultiPolygon

#-- PURPOSE: read keyhole markup language (.kml) files
def read_kml_file(input_file, KMZ=False):
	#-- if input file is compressed
	if KMZ:
		#-- decompress and parse KMZ file
		kmz = zipfile.ZipFile(os.path.expanduser(input_file), 'r')
		kml_input = geopandas.read_file(io.BytesIO(kmz.read('doc.kml')))
	else:
		kml_input = geopandas.read_file(os.path.expanduser(input_file))

	#-- list of polygons
	poly_list = []
	#-- find feature within kml file
	for feature in kml_input.iterfeatures():
		#-- extract coordinates
		coords = np.squeeze(feature['geometry']['coordinates'])
		#-- if coordinate set is a polygon
		if (coords.ndim == 2):
			#-- create polygon from coordinate set
			poly_obj = Polygon(list(zip(coords[:,0],coords[:,1])))
			#-- Valid Polygon cannot have overlapping exterior or interior rings
			if (not poly_obj.is_valid):
				poly_obj = poly_obj.buffer(0)
			poly_list.append(poly_obj)
	#-- create shapely multipolygon object
	mpoly_obj = MultiPolygon(poly_list)
	#-- return the polygon object
	return mpoly_obj