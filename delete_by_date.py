"""
This Script will find and remove files older then a date specified in the ISO format.
To use this script, just start it with the arguments as follows. 
USERNAME API-KEY DATACENTER(DFW,ORD,LON) CONTAINER_NAME DATE(YYYY-MM-DD)
Those 5 arguments will search through a container of any size, 
tell you how many files match your search, and remove those files.

PLEASE USE THIS AT YOUR OWN RISK!!!
This Script has worked for me, but I cannot and will not guarantee that it will work for you.

This scripts supports US and UK accounts. 
Let me know if you have any questions, issues or comments.
"""
import sys
try:
    import pyrax
    import pyrax.exceptions as exc
except ImportError:
    print "Pyrax Not Found\nPlease install Pyrax\nhttp://tinyurl.com/absxgak"
    sys.exit()

old_files = 0
del_files = 0
try:
    username = sys.argv[1]
    api_key = sys.argv[2]
    data_center = sys.argv[3].upper()
    container = sys.argv[4]
    usr_date = sys.argv[5]
except IndexError:
    print "Usage:",sys.argv[0],"Username API-Key Datacenter Container_name Date(YYYY-MM-dd)"
    sys.exit()
#AUTHINTICATION SECTION 
pyrax.set_setting("identity_type", "rackspace")
if data_center.upper() != "DFW" and data_center.upper() != "ORD" and data_center.upper() != "LON":
    print "Invalid Datacenter. Please use DFW, ORD, or LON"
    sys.exit()
if data_center.upper() != "LON":
    try:
        pyrax.set_credentials(username, api_key)
    except exc.AuthenticationFailed:
        print "Authentication Failed\nUsername or API-Key may be incorrect"
        sys.exit()
else:
    try:
        pyrax.set_credentials(username, api_key, region="LON")
    except exc.AuthenticationFailed:
        print "Authentication Failed\nUsername or API-Key may be incorret\nSure This Is A UK Account?"
        sys.exit()
#Connection to Cloud Files
if data_center.upper() == "DFW":
    cf = pyrax.connect_to_cloudfiles(region="DFW")
elif data_center.upper() == "ORD":
    cf = pyrax.connect_to_cloudfiles(region="ORD")
elif data_center.upper() == "LON":
    cf = pyrax.connect_to_cloudfiles(region="LON")
else:
    print "Something broke I think"
    sys.exit()
try:
    cont = cf.get_container(container)
except exc.NoSuchContainer:
    print "Could not find the container: %s\nEXITING" % (container)
    sys.exit()
#Searching for old files
marker = ''
objs = cont.get_objects()
total_count = cont.object_count
cont_name = cont.name
while len(objs) is not 0:
    for obj in objs:
        if obj.last_modified < usr_date:
            old_files += 1
    else:
        marker = obj.name
    objs = cont.get_objects(marker=marker)

if old_files == 0:
    print "No Files Older Then the Specified Date Found\nEXITING"
    sys.exit()
#Ask user and blow away old files
print "you have a total of",total_count,"files in the container:",cont_name
print "You have",old_files,"Files older then the date you specified.:",usr_date
print "That would leave you with",total_count - old_files,"files left."
print "Delete Those Files?[y/n]"
wanna_clear = raw_input("This is a perminant Action\n")
while wanna_clear.lower() != "y" and wanna_clear.lower() != "n":
    wanna_clear = raw_input("Please enter y or n\n")

wanna_clear = wanna_clear.lower()
if wanna_clear == "y":
    print "You said yes.\nDeleting old Files"
    objs = cont.get_objects()
    while len(objs) is not 0:
        for obj in objs:
            if obj.last_modified < usr_date:
                obj.delete()
                del_files += 1
        else:
            marker = obj.name
        objs = cont.get_objects(marker=marker)
else:
    print "You said no.\nEXITING"
    sys.exit()
print "All Done.\n%d Files Were Removed\nBye." % (del_files)
