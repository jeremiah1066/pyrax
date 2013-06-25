#Imports
import sys
import argparse
from novaclient import exceptions as ne
try:
  import pyrax
  import pyrax.exceptions as exc
except ImportError:
    print "Pyrax Not Found\nPlease install Pyrax\nhttp://tinyurl.com/absxgak"
    sys.exit()
"""Usage .py USER_NAME API_KEY RSA_FILE NAMING_SCHEME NUM_OF_SERVES"""
#Arg Check
parser = argparse.ArgumentParser(description="Secure Build Script")
parser.add_argument(dest='user_name', metavar='Username', type=str, help='UserName')
parser.add_argument(metavar='API_Key', dest='api_key', type=str, help='API-KEY')
parser.add_argument('-k',metavar='Pub_Key', dest='local_file', type=str, help='Pub_Key Location', required=False)
parser.add_argument('-N',metavar='Server_Name', dest='serv_name', type=str,  help='Nameing Convention of Server', default='server')
parser.add_argument('-n',metavar='#Servers', dest='num_of_servers', type=int, help='Number Of Servers To Build', default=1)
parser.add_argument('-d', required=False, dest='data_center', type=str, help='DFW,ORD,SYD,LON', default='DFW')
parser.add_argument('-l', required=False, action='store_true', help='List Image IDs', dest='list_images')
parser.add_argument('-f', required=False, action='store_true', help='List Flavors', dest='list_flavs')
parser.add_argument('-i', required=False, dest='server_id', type=str, help='Provide Image ID for Build',default='da1f0392-8c64-468f-a839-a9e56caebf07', metavar='image_id')
parser.add_argument('-L', required=False, dest='load_bal_id', type=str, help='ID of Load Balencer to Build server behind')
parser.add_argument('-LL', required=False, action='store_true', help='List Load Balencers and IDs', dest='list_load_balencers')
args = parser.parse_args()
#Auth Section
pyrax.set_setting("identity_type", "rackspace")
try:
	pyrax.set_credentials(args.user_name, args.api_key, region=args.data_center.upper())
except exc.AuthenticationFailed:
    print "Authentication Failed\nUsername or API-Key may be incorrect"
    sys.exit()


#Read and set RSA key file for use on server
cs = pyrax.cloudservers
#list images
def image_check():
	try:
		cloud_serv_images = cs.images.list()
	except ne.EndpointNotFound:
		print "Wrong Account Type For The DC You Selected"
		sys.exit()
	for img in cloud_serv_images:
		print 'Name:',img.name,'\n','ID:',img.id,'\n'
	sys.exit()
#list flavors 
def flav_lister():
	try:
		flvs = cs.flavors.list()
	except ne.EndpointNotFound:
		print "Wrong Account Type For The DC You Selected"
		sys.exit()
	for flv in flvs:
		print "ID: ",flv.id
		print flv.name
		print "Memory: ",flv.ram
		print "Disk: ",flv.disk
		print "vCPUs: ",flv.vcpus
		print
	sys.exit()
def list_load_balencers_id():
	clb = pyrax.cloud_loadbalancers
	try: 
		clb_list = clb.list()
	except ne.EndpointNotFound:
		print "Wrong Account Type For The DC You Selected"
		sys.exit()
	print "**Load Balencer List**"
	for i in clb_list:
		print 'Name:',i.name
		print 'ID:',i.id
		print 'Port:',i.port
		print
	sys.exit()

if args.list_images is True:
	image_check()
if args.list_flavs is True:
	flav_lister()
if args.list_load_balencers is True:
	list_load_balencers_id()

if args.local_file is not None:
	f = open(args.local_file, 'r')
	rsa_file = f.read()
	files = {"/root/.ssh/authorized_keys": rsa_file}
else:
	files = None


server_obj = []
server_private_ip_list = []
#Server Build 
def build_behind_load_balencers(load_balancer_id, priv_ip_listing):
	clb = pyrax.cloud_loadbalancers
	lb = clb.list()
	lb_listing = []
	lb_porter = []
	for i in lb:
		if str(i.id) == load_balancer_id:
			lb_listing.append(i)
			lb_porter.append(i.port)
	lb = lb_listing[0]
	for servers_priv in priv_ip_listing:
		print servers_priv
		new_node = clb.Node(address=servers_priv, port=lb_porter[0], condition="ENABLED")
		lb.add_nodes([new_node])

def server_check(server_list):
	for server in server_list:
		pyrax.utils.wait_until(server, "status", ["ACTIVE","ERROR"], interval=30, attempts=0, verbose=True)

for num in range(args.num_of_servers):
	b_serv_name = args.serv_name + str(num + 1)
	try:
		server = cs.servers.create(b_serv_name, args.server_id, "2", files=files)
	except ne.EndpointNotFound:
		print "Wrong Account Type For The DC You Selected"
		sys.exit()
	print b_serv_name
	server_obj.append(server)
#Wait Until Loop for all servers
server_check(server_obj)
#Check for errors and print IP Addresses after build. 
for server in server_obj:
	if server.status == "ERROR":
		curr_img = server.image
		server.rebuild(curr_img)

for server in server_obj:
	if len(server.networks['public'][0]) > 15:
		print server.networks['public'][1]
	else:
		print server.networks['public'][0]
	server_private_ip_list.append(server.networks['private'][0])
	if files is None:
			print "Admin Password:", server.adminPass



if len(args.load_bal_id) is not 0:
	build_behind_load_balencers(args.load_bal_id, server_private_ip_list)
