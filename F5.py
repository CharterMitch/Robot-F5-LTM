import functools
from robot.api.deco import keyword
from robot.api import logger
from robot.utils import ConnectionCache

import bigsuds
from f5.bigip import ManagementRoot

#logger.warn("Importing custom F5 library")

def ignore_duplicates(function):
        ''' A decorator that wraps the passed in function and ignores
            any F5 big-ip duplicate creation exceptions.
        '''
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except bigsuds.OperationFailed as e:
                if 'already exists' in str(e):
                    logger.warn(e)
                    pass
                else:
                    raise
        return wrapper

class F5:

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
        self.alias = None
        self.connections = dict()

    def connect_to_f5(self,device,user):
        logger.warn('Connecting to F5 {}'.format(device['host']))
        try:
            self.c = bigsuds.BIGIP(
                hostname = device['host'],
                username = user['username'],
                password = user['password']
            )
        except:
            AssertionError("Unable to connect to F5. Check settings.yaml.")

    # Create Functions

    @keyword('Create http virtual server ${name} ip ${ip} pool ${pool} port ${port:\d+}')
    @ignore_duplicates
    def create_http_virtual_server(self,name,ip,pool,port):
        ''' Create a basic F5 HTTP virtual server.

            Usage:
            *** Test Cases ***
            Test virtual server creation
                Create http virtual server named test-vs-http ip 1.1.1.1 pool test-pool port 80
                ...
            
            https://clouddocs.f5.com/api/icontrol-soap/LocalLB__VirtualServer__create.html
        '''
        definition = {
            'name': name,
            'address': ip,
            'port': port,
            'protocol': 'PROTOCOL_TCP'
        }
        resource =  { 
            'type': 'RESOURCE_TYPE_POOL',
            'default_pool_name': pool
            }
        profile = [{
            'profile_context': 'PROFILE_CONTEXT_TYPE_ALL',
            'profile_name': '/Common/tcp'
            }]
        logger.warn('Creating F5 virtual server {} with pool {}.'.format(name, pool))
        self.c.LocalLB.VirtualServer.create(
            [definition],
            ['255.255.255.255'],
            [resource],
            [profile]
            )

    @keyword('Create node ${ip}')
    @ignore_duplicates
    def create_node(self,ip):
        ''' Create a basic F5 node.

            Usage:
            *** Test Cases ***
            Test node creation
                Create node 1.1.1.1 
        '''
        logger.warn('Creating F5 node {}.'.format(ip))
        self.c.LocalLB.NodeAddressV2.create([ip],[ip],[0])

    @keyword('Create nodes ${nodes}')
    @ignore_duplicates
    def create_nodes(self,nodes):
        ''' Create F5 nodes from a list of IP addresses.
            The node names will be the IP address.

            Usage:
            *** Test Cases ***
            Test nodes creation
                Create nodes [1.1.1.1,2.2.2.2]
        '''
        logger.warn('Creating nodes from list {}.'.format(nodes))
        connection_limits = [0] * len(nodes)
        self.c.LocalLB.NodeAddressV2.create(nodes,nodes,connection_limits)

    @keyword('Create pool ${pool} using ${nodes} and port ${port:\d+}')
    @ignore_duplicates
    def create_pool(self,pool,nodes,port):
        ''' Create an initial F5 pool using the round robin load balancing method.
        
            https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
        '''
        logger.warn('Creating pool {}'.format(pool))
        lb_method = 'LB_METHOD_ROUND_ROBIN'
        address_ports = [{'address': x,'port': port} for x in nodes]
        self.c.LocalLB.Pool.create_v2([pool],[lb_method],[address_ports])

    # Set Functions

    @keyword('Set pool ${pool} method ${method}')
    def set_pool_method(self,pool,method):
        self.c.LocalLB.Pool.set_lb_method([pool],[method])

    def set_pool_ratio(self,pool,ratio1,ratio2):
        members = self.c.LocalLB.Pool.get_member_v2([pool])
        self.c.LocalLB.Pool.set_member_ratio([pool],members,[[ratio1,ratio2]])

    @keyword('Set route advertisement ${virtual_address}')
    def set_route_advertisement(self,virtual_address):
        ''' Set a virtual address to be advertised by BGP. '''
        state = 'RA_TYPE_SELECTIVE'
        self.c.LocalLB.VirtualAddressV2.set_route_advertisement_state_v2(
            [virtual_address],
            [state]
            )

    # Get Functions

    @keyword('Get total connections from pool ${pool}')
    def get_pool_stats(self,pool):
        stats = self.c.LocalLB.Pool.get_all_member_statistics([pool])
        stats_dict = {}
        for member in stats[0]['statistics']:
            address = (member['member']['address'].replace('/Common/',''))
            total_cons = member['statistics'][6]['value']['low']
            total_connections = member['statistics'][6]['value']['low']
            stats_dict.update({address: total_connections})
        return stats_dict

    @keyword('Percent difference between ${num1:\d+} and ${num2:\d+}')
    def get_difference(self, num1, num2):
        ''' Get the difference between two numbers as a percent. '''
        num1 = int(num1)
        num2 = int(num2)
        if int(num1) == num2:
            return 0
        if num1 != 0 and num2 != 0:
            return (abs(num1 - num2) / max(num1,num2)) * 100.0
    
    # Reset functions

    @keyword('Reset pool statistics')
    def reset_pool(self, pool):
        self.c.LocalLB.Pool.reset_statistics([pool])

    # Delete functions 

    @keyword('Delete nodes ${nodes}')
    def delete_nodes(self,nodes):
        ''' Delete nodes from the F5 using a list of IP addresses.
            The node names will be the IP address.
        '''
        self.c.LocalLB.NodeAddressV2.delete_node_address(nodes)
    
    @keyword('Delete pool ${pool}')
    def delete_pool(self, pool):
        self.c.LocalLB.Pool.delete_pool([pool])

    @keyword('Delete virtual server ${name}')
    def delete_server(self, name):
        self.c.LocalLB.VirtualServer.delete_virtual_server([name])
