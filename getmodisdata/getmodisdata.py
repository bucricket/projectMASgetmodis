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


base = os.getcwd()  

def folders(base):
    dataBase = os.path.join(base,'data')
    landsatDataBase = os.path.join(dataBase,'Landsat-8')
    metBase = os.path.join(dataBase,'MET')
    if not os.path.exists(metBase):
        os.makedirs(metBase) 
    ALEXIbase = os.path.join(dataBase,'ALEXI')
    if not os.path.exists(ALEXIbase):
        os.makedirs(ALEXIbase) 
    albedoBase = os.path.join(landsatDataBase,'albedo')
    if not os.path.exists(albedoBase):
        os.makedirs(albedoBase)   
    ndviBase = os.path.join(landsatDataBase,'ndvi')
    if not os.path.exists(ndviBase):
        os.makedirs(ndviBase)
    landsatSR = os.path.join(landsatDataBase,'SR')
    if not os.path.exists(landsatSR):
        os.makedirs(landsatSR)
    resultsBase = os.path.join(base,'outputs')
    if not os.path.exists(resultsBase):
        os.makedirs(resultsBase)
    landsatLC = os.path.join(landsatDataBase,'LC')
    if not os.path.exists(landsatLC):
        os.makedirs(landsatLC)
    landsatLAI = os.path.join(landsatDataBase,'LAI')
    if not os.path.exists(landsatLAI):
        os.makedirs(landsatLAI)
    modisBase = os.path.join(base,'data','MODIS')
    if not os.path.exists(modisBase):
        os.mkdir(modisBase)
    out = {'dataBase':dataBase,'metBase':metBase,
           'ALEXIbase':ALEXIbase,'landsatDataBase':landsatDataBase,
    'resultsBase':resultsBase,'landsatLC':landsatLC,'albedoBase':albedoBase,
    'ndviBase':ndviBase,'landsatSR':landsatSR,'modisBase':modisBase,'landsatLAI':landsatLAI}
    return out
Folders = folders(base)
modisBase = Folders['modisBase']
landsatSR = Folders['landsatSR']
landsatLAI = Folders['landsatLAI']
landsatTemp = os.path.join(landsatSR,'temp')
if not os.path.exists(landsatTemp):
    os.mkdir(landsatTemp)

def getMODISdata(tiles,product,version,startDate,endDate,auth):    

    if product.startswith('MCD'):
            folder = "MOTA"
    elif product.startswith('MOD'):
            folder = "MOLT"
    else:
        folder = "MOTA"
        
    subprocess.call(["modis_download.py", "-r", "-U", "%s" % auth[0], "-P", 
        "%s" % auth[1],"-p", "%s.%s" % (product,version), "-t", 
        "%s" % tiles,"-s","%s" % folder, "-f", "%s" % startDate,"-e", "%s" % endDate, 
         "%s" % modisBase])

                 
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
    #tiles = 'h10v04,h10v05'
    
    # download MODIS LAI over the same area and time
    print("Downloading MODIS data...")
    getMODISdata(tiles,product,version,startDate,endDate,("%s"% earthLoginUser,"%s"% earthLoginPass))
    
    
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, pycurl.error):
        exit('Received Ctrl + C... Exiting! Bye.', 1)  