#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 2021

Developed and tested on:

- Linux 20.04 LTS
- Windows 10
- Python 3.8 (Spyder 4)

@author: Nikola Knezevic ASTRO DATA
"""

import datetime
import os
import requests
import json
import zipfile
import shutil

#------------------------------------------------------------------------
WISeREP                = "www.wiserep.org"

url_wis_spectra_search = "https://" + WISeREP + "/search/spectra"

# Example of specific parameter options related to the download itself:
# &num_page=250
# &format=tsv/csv/json
# &files_type=none/ascii/fits/all
# &personal_api_key=...
# &bot_api_key=...

# Specify the Personal api key here (*** MUST BE PROVIDED ***)
personal_api_key       = "933df4cde7d550e732345ee0620929e35ae3dfdf"

# for User-Agent:
WIS_USER_NAME          = "theller"
WIS_USER_ID            = "YOUR_USER_ID"

# Specify the required parameters here
# Possible files type: &files_type=none | ascii | fits | all
# Possible metadata list format: &format=csv | tsv | json
# (In this example - all public type Ib/c's (and sub-types); metadata in CSV format; incl. ascii files.)
obj_type               = "type[]=3%2C103%2C104" #SN1a, SN1a-91-bg-like, SN1a-91-T-like
phase_types            = "phase_types[]=40"
spec_types             = "spectypes[]=10"
#query_params           = f"&public=yes&{obj_type}&{phase_types}"
query_params           = "&name=&name_like=0&public=yes&spectra_count=&ra=&decl=&radius=&coords_unit=arcsec&groupid[]=null&type[]=3%2C103%2C104&type_family[]=null&redshift_min=&redshift_max=&inserted_period_value=0&inserted_period_units=days&ra_range_min=&ra_range_max=&decl_range_min=&decl_range_max=&reporter=&hostname=&phase_types[]=40&date_start[date]=&date_end[date]=&last_modufied_start[date]=&last_modufied_end[date]=&last_modufied_modifier=&creation_start[date]=&creation_end[date]=&creation_modifier"
download_params        = "&num_page=250&format=csv&files_type=ascii"

parameters             = "?" + query_params+download_params + "&personal_api_key=" + personal_api_key

# url of wiserep spectra search (with parameters)
URL                    = url_wis_spectra_search + parameters

# external http errors
ext_http_errors       = [403, 500, 503]
err_msg               = ["Forbidden", "Internal Server Error: Something is broken", "Service Unavailable"]
#------------------------------------------------------------------------


#------------------------------------------------------------------------
def is_string_json(string):
    try:
        json_object = json.loads(string)
    except Exception:
        return False
    return json_object

def response_status(response):
    json_string = is_string_json(response.text)
    if json_string != False:
        status = "[ " + str(json_string['id_code']) + " - '" + json_string['id_message'] + "' ]"
    else:
        status_code = response.status_code
        if status_code == 200:
            status_msg = 'OK'
        elif status_code in ext_http_errors:
            status_msg = err_msg[ext_http_errors.index(status_code)]
        else:
            status_msg = 'Undocumented error'
        status = "[ " + str(status_code) + " - '" + status_msg + "' ]"
    return status

def print_response(response, page_num):
    status = response_status(response)
    stats = 'Page number ' + str(page_num) + ' | return code: ' + status        
    print (stats)
#------------------------------------------------------------------------


#------------------------------------------------------------------------
# current date and time
current_datetime = datetime.datetime.now()
current_date_time = current_datetime.strftime("%Y%m%d_%H%M%S")

# current working directory
cwd = os.getcwd()

# current download folder
current_download_folder = os.path.join(cwd, "wiserep_data")
os.mkdir(current_download_folder)

# marker and headers
wis_marker = 'wis_marker{"wis_id": "' + str(WIS_USER_ID) + '", "type": "user", "name": "' + WIS_USER_NAME + '"}'
headers = {'User-Agent': wis_marker}

# check file extension
if "format=tsv" in download_params:
    extension = ".tsv"
elif "format=csv" in download_params:
    extension = ".csv"
elif "format=json" in download_params:
    extension = ".json"
else:
    extension = ".txt"

# meta data list and file
META_DATA_LIST = []
META_DATA_FILE = os.path.join(cwd, "spectra_" + current_date_time + extension)

# page number
page_num = 0

# go trough every page
while True:
    # url for download
    url = URL + "&page=" + str(page_num)
    # send requests
    response = requests.post(url, headers = headers, stream = True)
    # chek if response status code is not 200
    if (response.status_code != 200):
        # if there are no more pages for download, don't print response, 
        # only print if response is something else
        if response.status_code != 404:
            print_response(response, page_num + 1)
        break 
    # print response
    print_response(response, page_num + 1)
    # download data
    file_name = 'wiserep_spectra.zip'
    file_path = os.path.join(current_download_folder, file_name)
    with open(file_path, 'wb') as f:
        for data in response:
            f.write(data)
    # unzip data
    zip_ref = zipfile.ZipFile(file_path, 'r')
    zip_ref.extractall(current_download_folder)
    zip_ref.close()
    # remove .zip file
    os.remove(file_path)            
    # take meta data file
    downloaded_files = os.listdir(current_download_folder)
    meta_data_file = os.path.join(current_download_folder, [e for e in downloaded_files if 'wiserep_spectra' in e][0])          
    # read meta data file
    with open(meta_data_file,'r', encoding='utf8') as f:
        meta_data_list = f.read().splitlines()

    # write this meta data list to the final meta data list
    if page_num == 0:
        META_DATA_LIST = META_DATA_LIST + meta_data_list
    else:
        META_DATA_LIST = META_DATA_LIST + meta_data_list[1:]         
    # increase page number 
    page_num = page_num + 1                 
    # remove meta data file
    os.remove(meta_data_file)

# write meta data list to file         
if META_DATA_LIST != []:
    f = open(META_DATA_FILE, 'w', encoding='utf8')
    for i in range(len(META_DATA_LIST)):
        if i == len(META_DATA_LIST) - 1:
            f.write(META_DATA_LIST[i])
        else:
            f.write(META_DATA_LIST[i] + '\n')
    f.close()
    print ("Wiserep data was successfully downloaded.")
    print ("Folder /wiserep_data/ containing the data was created.")
    print ("File spectra_" + current_date_time + extension + " was created.")
else:
    print ("There is no WISeREP data for the given parameters.")
    shutil.rmtree(current_download_folder)
#------------------------------------------------------------------------
