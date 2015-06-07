# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 22:02:46 2014

@author: guidolo
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# imagen2csv.py
#
# Copyright 2014 santiago <santiago@geofreedom>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
#
from osgeo import gdal
from sys import argv
from numpy import asarray, savetxt, hstack

# Datos a ingresar
full_path_img = argv[1]
full_path_csv = argv[2]

# Abre la imagen
dataset = gdal.Open(full_path_img, gdal.GA_ReadOnly)
cantidad_bandas = dataset.RasterCount
datos_bandas = []
header = ""
fmt = []
print "Tamaño: %ix%i" %(dataset.RasterXSize, dataset.RasterYSize)

# para cada banda
for b in range(cantidad_bandas):
    print "Procesando Banda: %i de %i" %(b + 1, cantidad_bandas)
    una_banda = dataset.GetRasterBand(b + 1)
    datos_bandas.append(asarray(una_banda.ReadAsArray()).reshape(-1).transpose() )
    header += "banda_%i,"% (b + 1)
    fmt.append('%.f')
    
print "Header:", header
print "Format:", fmt

savetxt(full_path_csv, hstack(datos_bandas).reshape(dataset.RasterXSize * dataset.RasterYSize, cantidad_bandas), delimiter=",", header=header, fmt=fmt, comments='')
