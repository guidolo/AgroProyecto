#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script para descarga y procesamiento de datos de shapefiles con datos de serie 1.
#
# Como salida genera el archivo csv salida_serie_1_wc.csv con variables de posición, rendimineto, y clima para cada serie
#
# En el mismo directorio del script debe contener el archivo file_serie1.csv que contiene los identificadores de cada serie.
#
# Además el directorio debe contener la carpeta worldclim con los rasters 43 y 44 de datos 
# climáticos historicos (descargar en http://www.worldclim.org/tiles.php )


import csv
import wget
import zipfile
import shutil
import ogr
import gdal
import numpy
import os.path
import struct

class WorldClim:
	def __init__(self, path = "./worldclim", grid = ["43", "44"]):
		self.alt = {}
		self.bio = {}
		self.prec = {}
		self.tmax = {}
		self.tmean = {}
		self.tmin = {}
		for cell in grid:
			self.alt[str(cell)] = gdal.Open(os.path.join(path, "alt" ,"alt_" + str(cell) + ".tif" ))
			self.bio[str(cell)] =  [gdal.Open(os.path.join(path, "bio", "bio" + str(i) + "_" + str(cell) + ".tif" )) for i in range(1,20)]
			self.prec[str(cell)] =  [gdal.Open(os.path.join(path, "prec","prec" + str(i) + "_" + str(cell) + ".tif" )) for i in range(1,13)]
			self.tmax[str(cell)] =  [gdal.Open(os.path.join(path, "tmax", "tmax" + str(i) + "_" + str(cell) + ".tif" )) for i in range(1,13)]
			self.tmean[str(cell)] = [gdal.Open(os.path.join(path, "tmean", "tmean" + str(i) + "_" + str(cell) + ".tif" )) for i in range(1,13)]
			self.tmin[str(cell)] =  [gdal.Open(os.path.join(path,"tmin", "tmin" + str(i) + "_" + str(cell) + ".tif" )) for i in range(1,13)]
	
	def get_cell(self, lng, lat):
		for cell, src_ds in self.alt.items():
			gt=src_ds.GetGeoTransform()
			
			min_lng = gt[0] # ejemplo 44: -60.0 -> 60 Oeste
			max_lng =  src_ds.RasterXSize * gt[1] + gt[0] # -30.0 -> 30 Oeste
			
			min_lat = src_ds.RasterYSize * gt[5] + gt[3] # -60 -> 60 Sur
			max_lat = gt[3] # -30.0 -> 30 Sur
			if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
				return cell
				
		raise IndexError("La cordenada (lat: %f, lng: %f) no se encuentra dentro de los rasters de worldclim." % (lat,lng))
	
	
	def get_row_header(self):
		ret = ["alt"]
		ret += ["prec" + str(i) for i in range(1,13)]
		ret += ["tmin" + str(i) for i in range(1,13)]
		ret += ["tmean" + str(i) for i in range(1,13)]
		ret += ["tmax" + str(i) for i in range(1,13)]
		ret += ["bio" + str(i) for i in range(1,20)]
		return ret
		
	def get_row(self, lng, lat):
		ret = []
		cell = self.get_cell(lng, lat)
		
		src_ds = self.alt[cell]
		gt = src_ds.GetGeoTransform()
		
		px = int((lng - gt[0]) / gt[1]) #x pixel
		py = int((lat - gt[3]) / gt[5]) #y pixel
		
		#altitud
		rb=src_ds.GetRasterBand(1)
		structval=rb.ReadRaster(px,py,1,1,buf_type=gdal.GDT_UInt16)
		ret.append(struct.unpack('h' , structval)[0])
		 
		# resto de varialbes
		for variable in [self.prec[cell],self.tmin[cell],self.tmean[cell],self.tmax[cell],self.bio[cell]]:
			for src_ds in variable:
				rb=src_ds.GetRasterBand(1)
				structval=rb.ReadRaster(px,py,1,1,buf_type=gdal.GDT_UInt16)
				ret.append(struct.unpack('h' , structval)[0]) 
		
		return ret
				
	def get_tmean(self, month, lng, lat):
		cell = self.get_cell(lng, lat)
		return self.get_raster_value(self.tmean[cell][month])

	def get_tmin(self, month, lng, lat):
		cell = self.get_cell(lng, lat)
		return self.get_raster_value(self.tmin[cell][month])
	
	def get_tmax(self, month, lng, lat):
		cell = self.get_cell(lng, lat)
		return self.get_raster_value(self.tmax[cell][month])
	
	def get_prec(self, month, lng, lat):
		cell = self.get_cell(lng, lat)
		return self.get_raster_value(self.tprec[cell][month])
	
	def get_alt(self, lng, lat):
		cell = self.get_cell(lng, lat)
		return self.get_raster_value(self.alt[cell])
	
	def get_bio(self, variable, lng, lat):
		cell = self.get_cell(lng, lat)
		return self.get_raster_value(self.bio[cell][variable])
		
	def get_raster_value(self, src_ds, lng, lat):
		gt = src_ds.GetGeoTransform()
		rb = src_ds.GetRasterBand(1)
		px = int((lng - gt[0]) / gt[1]) #x pixel
		py = int((lat - gt[3]) / gt[5]) #y pixel
		structval=rb.ReadRaster(px,py,1,1,buf_type=gdal.GDT_UInt16) #Assumes 16 bit int aka 'short'
		intval = struct.unpack('h' , structval) #use the 'short' format code (2 bytes) not int (4 bytes)
		return intval[0] #intval is a tuple, length=1 as we only asked for 1 pixel value
		
		
csvfile_out=open("salida_serie_1_wc.csv",'w+')
csvwriter = csv.writer(csvfile_out)
wc = WorldClim()
 
csvwriter.writerow(["id_serie", "serie", "producto", "campania", 
					"lng","lat",
					"humedad_mean","humedad_std",
					"elevacion_mean","elevacion_std"] + wc.get_row_header() +\
					["rendimiento_median", "rendimiento_mean","rendimiento_std"])

csvfile_in = open('file_serie1.csv', 'rb')
csvreader = csv.reader(csvfile_in) 
csvreader.next()

i = 0
for row in csvreader:
	id_serie = row[0]
	producto = row[1]
	campania = row[2][:4]
	serie = 1
	i +=1
	if i % 500 == 0:
		print str(i) + " - IDSERIE: " + id_serie
	filezip = "./zips/" + id_serie + ".zip"
	if not os.path.exists(filezip):
		if serie == 1:
			filezip = wget.download("http://agrodatos.info/monitores/serie-1/" + id_serie + ".zip", out ="./zips/")
		elif serie == 2:
			filezip = wget.download("http://agrodatos.info/monitores/serie-2/curated/" + id_serie + ".zip", out ="./zips-serie2/")
		else:
			raise ValueError("Serie desconocida")
	#else:
	#	print "Archivo ya descargado"
	
	continue
	
	z = zipfile.ZipFile(filezip)
	z.extractall(id_serie)

	ds=ogr.Open(id_serie +"/" + id_serie +".shp")
	lyr=ds.GetLayer()

	humedad = []
	rendimiento = []
	elevacion = []

	geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
	for feature in lyr:
		geomcol.AddGeometry(feature.GetGeometryRef())
		humedad.append(feature.GetField("HUMEDAD"))
		rendimiento.append(feature.GetField("REND"))
		elevacion.append(feature.GetField("ELEVACION"))

	centroid = geomcol.ConvexHull().Centroid()
	wc_data = wc.get_row(centroid.GetX(), centroid.GetY())

	csvwriter.writerow([id_serie, producto, campania, 
						centroid.GetX(),centroid.GetY(),
						numpy.mean(humedad),numpy.std(humedad),
						numpy.mean(elevacion),numpy.std(elevacion)] + wc_data +\
						[numpy.median(rendimiento),numpy.mean(rendimiento),numpy.std(rendimiento)])
	z.close()
	shutil.rmtree(id_serie)

	
csvfile_out.close()
csvfile_in.close()
