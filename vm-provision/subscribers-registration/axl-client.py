import sys;
from lxml import etree;
from requests import Session;
from requests.auth import HTTPBasicAuth;

from zeep import Client, Settings, Plugin;
from zeep.transports import Transport;
from zeep.cache import SqliteCache;
from zeep.plugins import HistoryPlugin;
from zeep.exceptions import Fault;

# Get Arguments
USERNAME = sys.argv[1];
PASSWD = sys.argv[2];
PUBLISHER_PRODUCT_TYPE = sys.argv[3];
SUBSCRIBER_PRODUCT_TYPE = sys.argv[4];
SUBSCRIBER_HOST_NAME = sys.argv[5];
PUBLISHER_HOST_IP = sys.argv[6];
if SUBSCRIBER_PRODUCT_TYPE == 'IMP':
    IMP_DOMAIN_NAME = sys.argv[7];

# this is a local file
WSDL_URL = PUBLISHER_PRODUCT_TYPE + '/AXLAPI.wsdl'

# These are sample values for DevNet sandbox
# replace them with values for your own CUCM, if needed
AXL_URL = 'https://' + PUBLISHER_HOST_IP + ':8443/axl/';

if SUBSCRIBER_PRODUCT_TYPE == 'CUCM' or SUBSCRIBER_PRODUCT_TYPE == 'CUCX':
    PROCESS_NODE_ROLE = 'CUCM Voice/Video'
elif SUBSCRIBER_PRODUCT_TYPE == 'IMP':
    PROCESS_NODE_ROLE = 'CUCM IM and Presence'

# If you have a pem file certificate for CUCM, uncomment and define it here
#CERT = 'some.pem'

# history shows http_headers
history = HistoryPlugin()

# This class lets you view the incoming and outgoing http headers and XML
class MyLoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
        print(etree.tostring(envelope, pretty_print=True));
        return envelope, http_headers;

    def egress(self, envelope, http_headers, operation, binding_options):
        print(etree.tostring(envelope, pretty_print=True));
        return envelope, http_headers;

# Create a SOAP client session
session = Session();

#session.verify = CERT
session.verify = False
session.auth = HTTPBasicAuth(USERNAME, PASSWD);

transport = Transport(session=session, timeout=10, cache=SqliteCache());

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True);

client = Client(WSDL_URL, settings=settings, transport=transport, plugins=[MyLoggingPlugin(),history]);

service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL);

# Process Node Data
process_node_data = {
	'processNode': {
		'name': SUBSCRIBER_HOST_NAME,
		'processNodeRole': PROCESS_NODE_ROLE
	}
}

# Add IMP Domain Name if Necessary
if SUBSCRIBER_PRODUCT_TYPE == 'IMP':
    process_node_data['processNode']['cupDomain'] = IMP_DOMAIN_NAME;

print(process_node_data,"\n")

# CM Publisher:
# 	CM Subscribers		-> 'processNodeRole': 'CUCM Voice/Video'
# 	IM&P Subscribers	-> 'processNodeRole': 'CUCM IM and Presence'

# CUCx Publisher:
#	CUCx Subscribers	-> 'processNodeRole': 'CUCM Voice/Video'
#   CUCx Subscribers    -> 'cupDomain': ''

# the ** before line_data tells the Python function to expect
# an unspecified number of keyword/value pairs

try:
    app_user = service.addProcessNode(**process_node_data)
except Fault as err:
    print("Zeep error: {0}".format(err))
else:
    print("\naddApplicationServer response\n")
    print("\naddApp User\n")
    print(app_user,"\n")
    print("\nLast Sent\n")
    print(history.last_sent,"\n")
    print("\nLast Received\n")
    print(history.last_received,"\n")