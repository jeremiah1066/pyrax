"""
This script will find continer and account info from a CDN URI.
Usage cf_search_uri.py APIKEY_FILE.txt CDN_URL
The password file format should a text file with each username -space- apikey.
Below is an example of how the APIKEY_FILE.txt should look.

username api_key
username2 api_key2
username3 api_key3

Works with both US and UK accounts. 
"""


import os
import sys
import pyrax
import pyrax.exceptions as exc


f = open(sys.argv[1], "r")
words = f.read().split("\n")
dict = {}
for w in words:
    try:
        s = w.split(" ")
        x = len(s)
        dict[s[0]] = s[1]
    except:
        break
for user_n in dict:
    try:
        pyrax.set_credentials(user_n, dict[user_n])
        london_check = False
    except exc.AuthenticationFailed:
        print user_n, ": False"
        continue
    except AttributeError:
        try:
            pyrax.set_credentials(user_n, dict[user_n], region="LON")
            london_check = True
        except exc.AuthenticationFailed:
            print user_n, ": False"
            continue
    print user_n, ":", pyrax.identity.authenticated
    if london_check is True:
        cf_lon = pyrax.connect_to_cloudfiles(region="LON")
        for i in cf_lon.get_all_containers():
            if i.cdn_uri == sys.argv[2] or i.cdn_ssl_uri == sys.argv[2] or i.cdn_streaming_uri == sys.argv[2]:
                print "**", i.name, "**"
                print "URL:", i.cdn_uri
                print "SSL:", i.cdn_ssl_uri
                print "Streaming:", i.cdn_streaming_uri
    else:
        cf_ord = pyrax.connect_to_cloudfiles(region="ORD")
        cf_dfw = pyrax.connect_to_cloudfiles(region="DFW")
        for i in cf_ord.get_all_containers() + cf_dfw.get_all_containers():
                if i.cdn_uri is not None:
                        if i.cdn_uri == sys.argv[2] or i.cdn_ssl_uri == sys.argv[2] or i.cdn_streaming_uri == sys.argv[2]:
                            print "**", i.name, "**"
                            print "URL:", i.cdn_uri
                            print "SSL:", i.cdn_ssl_uri
                            print "Streaming:", i.cdn_streaming_uri
