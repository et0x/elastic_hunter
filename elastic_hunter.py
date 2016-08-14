#!/usr/bin/env python
from elasticsearch import Elasticsearch as es
import csv
import json
import optparse
import os
import sys

parser = optparse.OptionParser()
parser.add_option('-c', '--csv', action="store", dest="csv_file")
parser.add_option('-i', '--index', action="store", dest="index_name")
parser.add_option('-s', '--server', action="store", default="localhost")
parser.add_option('-p', '--port', action="store", default=9200, type="int")

options, args = parser.parse_args()

if options.csv_file == None or options.index_name == None:
    print "[!] Invalid usage, check %s -h"%(sys.argv[0])
    sys.exit(-1)

if not (os.path.exists(options.csv_file) and (os.path.isdir(options.csv_file) == False)):
    print "[!] CSV doesn't exist or is a directory"
    sys.exit(-1)


f = open(options.csv_file, 'r')
try:
    reader = csv.DictReader(f)
except:
    print "[!] Error parsing CSV file"
    sys.exit(-1)

try:
    elastic = es([{'host':options.server, 'port':options.port}])
except:
    print "[!] Error connecting to elasticsearch instance"
    sys.exit(-1)

if not elastic.indices.exists(options.index_name):
    print "[!] Index doesn't exist!"
    sys.exit(-1)

found_hits = False
for entry in reader:
    for header_name in entry.keys():
        results = elastic.search(index=options.index_name,  body={"query": {"match": {header_name:entry[header_name]}}})
        if results["hits"]["total"]:
            found_hits = True
            print "[+] Got %d hits where '%s' = '%s'"%(results["hits"]["total"], header_name, entry[header_name])

if not found_hits:
    print "[+] No hits found ..."
