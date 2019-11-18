import json
import time
from urllib.parse import urljoin, urlencode
from urllib3 import HTTPConnectionPool

import requests
from retry import retry
from robot.api.deco import keyword
from robot.api import logger


class IxLoadRobot:

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    JSON_HEADER = {'content-type': 'application/json'}

    def __init__(self, site_url, ixload_version):
        ''' Initialize a connection to the IXLoad API.

            Args:
            - site_url - URL to IXLoad API
                Example: http://server:port/api/v0/
                Keep the trailing / at the end of the site_url
            - ixload_version - Actual version of the REST API
                The exact version is required to start the IXLoad API
        '''
        self.site_url = site_url
        self.ixload_version = ixload_version
        self.session_started = False
        self.s = requests.Session()
        self.s.mount('http://', requests.adapters.HTTPAdapter(
            pool_connections=1,
            max_retries=3
        ))
        self.create_session()

    def __del__(self):
        ''' Cleanup connections and sessions once python exits.

            Deletes the IXLoad Session from the IXLoad API server
            Closes the HTTPConnectionPool
        '''
        self.s.delete(self.url, headers=self.JSON_HEADER)
        self.s.close()

    @property
    def url(self):
        ''' Return the full URL with session ID for HTTP requests '''
        # http://server:port/api/v0/sessions/45/
        return urljoin(self.site_url, self.session_id)

    def create_session(self):
        ''' This method is used to create a new IXLoad session.

            Sessions are built on the API server and used in all
            further requests. For now this is simply a placeholder
            on the API server.
        '''
        logger.info('Create IXIA Session.')
        data = {"ixLoadVersion": self.ixload_version}
        data = json.dumps(data)
        _url = urljoin(self.site_url, 'sessions')
        reply = self.s.post(_url, data=data, headers=self.JSON_HEADER)
        #  reply.headers['Location'] = '/api/v0/sessions/45'
        try:
            # Add a trailing slash to the session_id so it is "absolute"
            self.session_id = reply.headers['Location'] + '/'
        except KeyError:
            raise AssertionError("Unable to create session. {}"
                                 .format(reply.text))
        return reply

    def start_session(self):
        ''' Send an HTTP Post to the IXIA API to Start the Session.

            This is similar to opening the IXLoad GUI on the server
            itself and takes a while to load.

            This must be done before issuing operations commands!
        '''
        if not self.session_started:
            logger.warn("Sending 'start' to IXIA API Session. ~10 seconds...")
            _url = urljoin(self.url, 'operations/start')
            reply = self.s.post(_url, headers=self.JSON_HEADER)
            if not reply.status_code == 202:
                AssertionError("Unable to start session.")
            self.wait(reply)
            self.session_started = True

    @keyword('load rxf ${rxf_file_path}')
    def load_rxf(self, rxf_file_path):
        ''' Load an RXF file on the remote IXLoad Server '''
        self.start_session()
        # Cleanup file path replacing 's and whitespace
        file_path = rxf_file_path.replace("'", "").strip()
        logger.warn("Loading RXF file {}. Takes ~3 minutes.".format(file_path))
        data = json.dumps({"fullPath": file_path})
        operation = 'loadTest'
        self._test_operation(operation, data=data)
        self.apply_config()

    def apply_config(self):
        self._test_operation('applyConfiguration')

    @keyword("Start IXLoad Test")
    def start_test(self):
        ''' Start the currently loaded test. '''
        logger.warn("Starting IXIA Test...")
        self.apply_config()
        self._test_operation('runTest')

    @keyword("Stop IXLoad Test")
    def stop_test(self):
        ''' Stop the currently loaded test. '''
        logger.info("Stopping IXIA Test ...")
        url = urljoin(self.url, 'ixload/test/activeTest')
        r = self.s.get(url)
        if r.json()['currentState'] == 'Running':
            self._test_operation('gracefulStopRun')

    @keyword("Gather IXLoad Stats")
    def gather_stats(self):
        logger.warn('Gathering stats while IXIA test runs.')
        _dict = {}
        test_url = urljoin(self.url, 'ixload/test/activeTest')
        stats_url = urljoin(self.url, 'ixload/stats/HTTPClient/values')
        r = self.s.get(test_url)
        if r.json()['currentState'] != 'Running':
            logger.warn('Please start an IXIA test before gathering stats.')
        while r.json()['currentState'] == 'Running':
            # Add stats to the dictionary placeholder
            _dict.update(self.s.get(stats_url).json())
            time.sleep(4)
            r = self.s.get(test_url)
        return _dict

    @keyword("IXLoad Chart ${stats} ${stats_wanted}")
    def create_html_chart(self, stats, stats_wanted):
        ''' Create an HTML chart from IXLoad stats gathered from the
            gather_stats command / IXIA API.

            A list of available stats for your test can be found in the API:
            /api/v0/sessions/<session>/ixload/stats/HTTPClient/availableStats

            Example robot use:
            ${stats}=   Gather IXLoad Stats
            @{list}=    Create List   HTTP Concurrent Connections ...
            ${chart}=   IXLoad Chart ${stats} @list
            Log         ${chart}
        '''
        import pandas
        import mpld3
        import matplotlib.pyplot as plt
        df = pandas.DataFrame.from_dict(r.json(), orient='index')
        # Log statistics as an HTML chart
        logger.info(df.to_html(), html=True)
        # Convert index from miliseconds to seconds (from test start)
        x = df.index.astype(int).to_numpy() / 1000
        # Create a base matplot figure
        fig = plt.figure(figsize=(18, 16), dpi=80)
        fig, ax = plt.subplots()
        for name in stats_wanted:
            try:
                # Add a new line chart to the graph
                y = list(df[name])
                ax.plot(x, y, lw=1, alpha=0.8, label=name)
            except KeyError:
                pass
        # Add the label to bottom of graph
        ax.set_xlabel('Time (s)')
        # Display the legend
        ax.legend()
        # Return graph as HTML (so we can log it to robot)
        return mpld3.fig_to_html(fig)

    @retry(tries=5, delay=5)
    def _test_operation(self, operation, data={}):
        ''' Send an HTTP POST to a given test operation URL
            then wait for the operation to complete.

            http://<host>:<port>/api/v0/sessions/<session id>/
            ixload/test/operations/<operation>

            Added retry library decorator as stoping tests, starting tests,
            etc. can leave the API in an odd state for many seconds and
            programming for all the interim states would require a lot
            more logic than just a quick resend of the command.
        '''
        operation = 'ixload/test/operations/{}'.format(operation)
        _url = urljoin(self.url, operation)
        reply = self.s.post(_url, data=data, headers=self.JSON_HEADER)
        self.wait(reply)
        return reply

    def load_local_rxf(self, rxf_file_path):
        # TODO: Upload a local file then load it?
        pass

    def wait(self, reply):
        ''' This method waits for an action to finish executing.

            It uses the reply object from the action to get the
            actions GET url. We then make a series of calls to the
            URL until the statr is finished.

            Once the aciton is finished we see if there were any errors.
        '''
        if reply.headers.get('location') is None:
            raise AssertionError('API request failed. {}'
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
                    time.sleep(0.5)
