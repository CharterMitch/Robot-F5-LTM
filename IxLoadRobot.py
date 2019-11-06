import os
import json
import re
import time
from urllib.parse import urljoin, urlencode
from urllib3 import HTTPConnectionPool

import requests
from robot.api.deco import keyword
from robot.api import logger


class IxLoadRobot:

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    JSON_HEADER = {'content-type': 'application/json'}

    def __init__(self, site_url, ixload_version):
        ''' Args:
            - site_url - URL to IXLoad API
            - ixload_version - Actual version of the REST API
        '''
        self.site_url = site_url
        self.ixload_version = ixload_version
        self.s = requests.Session()
        self.s.mount('http://', requests.adapters.HTTPAdapter(
            pool_connections=1,
            max_retries=3
        ))
        self.create_session()
        self.start_session()

    def __del__(self):
        ''' Delete the IXLoad Session to free up resources.
            Close the requests session.
        '''
        self.s.delete(self.url, headers=self.JSON_HEADER)
        self.s.close()

    @property
    def url(self):
        return urljoin(self.site_url, self.session_id)

    def create_session(self):
        ''' This method is used to create a new IXLoad session.
            It will return the url of the newly created session.
        '''
        data = {"ixLoadVersion": self.ixload_version}
        data = json.dumps(data)
        _url = urljoin(self.site_url, 'sessions')
        reply = self.s.post(_url, data=data, headers=self.JSON_HEADER)
        #  reply.headers['Location'] = '/api/v0/sessions/45'
        try:
            self.session_id = reply.headers['Location'] + '/'
        except KeyError:
            raise AssertionError("Unable to create session. {}"
                                 .format(reply.text))
        return reply

    def start_session(self):
        ''' Send an HTTP Post to the IXIA API to Start the Session'''
        logger.warn("Sending 'start' to IXIA API Session. ~10 seconds...")
        _url = urljoin(self.url, 'operations/start')
        reply = self.s.post(_url, headers=self.JSON_HEADER)
        if not reply.status_code == 202:
            AssertionError("Unable to start session.")
        self.wait(reply)

    def isactive(func):
        ''' Decorator to make sure session to device is active. '''
        def decorated(self, *args, **kwargs):
            # Get if the current session state is active
            reply = self.s.get(self.url)
            if not reply.json()['isActive']:
                self.start()
            return func(self, *args, **kwargs)
        return decorated

    @keyword('load rxf ${rxf_file_path}')
    def load_rxf(self, rxf_file_path):
        ''' Load and RXF file on the remote IXLoad Server '''
        # Cleanup string replacing 's and whitespace
        file_path = rxf_file_path.replace("'", "").strip()
        logger.warn("Loading RXF file {}".format(file_path))
        data = {"fullPath": file_path}
        url = 'ixload/test/operations/loadTest'
        reply = self.post(url, data=data, headers=self.JSON_HEADER)
        self.wait(reply)
        self.apply_config()
        return reply

    def apply_config(self):
        self._test_operation('applyConfiguration')

    def add_community(self):
        data = {'_object_': 'NetTraffic'}
        operation = 'ixload/test/operations/add_community'
        _url = urljoin(self.url, operation)
        self.s.post(_url, data=data, headers=self.JSON_HEADER)

    @keyword("Start IXLoad Test")
    def start_test(self):
        ''' Start the currently loaded test. '''
        logger.warn("Starting IXIA Test ...")
        self.apply_config()
        self._test_operation('runTest')

    @keyword("Stop IXLoad Test")
    def stop_test(self):
        ''' Start the currently loaded test. '''
        logger.warn("Stopping IXIA Test ...")
        self._test_operation('gracefulStopRun')

    def _test_operation(self, operation, data={}):
        ''' Send an HTTP POST to a given test operation URL
            then wait for the operation to complete.

        http://<host>:<port>/api/v0/sessions/<session id>/
            ixload/test/operations/<operation>
        '''
        operation = 'ixload/test/operations/{}'.format(operation)
        _url = urljoin(self.url, operation)
        reply = self.s.post(_url, data=data, headers=self.JSON_HEADER)
        self.wait(reply)

    def load_local_rxf(self, rxf_file_path):
        # TODO: Upload a local file then load it?
        pass

    def wait(self, reply):
        ''' This method waits for an action to finish executing.

            It uses the reply object from the action to get the
            actions GET url. It then calls that URL until the operation
            is finished or errors.
        '''
        if reply.headers.get('location') is None:
            raise AssertionError('Location headers not sent after action. {}'
                                 .format(reply.text))
        else:
            action_finished = False
            _url = reply.headers.get('location')
            _url = urljoin(self.url, _url)
            while not action_finished:
                r = self.s.get(_url)
                data = r.json()
                if data['state'] == 'finished':
                    if data['status'] == 'Successful':
                        action_finished = True
                    else:
                        errorMsg = "Error while executing action {}.\n"\
                                    .format(_url)
                        if data['status'] == 'Error':
                            errorMsg += data['error']
                        raise AssertionError(errorMsg)
                else:
                    time.sleep(0.3)

    def enableForceOwnership(self):
        return self.s.patch(
            self.url,
            data={'enableForceOwnership': True},
            header=self.JSON_HEADER
            )
