#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ############################################################################
#
# download.py
# 05/14/2022 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# Download and store the data for the backup of viaClásica
# we need the JSON file from web.archive.org so:
# 
# go to https://web.archive.org/web/*/www.viaclasica.com/*
# select the URLS
# the json file is 
#   https://web.archive.org/web/timemap/json?url=www.viaclasica.com%2F&matchType=prefix&collapse=urlkey&output=json&fl=original%2Cmimetype%2Ctimestamp%2Cendtimestamp%2Cgroupcount%2Cuniqcount&filter=!statuscode%3A%5B45%5D..&limit=1000000000&_=1652520674856

# https://web.archive.org/web/timemap/json?url=www.viaclasica.com%2F&matchType=prefix&collapse=urlkey&output=json&fl=original%2Cmimetype%2Ctimestamp%2Cendtimestamp%2Cgroupcount%2Cuniqcount&filter=!statuscode%3A%5B45%5D..&limit=0
# now, we have all the data stored in the archive for this site. Just process the required mime types and filters.
#
# aportaciones_croquis
# banco_de_fotos
# croquis
# fondos_escritorio
# imagen
# libros_pedriza
#
# process the format.
# 
# ['original', 'mimetype', 'timestamp', 'endtimestamp', 'groupcount', 'uniqcount']
# ["http://www.viaclasica.com:80/aportaciones_croquis/fotos/Cabrera/miel/viapiloto.pdf","application/pdf","20081031144944","20081031144944","2","1"],
# https://web.archive.org/web/20081031144944/http://www.viaclasica.com:80/aportaciones_croquis/fotos/Cabrera/miel/viapiloto.pdf
# https://web.archive.org/web/20081031144944if_/http://www.viaclasica.com:80/aportaciones_croquis/fotos/Cabrera/miel/viapiloto.pdf
# download it XD
# 
# https://mega.nz/file/RSBklY7C#qn-let0G4NZBPNuUp8A8Upcp6UXsZNkPe4wo-nBX13M
# 
# ############################################################################

import argparse
import json
import sys
import re
import os
import urllib.parse
from pathlib import Path
import wget
import time

def dd(what):
    print(what)
    sys.exit(0)

class WebManager:

    def __init__(self, output):
        self.output = output

    def load_json(self, fn):
        f = open(fn)
        self.data = json.load(f)
        self.data = self.data[1:]

    def filter_data(self, url=None, mime_type=None, skip=None):

        skip_pattern = ".*(%s).*" % "|".join(skip) if url else None
        url_pattern = ".*(%s).*" % "|".join(url) if url else ".*"
        mime_type_pattern = ".*(%s).*" % "|".join(mime_type) if mime_type else ".*"
       
        ret = []
        for entry in self.data:
            if skip_pattern and re.match(skip_pattern, entry[0]):
                continue

            if re.match(url_pattern, entry[0]) or re.match(mime_type_pattern, entry[1]):
                ret.append(entry)
        return ret
        
    def build_urls(self, items):
        ret = []
        for item in items:
            # download url
            url = "https://web.archive.org/web/%sif_/%s" % (item[3],item[0])
            item.append(url)

            # dirpath structure
            parse_data = urllib.parse.urlparse(item[0])
            item.append(parse_data.path)

            ret.append(item)
        return ret

    def download(self, items, overwrite, sleep_time=0.5):
        for item in items:

            target_path = "%s%s" % (self.output, os.path.dirname(item[7]))
            target_file = "%s%s" % (self.output, item[7])

            if not overwrite and os.path.exists(target_file):
                print("skipping %s (exists)" % item[7])
                continue

            Path(target_path).mkdir(parents=True, exist_ok=True)
            print("downloading %s -> %s" % (item[6], item[7]))
            try:
                wget.download(item[6], target_file) 
            except Exception as e:
                print("error: %s" % e)
                fd = open('error.log','a+')
                fd.write("%s\n" % target_file)
                fd.close()
            
            print("")
            time.sleep(sleep_time) # seconds

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing (Debug)", action="count")
    parser.add_argument('-i', "--input", help="input file (json)", required=True)
    parser.add_argument('-o', "--output", help="output dir", default="output")
    parser.add_argument('-w', "--overwrite", help="overwrite data", default=False)
    args = parser.parse_args()
    
    site =  WebManager(output=args.output)
    site.load_json(args.input)

    # filter data from Json in order to get only the required values
    items = site.filter_data(url=["croquis","fotos"], mime_type=['pdf','ppt','pps','ppx','gif','jpg','png'], skip=["\/foro", "\/wp-content", "\/parallax"])
    print("%d items found" % len(items))
    
    # now, build the download url
    # this is the json data
    # ['original', 'mimetype', 'timestamp', 'endtimestamp', 'groupcount', 'uniqcount']
    # https://web.archive.org/web/20081031144944/http://www.viaclasica.com:80/aportaciones_croquis/fotos/Cabrera/miel/viapiloto.pdf
    # https://web.archive.org/web/20081031144944if_/http://www.viaclasica.com:80/aportaciones_croquis/fotos/Cabrera/miel/viapiloto.pdf

    # build this https://web.archive.org/web/<endtimestamp>if_/<url>
    # also, prepare dirs:
    #  - remove the http.
    #  - use the intermediate path to build the dir structure.
    #  - use the last element as target to download.

    items = site.build_urls(items)
   
    # do the download
    site.download(items, overwrite = args.overwrite)
    