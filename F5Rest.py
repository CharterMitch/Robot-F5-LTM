from robot.api.deco import keyword
from robot.api import logger
from robot.utils import ConnectionCache

from f5.bigip import ManagementRoot

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

    @keyword('imish -c ${commands}')
    def imish(self,commands,route_domain=0,):
        command_list = str(commands).strip('[]')
        cmd = '-c "zebos -r {} cmd {}"'.format(route_domain, command_list)
        return self.mgmt.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd).commandResult
