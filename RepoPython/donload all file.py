# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 23:24:29 2014

@author: guidolo
"""

import urllib
import pandas as pd
import shapefile
import os

def shp2dataframe(fname):
    shp = shapefile.Reader(fname)
    r = shp.records()
    fld = np.array(shp.fields[1:], dtype=str)
    data = pd.DataFrame(r, columns=fld[:, 0])
    del shp
    return data

data = shp2dataframe('files_serie_1.dbf')

for i in data['ID']:
    nombre = i + '.zip'
    print(nombre)
    if not os.path.exists(nombre):
        urllib.urlretrieve ("http://agrodatos.info/monitores/serie-1/" + nombre, nombre)