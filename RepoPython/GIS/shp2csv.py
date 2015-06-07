#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Conversor de formato shapefiles a csv.
Uso:

shp2csv.py <archivo_origen.shp> <archivo_salida.csv>

Dependencias:

Python GDAL/OGR (sudo easy_install GDAL)
http://trac.osgeo.org/gdal/wiki/GdalOgrInPython
http://pcjericks.github.io/py-gdalogr-cookbook/
"""

import ogr,csv,sys

if len(sys.argv) < 3:
    print "Uso:"
    print "\tshp2csv.py <archivo_origen.shp> <archivo_salida.csv>"
    sys.exit()

shpfile= sys.argv[1]
csvfile= sys.argv[2]

#Open files
ds=ogr.Open(shpfile)
lyr=ds.GetLayer()
csvfile=open(csvfile,'wb')


#Get field names
dfn=lyr.GetLayerDefn()
nfields=dfn.GetFieldCount()
fields=[]
for i in range(nfields):
    fields.append(dfn.GetFieldDefn(i).GetName())
fields.append('kmlgeometry')
fields.append('GeometryType')
fields.append('Centroid')
fields.append('Area')
fields.append('Length')
csvwriter = csv.DictWriter(csvfile, fields)
try:csvwriter.writeheader() #python 2.7+
except:csvfile.write(','.join(fields)+'\n')

# Write attributes and kml out to csv
for feat in lyr:
    attributes=feat.items()
    geom=feat.GetGeometryRef()
    attributes['kmlgeometry']=geom.ExportToKML()
    attributes['GeometryType']=geom.GetGeometryName()
    attributes['Centroid']=geom.Centroid()
    attributes['Area']=geom.GetArea()
    attributes['Length']=geom.Length()
    
    csvwriter.writerow(attributes)

#clean up
del csvwriter,lyr,ds
csvfile.close()	
