# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 10:25:48 2014

@author: guidolo
"""

from osgeo import gdal
from sys import argv
from numpy import asarray, savetxt, hstack

# Datos a ingresar
full_path_img = argv[1]
full_path_csv = argv[2]

full_path_img = 'cebada.asc'

full_path_img = '..\\DatosEntrada\\CVPrecAnual.asc'
full_path_img = '..\\DatosEntrada\\IndiceProdSuelo.asc'


# Abre la imagen
dataset= gdal.Open(full_path_img, gdal.GA_ReadOnly)

cantidad_bandas = dataset.RasterCount
print "Tamaño: %ix%i" %(dataset.RasterXSize, dataset.RasterYSize)


una_banda = dataset.GetRasterBand(1)
una_banda.ReadAsArray()

una_banda.

# para cada banda
for b in range(cantidad_bandas):
    print "Procesando Banda: %i de %i" %(b + 1, cantidad_bandas)
    una_banda = dataset.GetRasterBand(b + 1)
    datos_bandas.append(asarray(una_banda.ReadAsArray()).reshape(-1).transpose() )
    header += "banda_%i,"% (b + 1)
    fmt.append('%.f')
