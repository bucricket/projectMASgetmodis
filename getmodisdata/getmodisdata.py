#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 15:10:13 2017

@author: mschull
"""
import subprocess
import os
from pyproj import Proj
import argparse
import getpass
import keyring
import pycurl
from pymodis.downmodis import downModis


base = os.getcwd()  

def folders(base):
    dataBase = os.path.join(base,'data')
    modisBase = os.path.join(dataBase,'MODIS')
    if not os.path.exists(modisBase):
        os.mkdir(modisBase)
    out = {'modisBase':modisBase}
    return out
Folders = folders(base)
modisBase = Folders['modisBase']


def getMODISdata(tiles,product,version,start_date,end_date,auth):    

    if product.startswith('MCD'):
            folder = "MOTA"
    elif product.startswith('MOD'):
            folder = "MOLT"
    else:
        folder = "MOTA"
    product_path = os.path.join(modisBase,product)   
    if not os.path.exists(product_path):
        os.mkdir(product_path)
        
    downModis(product_path, auth[1], auth[0],tiles=tiles, path=folder, 
              product=product,todat=start_date,enddate=end_date)
#    subprocess.call(["modis_download.py", "-r", "-U", "%s" % auth[0], "-P", 
#        "%s" % auth[1],"-p", "%s.%s" % (product,version), "-t", 
#        "%s" % tiles,"-s","%s" % folder, "-f", "%s" % startDate,"-e", "%s" % endDate, 
#         "%s" % productPath])

                 
def latlon2MODtile(lat,lon):
    # reference: https://code.env.duke.edu/projects/mget/wiki/SinusoidalMODIS
    p_modis_grid = Proj('+proj=sinu +R=6371007.181 +nadgrids=@null +wktext')
    x, y = p_modis_grid(lon, lat)
    # or the inverse, from x, y to lon, lat
    lon, lat = p_modis_grid(x, y, inverse=True)
    tileWidth = 1111950.5196666666
    ulx = -20015109.354
    uly = -10007554.677
    H = (x-ulx)/tileWidth
    V = 18-((y-uly)/tileWidth)
    return int(V),int(H)


def main():
    # Get time and location from user
    parser = argparse.ArgumentParser()
    parser.add_argument("lat", type=float, help="latitude")
    parser.add_argument("lon", type=float, help="longitude")
    parser.add_argument("startDate", type=str, help="Start date yyyy-mm-dd")
    parser.add_argument("endDate", type=str, help="end date yyyy-mm-dd")
    parser.add_argument("product", type=str, help="MODIS product")
    parser.add_argument("version", type=str, help="MODIS product version")
    args = parser.parse_args()

    startDate = args.startDate
    endDate = args.endDate
    
     # =====earthData credentials===============
    earthLoginUser = str(getpass.getpass(prompt="earth login username:"))
    if keyring.get_password("nasa",earthLoginUser)==None:
        earthLoginPass = str(getpass.getpass(prompt="earth login password:"))
        keyring.set_password("nasa",earthLoginUser,earthLoginPass)
    else:
        earthLoginPass = str(keyring.get_password("nasa",earthLoginUser)) 

    
    # find MODIS tiles that cover landsat scene
    # MODIS products   
    product = args.product
    version = args.version
    [v,h]= latlon2MODtile(args.lat,args.lon)
    tiles = "h%02dv%02d" %(h,v)
    
    # download MODIS LAI over the same area and time
    print("Downloading MODIS data...")
    getMODISdata(tiles,product,version,startDate,endDate,("%s"% earthLoginUser,"%s"% earthLoginPass))
    
    
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, pycurl.error):
        exit('Received Ctrl + C... Exiting! Bye.', 1)  