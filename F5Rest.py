from robot.api.deco import keyword
from robot.api import logger
from robot.utils import ConnectionCache

from f5.bigip import ManagementRoot
from f5.utils.responses.handlers import Stats

#logger.warn("Importing F5 REST library")

class F5Rest():

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self,device,user):
        self.hostname = device['host']
        self.user = user
        self.f5_rest_connect(self.hostname,self.user)

    def f5_rest_connect(self,hostname,user):
        #logger.warn('Connecting to F5 {}'.format(hostname))
        try:
            self.mgmt = ManagementRoot(hostname, user['username'], user['password'])
        except:
            AssertionError("Unable to connect to F5 REST API. Check settings.yaml.")

    @keyword('tmsh ${command:.+}')
    def tmsh(self,command):
        ''' Run a tmsh command on an F5 BIG-IP device.
            Return any output from the command.
        '''
        cmd = '-c "tmsh {}"'.format(command)
        return self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd).commandResult

    @keyword('imish -c ${commands}')
    def imish(self,commands,route_domain=0):
        ''' Run a zebos / "imish" command on an F5 BIG-IP device.
            Return any output from the command.
        '''
        command_list = str(commands).strip('[]') # Allows lists as well as strings?
        cmd = '-c "zebos -r {} cmd {}"'.format(route_domain, command_list)
        return self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd).commandResult

    @keyword('imish -r ${route_domain} -c ${commands}')
    def imish_rd(self,commands,route_domain):
        ''' Run a zebos / "imish" command in a route partition an F5 BIG-IP device.
            Return any output from the command.
        '''
        command_list = str(commands).strip('[]')  # Allows lists as well as strings?
        cmd = '-c "zebos -r {} cmd {}"'.format(route_domain, command_list)
        return self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd).commandResult

    @keyword('get pool ${pool} stats')
    def get_pool_stats(self,pool):
        ''' HTTP GET an F5 pool by name in the /Common partition.
            Then load the pool members statistics and return them
            as a dictionary object.

            {'/Common/example-server': {
                'addr': {'description': '2001:200:0:1300::100'},
                'connq_ageEdm': {'value': 0},
                'connq_ageEma': {'value': 0},
                'connq_ageHead': {'value': 0},
                'connq_ageMax': {'value': 0},
                'connq_depth': {'value': 0},
                'connq_serviced': {'value': 0},
                'curSessions': {'value': 0},
                'monitorRule': {'description': 'none'},
                'monitorStatus': {'description': 'unchecked'},
                'nodeName': {'description': '/Common/example-server},
                'poolName': {'description': '/Common/example-pool'},
                'port': {'value': 80},
                'serverside_bitsIn': {'value': 3998642720},
                'serverside_bitsOut': {'value': 869489671944},
                'serverside_curConns': {'value': 0},
                'serverside_maxConns': {'value': 121},
                'serverside_pktsIn': {'value': 6641290},
                'serverside_pktsOut': {'value': 72555193},
                'serverside_totConns': {'value': 98443},
                'sessionStatus': {'description': 'enabled'},
                'status_availabilityState': {'description': 'unknown'},
                'status_enabledState': {'description': 'enabled'},
                'status_statusReason': {'description': 'Pool member does not have service checking enabled'},
                'totRequests': {'value': 98443}
            }, ...
        '''
        stats = {}
        my_pool = self.mgmt.tm.ltm.pools.pool.load(
            partition='Common',
            name=pool
            )
        my_pool_mbrs = my_pool.members_s.get_collection()
        for pool_mbr in my_pool_mbrs:
            mbr_stats = Stats(pool_mbr.stats.load())
            dict_ = {mbr_stats.stat.nodeName.description: mbr_stats.stat}
            stats.update(dict_)
        return stats

