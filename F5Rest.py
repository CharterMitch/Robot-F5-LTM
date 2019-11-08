from pathlib import Path

from robot.api.deco import keyword
from robot.api import logger
from robot.utils import ConnectionCache

from f5.bigip import ManagementRoot
from f5.utils.responses.handlers import Stats
from f5.sdk_exception import LazyAttributesRequired

# logger.warn("Importing F5 REST library")


class F5Rest():

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, device, user):
        self.hostname = device['host']
        self.user = user
        self.f5_rest_connect(self.hostname, self.user)

    def f5_rest_connect(self, hostname, user):
        # logger.warn('Connecting to F5 {}'.format(hostname))
        try:
            self.mgmt = ManagementRoot(
                hostname,
                user['username'],
                user['password']
                )
        except:
            AssertionError("Unable to connect to F5 REST API. \
                            Check settings.yaml.")

    @keyword('load tmsh ${file}')
    def load_tmsh(self, file):
        # Base config is located in this same directory
        # Not linux compatible?
        file = str(Path(__file__).parent.absolute()) + "\\" + file
        with open(file, 'r') as fp:
            for line in fp:
                if '#' not in line and len(line) > 4:
                    # logger.warn("Sending command {}".format(line))
                    cmd = "-c '{}'".format(line.rstrip())
                    result = self.mgmt.tm.util.bash.exec_cmd(
                        'run', utilCmdArgs=cmd)
                    try:
                        if 'Error' in result.commandResult:
                            logger.warn(cmd)
                            logger.warn(result.commandResult)
                    except:
                        pass

    @keyword('load imish ${file}')
    def load_imish(self, file):
        file = str(Path(__file__).parent.absolute()) + "\\" + file
        with open(file, 'r') as fp:
            for line in fp:
                if '!' not in line and len(line) > 4:
                    if ',' in line:
                        cmd = ['enable', 'conf t'] + line.rstrip().split(',')
                    else:
                        cmd = ['enable', 'conf t'] + [line.rstrip()]
                    self.imish(cmd)

    @keyword('tmsh ${command:.+}')
    def tmsh(self, command):
        ''' Run a tmsh command on an F5 BIG-IP device.
            Return any output from the command.
        '''
        cmd = str("-c 'tmsh {}'".format(command))
        logger.info(cmd)
        command = self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd)
        try:
            # Return any errors in tmsh create/modify commands
            if 'create' in cmd or 'modify' in cmd or 'delete' in cmd \
                    and command.commandResult:
                if 'already exists' in command.commandResult:
                    logger.warn(command.commandResult)
                else:
                    raise AssertionError('Error in tmsh command: {}\n{}'
                                         .format(cmd, command.commandResult))
            # logger.warn(command.raw)
            # Return output from command
            logger.info(command.commandResult)
            return command.commandResult
        except LazyAttributesRequired:
            # Do nothing if there is no output
            # logger.warn(command.raw)
            pass

    @keyword('bash ${command:.+}')
    def bash(self, command):
        ''' Run a bash command on an F5 BIG-IP device.
            Return any output from the command.
        '''
        cmd = str("-c '{}'".format(command))
        logger.info(cmd)
        command = self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd)
        try:
            return command.commandResult.strip()
        except LazyAttributesRequired:
            return ''

    @keyword('imish -c ${commands}')
    def imish(self, commands, route_domain=0):
        ''' Run a zebos / "imish" command on an F5 BIG-IP device.
            Return any output from the command.
        '''
        command_list = str(commands).strip('[]')  # Allows lists and strings
        cmd = '-c "zebos -r {} cmd {}"'.format(route_domain, command_list)
        logger.info(cmd)
        command = self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd)
        try:
            # Return any output
            return command.commandResult
        except LazyAttributesRequired:
            return True

    @keyword('imish -r ${route_domain} -c ${commands}')
    def imish_rd(self, commands, route_domain):
        ''' Run a zebos / "imish" command in a route partition.
            Return any output from the command.
        '''
        command_list = str(commands).strip('[]')  # Allow lists and strings
        cmd = '-c "zebos -r {} cmd {}"'.format(route_domain, command_list)
        logger.info(cmd)
        command = self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd)
        try:
            # Return any output
            return command.commandResult
        except LazyAttributesRequired:
            return True

    @keyword('get pool ${pool}')
    def get_pool(self, pool):
        return self.mgmt.tm.ltm.pools.pool.load(partition='Common', name=pool)

    @keyword('get partition ${partition} pool ${pool}')
    def get_pool_in_partition(self, pool, partition):
        return self.mgmt.tm.ltm.pools.pool.load(partition=partition, name=pool)

    @keyword('get stats for pool ${pool}')
    def get_pool_stats(self, pool):
        ''' HTTP GET an F5 pool by name in the /Common partition.
            Then load the pool members statistics and return them
            as a dictionary object.

            API Result:
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
                'status_statusReason':
                {'description': 'Pool member does not have service checking
                                 enabled'},
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
            # Create a new dictionary with the node name as the key
            dict_ = {mbr_stats.stat.nodeName.description: mbr_stats.stat}
            stats.update(dict_)
        # Return { node: node_stats_dict } to Robot Keyword
        return stats

    @keyword('get ssl profile ${profile} stats')
    def get_ssl_profile_stats(self, profile):
        pass

    @keyword('Percentage difference ${num1:\d+} ${num2:\d+}')
    def get_percent(self, num1, num2):
        ''' Get the difference between two numbers as a percent. '''
        num1 = int(num1)
        num2 = int(num2)
        if int(num1) == num2:
            return 0
        if num1 != 0 and num2 != 0:
            return (abs(num1 - num2) / max(num1, num2)) * 100.0
