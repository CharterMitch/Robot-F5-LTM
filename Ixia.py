# https://github.com/CiscoTestAutomation/genietrafficgen/blob/master/src/genie/trafficgen/ixianative.py

# Python
import re
import os
import csv
import time
import logging
from shutil import copyfile
from prettytable import PrettyTable, from_csv

# Robot
from robot.api import logger

# IxNetwork Native
try:
    from IxNetwork import IxNet
except ImportError as e:
    raise ImportError("IxNetwork package is not installed in virtual env - "
                      "https://pypi.org/project/IxNetwork/") from e


logger.warn("Importing custom IXIA library")

class Ixia():
    def __init__(self, *args, **kwargs):

        ROBOT_LIBRARY_SCOPE = "GLOBAL"

        # Init class variables
        self.ixNet = IxNet()
        self._is_connected = False
        self.virtual_ports = []
        self._robot_view = None
        self._robot_page = None
        self._golden_profile = PrettyTable()
        self._flow_statistics_table = PrettyTable()
        self._traffic_statistics_table = PrettyTable()
        # Valid QuickTests (to be expanded as tests have been validated)
        self.valid_quicktests = [
            'rfc2544frameLoss',
            'rfc2544throughput',
            'rfc2544back2back'
            ]

        # Make sure all variables are included in initialization
        for key in ['api_server_ip','tcl_port','port_list','name',
                    'ixnetwork_version','chassis_ip','license_server_ip']:
            try:
                setattr(self, key, kwargs.get(key))
            except Exception:
                raise AssertionError("Argument '{k}' is not found in testbed "
                                    "YAML for device '{d}'".\
                                    format(k=key, d='ixia'))

    def isconnected(func):
        '''Decorator to make sure session to device is active
            There is limitation on the amount of time the session can be active
            to IxNetwork API server. However, there are no way to verify if the
            session is still active unless we test sending a command.
            '''
        def decorated(self, *args, **kwargs):
            # Check if connected
            try:
                logger.propagate = False
                self.ixNet.getAttribute('/globals', '-buildNumber')
            except Exception:
                self.connect()
            finally:
                logger.propagate = True
            return func(self, *args, **kwargs)
        return decorated


    def connect(self):
        '''Connect to Ixia'''
        logger.info("Connecting to IXIA")
        try:
            connect = self.ixNet.connect(self.ixnetwork_api_server_ip,
                                        '-port', self.ixnetwork_tcl_port,
                                        '-version', self.ixnetwork_version,
                                        '-setAttribute', 'strict')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Failed to connect to device '{d}' on port "
                                "'{p}'".format(d=self.name,
                                            p=self.ixnetwork_tcl_port)) from e
        # Verify return
        try:
            assert connect == _PASS
        except AssertionError as e:
            logger.error(connect)
            raise AssertionError("Failed to connect to device '{d}' on port "
                                "'{p}'".format(d=self.name,
                                            p=self.ixnetwork_tcl_port)) from e
        else:
            self._is_connected = True
            logger.info("Connected to IxNetwork API server on TCL port '{p}'".\
                        format(d=self.name, p=self.ixnetwork_tcl_port))


    def disconnect(self):
        '''Disconnect from traffic generator device'''

        # Execute disconnect on IxNetwork
        try:
            disconnect = self.ixNet.disconnect()
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to disconnect from '{}".\
                                format(self.name))

        # Verify return
        try:
            assert disconnect == _PASS
        except AssertionError as e:
            logger.error(disconnect)
            raise AssertionError("Unable to disconnect from '{}'".\
                                format(self.name))
        else:
            self._is_connected = False
            logger.info("Disconnected from IxNetwork API server on TCL port '{p}'".\
                        format(d=self.name, p=self.ixnetwork_tcl_port))


    @isconnected
    def load_configuration(self, configuration, wait_time=60):
        '''Load static configuration file onto Ixia'''
        logger.info("Loading configuration")
        try:
            load_config = self.ixNet.execute('loadConfig', 
                                                self.ixNet.readFrom(configuration))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to load configuration file '{f}' onto "
                                "device '{d}'".format(d=self.name,
                                                f=configuration)) from e
        # Verify return
        try:
            assert load_config == _PASS
        except AssertionError as e:
            logger.error(load_config)
            raise AssertionError("Unable to load configuration file '{f}' onto "
                                "device '{d}'".format(d=self.name,
                                                f=configuration)) from e
        else:
            logger.info("Loaded configuration file '{f}' onto device '{d}'".\
                    format(f=configuration, d=self.name))

        # Wait after loading configuration file
        logger.info("Waiting for '{}' seconds after loading configuration...".\
                    format(wait_time))
        time.sleep(wait_time)

        # Verify traffic is in 'unapplied' state
        logger.info("Verify traffic is in 'unapplied' state after loading configuration")
        try:
            assert self.get_traffic_attribute(attribute='state') == 'unapplied'
        except AssertionError as e:
            raise AssertionError("Traffic is not in 'unapplied' state after "
                                "loading configuration onto device '{}'".\
                                format(self.name)) from e
        else:
            logger.info("Traffic in 'unapplied' state after loading configuration "
                        "onto device '{}'".format(self.name))


    @isconnected
    def start_all_protocols(self, wait_time=60):
        '''Start all protocols on Ixia'''

        logger.info("Starting routing engine")

        # Start protocols on IxNetwork
        try:
            start_protocols = self.ixNet.execute('startAllProtocols')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to start all protocols on device '{}'".\
                                format(self.name)) from e
        # Verify return
        try:
            assert start_protocols == _PASS
        except AssertionError as e:
            logger.error(start_protocols)
            raise AssertionError("Unable to start all protocols on device '{}'".\
                                format(self.name)) from e
        else:
            logger.info("Started protocols on device '{}".format(self.name))

        # Wait after starting protocols
        logger.info("Waiting for '{}' seconds after starting all protocols...".\
                    format(wait_time))
        time.sleep(wait_time)


    @isconnected
    def stop_all_protocols(self, wait_time=60):
        '''Stop all protocols on Ixia'''

        logger.info("Stopping routing engine")

        # Stop protocols on IxNetwork
        try:
            stop_protocols = self.ixNet.execute('stopAllProtocols')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to stop all protocols on device '{}'".\
                                format(self.name)) from e
        # Verify return
        try:
            assert stop_protocols == _PASS
        except AssertionError as e:
            logger.error(stop_protocols)
            raise AssertionError("Unable to stop all protocols on device '{}'".\
                                format(self.name)) from e
        else:
            logger.info("Stopped protocols on device '{}'".format(self.name))

        # Wait after stopping protocols
        logger.info("Waiting for  '{}' seconds after stopping all protocols...".\
                    format(wait_time))
        time.sleep(wait_time)


    @isconnected
    def apply_traffic(self, wait_time=60):
        '''Apply L2/L3 traffic on Ixia'''
        try:
            apply_traffic = self.ixNet.execute('apply', '/traffic')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to apply L2/L3 traffic on device '{}'".\
                                format(self.name)) from e
        # Verify return
        try:
            assert apply_traffic == _PASS
        except AssertionError as e:
            logger.error(apply_traffic)
            raise AssertionError("Unable to apply L2/L3 traffic on device '{}'".\
                                format(self.name)) from e
        else:
            logger.info("Applied L2/L3 traffic on device '{}'".format(self.name))

        # Wait after applying L2/L3 traffic
        logger.info("Waiting for '{}' seconds after applying L2/L3 traffic...".\
                    format(wait_time))
        time.sleep(wait_time)

        # Verify traffic is in 'stopped' state
        logger.info("Verify traffic is in 'stopped' state...")
        try:
            assert self.get_traffic_attribute(attribute='state') == 'stopped'
        except Exception as e:
            raise AssertionError("Traffic is not in 'stopped' state after "
                                "applying L2/L3 traffic on device '{}'".\
                                format(self.name))
        else:
            logger.info("Traffic is in 'stopped' state after applying traffic as "
                        "expected")


    @isconnected
    def send_arp(self, wait_time=10):
        '''Send ARP to all interfaces from Ixia'''
        logger.info("Sending ARP to all interfaces from Ixia")
        # Send ARP from Ixia
        try:
            send_arp = self.ixNet.execute('sendArpAll')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to send ARP to all interfaces on device"
                                " '{}'".format(self.name)) from e
        # Verify return
        try:
            assert send_arp == _PASS
        except AssertionError as e:
            logger.error(send_arp)
            raise AssertionError("Unable to send ARP to all interfaces on device"
                                " '{}'".format(self.name)) from e
        else:
            logger.info("Sent ARP to all interfaces on device '{}'".\
                    format(self.name))

        # Wait after sending ARP
        logger.info("Waiting for '{}' seconds after sending ARP to all interfaces...".\
                    format(wait_time))
        time.sleep(wait_time)


    @isconnected
    def send_ns(self, wait_time=10):
        '''Send NS to all interfaces from Ixia'''
        try:
            send_ns = self.ixNet.execute('sendNsAll')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error sending NS to all interfaces on device "
                                "'{}'".format(self.name)) from e
        try:
            assert send_ns == _PASS
        except AssertionError as e:
            logger.error(send_ns)
            raise AssertionError("Error sending NS to all interfaces on device "
                                "'{}'".format(self.name)) from e
        else:
            logger.info("Sent NS to all interfaces on device '{}'".\
                        format(self.name))

        # Wait after sending NS
        logger.info("Waiting for '{}' seconds after sending NS...".\
                    format(wait_time))
        time.sleep(wait_time)


    @isconnected
    def start_traffic(self, wait_time=60):
        '''Start traffic on Ixia'''
        logger.info("Starting L2/L3 traffic")
        # Check if traffic is already started
        state = self.get_traffic_attribute(attribute='state')
        running = self.get_traffic_attribute(attribute='isTrafficRunning')
        if state == 'started' or running == 'true':
            logger.info("Traffic is already running and in 'started' state")
            return

        # Start traffic on IxNetwork
        try:
            start_traffic = self.ixNet.execute('start', '/traffic')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to start traffic on device '{}'".\
                                format(self.name)) from e
        # Verify return
        try:
            assert start_traffic == _PASS
        except AssertionError as e:
            logger.error(start_traffic)
            raise AssertionError("Unable to start traffic on device '{}'".\
                                format(self.name)) from e
        else:
            logger.info("Started L2/L3 traffic on device '{}'".\
                        format(self.name))

        # Wait after starting L2/L3 traffic for streams to converge to steady state
        logger.info("Waiting for '{}' seconds after after starting L2/L3 traffic "
                    "for streams to converge to steady state...".format(wait_time))
        time.sleep(wait_time)

        # Check if traffic is in 'started' state
        logger.info("Checking if traffic is in 'started' state...")
        current_state = self.get_traffic_attribute(attribute='state')
        try:
            assert current_state == 'started'
        except AssertionError as e:
            logger.error(e)
            raise AssertionError("Traffic is not in 'started' state - traffic "
                                "state is '{}'".format(current_state))
        else:
            logger.info("Traffic is in 'started' state")


    @isconnected
    def stop_traffic(self, wait_time=60):
        '''Stop traffic on Ixia'''
        logger.info("Stopping L2/L3 traffic")
        # Check if traffic is already stopped
        state = self.get_traffic_attribute(attribute='state')
        running = self.get_traffic_attribute(attribute='isTrafficRunning')
        if state == 'stopped' or running == 'false':
            logger.info("Traffic is not running or already in 'stopped' state")
            return
        # Stop traffic on IxNetwork
        try:
            stop_traffic = self.ixNet.execute('stop', '/traffic')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to stop traffic on device '{}'".\
                                format(self.name)) from e
        # Verify result
        try:
            assert stop_traffic == _PASS
        except AssertionError as e:
            logger.error(stop_traffic)
            raise AssertionError("Unable to stop traffic on device '{}'".\
                                format(self.name)) from e
        else:
            logger.info("Stopped L2/L3 traffic on device '{}'".\
                        format(self.name))
        # Wait after starting L2/L3 traffic for streams to converge to steady state
        logger.info("Waiting for '{}' seconds after after stopping L2/L3 "
                    "traffic...".format(wait_time))
        time.sleep(wait_time)
        # Check if traffic is in 'stopped' state
        logger.info("Checking if traffic is in 'stopped' state...")
        current_state = self.get_traffic_attribute(attribute='state')
        try:
            assert current_state == 'stopped'
        except AssertionError as e:
            logger.error(e)
            raise AssertionError("Traffic is not in 'stopped' state - traffic "
                                "state is '{}'".format(current_state))
        else:
            logger.info("Traffic is in 'stopped' state")


    @isconnected
    def clear_statistics(self, wait_time=10, clear_port_stats=True, clear_protocol_stats=True):
        '''Clear all traffic, port, protocol statistics on Ixia'''
        try:
            res_clear_all = self.ixNet.execute('clearStats')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to clear all statistics") from e
        else:
            try:
                assert res_clear_all == _PASS
            except AssertionError as e:
                logger.error(res_clear_all)
            else:
                logger.info("Successfully cleared traffic statistics on "
                            "device '{}'".format(self.name))

        if clear_port_stats:
            logger.info("Clearing port statistics...")
            try:
                res_clear_port = self.ixNet.execute('clearPortsAndTrafficStats')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to clear port statistics") from e
            else:
                try:
                    assert res_clear_port == _PASS
                except AssertionError as e:
                    logger.error(res_clear_port)
                else:
                    logger.info("Successfully cleared port statistics on "
                                "device '{}'".format(self.name))

        if clear_protocol_stats:
            logger.info("Clearing protocol statistics...")
            try:
                res_clear_protocol = self.ixNet.execute('clearProtocolStats')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to clear protocol statistics") from e
            else:
                try:
                    assert res_clear_protocol == _PASS
                except AssertionError as e:
                    logger.error(res_clear_protocol)
                else:
                    logger.info("Successfully cleared protocol statistics on "
                                "device '{}'".format(self.name))
        # Wait after clearing statistics
        logger.info("Waiting for '{}' seconds after clearing statistics".\
                    format(wait_time))
        time.sleep(wait_time)


    @isconnected
    def create_robot_statistics_view(self, view_create_interval=30, view_create_iteration=10, disable_tracking=False, disable_port_pair=False):
        '''Creates a custom TCL View named "Robot" with the required stats data'''
        logger.info("Creating new custom IxNetwork traffic statistics view 'Robot'")
        # Default statistics to add to custom 'Robot' traffic statistics view
        default_stats_list = ["Frames Delta",
                                "Tx Frames",
                                "Rx Frames",
                                "Loss %",
                                "Tx Frame Rate",
                                "Rx Frame Rate",
                                ]

        # Delete any previously created TCL Views called Robot
        logger.info("Deleting any existing traffic statistics view 'Robot'...")
        try:
            for view in self.ixNet.getList('/statistics', 'view'):
                if self.ixNet.getAttribute(view, '-caption') == 'Robot':
                    self.ixNet.remove(view)
                    self.ixNet.commit()
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to delete any previously created "
                                "traffic statistics view named 'Robot'.") from e

        # Enable 'Traffic Items' filter if not present
        if disable_tracking:
            logger.info("Not enabling 'Traffic Items' filter for all traffic streams")
        else:
            self.enable_flow_tracking_filter(tracking_filter='trackingenabled0')

        # Enable 'Source/Dest Port Pair' filter if not present
        if disable_port_pair:
            logger.info("Not enabling 'Source/Dest Port Pair' filter for all traffic streams")
        else:
            self.enable_flow_tracking_filter(tracking_filter='sourceDestPortPair0')

        # Create a new TCL View called Robot
        logger.info("Creating a new traffic statistics view 'Robot'")
        try:
            self._robot_view = self.ixNet.add(self.ixNet.getRoot() + '/statistics', 'view')
            self.ixNet.setAttribute(self._robot_view, '-caption', 'Robot')
            self.ixNet.setAttribute(self._robot_view, '-type', 'layer23TrafficFlow')
            self.ixNet.setAttribute(self._robot_view, '-visible', 'true')
            self.ixNet.commit()
            self._robot_view = self.ixNet.remapIds(self._robot_view)
            self._robot_view = self._robot_view[0]
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to create new traffic statistics view "
                                "named 'Robot'.") from e

        # Populate traffic stream statistics in new TCL View 'Robot'
        logger.info("Populating custom IxNetwork traffic statistics view 'Robot'...")
        try:
            # Get available traffic items, port filters
            avail_traffic_items = self.ixNet.getList(self._robot_view, 'availableTrafficItemFilter')
            avail_port_filter_list = self.ixNet.getList(self._robot_view, 'availablePortFilter')
            layer23_traffic_flow_filter = self.ixNet.getList(self._robot_view, 'layer23TrafficFlowFilter')

            # Set attributes
            self.ixNet.setAttribute(self._robot_view+'/layer23TrafficFlowFilter', '-trafficItemFilterIds', avail_traffic_items)
            self.ixNet.setAttribute(self._robot_view+'/layer23TrafficFlowFilter', '-portFilterIds', avail_port_filter_list)
            #self.ixNet.setAttribute(self._robot_view+'/layer23TrafficFlowFilter', '-egressLatencyBinDisplayOption', 'showIngressRows')

            # RemapIds
            self._robot_view = self.ixNet.remapIds(self._robot_view)[0]

            # Add specified columns to TCL view
            availableStatList = self.ixNet.getList(self._robot_view, 'statistic')
            for statName in default_stats_list:
                logger.info("Adding '{}' statistics to 'Robot' view".format(statName))
                stat = self._robot_view + '/statistic:' + '"{}"'.format(statName)
                if stat in availableStatList:
                    self.ixNet.setAttribute(stat, '-enabled', 'true')
                    self.ixNet.commit()
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to add Tx/Rx Frame Rate, Loss %, Frames"
                        " delta data to 'Robot' traffic statistics view") from e

        # Create and set enumerationFilter to descending
        logger.info("Get enumerationFilter to add custom columns to view")
        try:
            # Get enumerationFilter object
            enumerationFilter = self.ixNet.add(self._robot_view+'/layer23TrafficFlowFilter', 'enumerationFilter')
            self.ixNet.setAttribute(enumerationFilter, '-sortDirection', 'descending')
            self.ixNet.commit()
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get enumerationFilter object for"
                                " 'Robot' view") from e

        # Adding 'Source/Dest Port Pair' column to 'Robot' view
        logger.info("Add 'Source/Dest Port Pair' column to 'Robot' custom traffic statistics view...")
        try:
            # Find the 'Source/Dest Port Pair' object, add it to the 'Robot' view
            source_dest_track_id = None
            trackingFilterIdList = self.ixNet.getList(self._robot_view, 'availableTrackingFilter')
            for track_id in trackingFilterIdList:
                if re.search('Source/Dest Port Pair', track_id):
                    source_dest_track_id = track_id
                    break
            if source_dest_track_id:
                self.ixNet.setAttribute(enumerationFilter, '-trackingFilterId', source_dest_track_id)
                self.ixNet.commit()
            else:
                raise AssertionError("Unable to add column for filter "
                                    "'Source/Dest Port Pair' to 'Robot' "
                                    "traffic statistics view.")
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to add 'Source/Dest Port Pair' to "
                                "'Robot' traffic statistics view.") from e

        # Enable 'Robot' view visibility
        logger.info("Enable custom IxNetwork traffic statistics view 'Robot'...")
        try:
            # Re-enable TCL View Robot
            self.ixNet.setAttribute(self._robot_view, '-enabled', 'true')
            self.ixNet.setAttribute(self._robot_view, '-visible', 'true')
            self.ixNet.commit()

            # Print to log
            logger.info("Populated traffic statistics view 'Robot' with required "
                        "data.")
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while enabling traffic statistics view "
                                "'Robot' with required data.") from e

        # Create Robot Page object to parse later
        logger.info("Displaying custom IxNetwork traffic statistics view 'Robot' page...")
        try:
            # Get the page view of the TCL View Robot
            self._robot_page = self.ixNet.getList(self._robot_view, 'page')[0]
            self.ixNet.setAttribute(self._robot_page, '-egressMode', 'conditional')
            self.ixNet.commit()

            # Poll until the view is ready
            for i in range(0, view_create_iteration):
                try:
                    assert self.ixNet.getAttribute(self._robot_page, '-isReady') == 'true'
                except Exception as e:
                    logger.warning("IxNetwork traffic statistics view 'Robot' is "
                                "not ready.\nSleeping {} seconds and before "
                                "checking traffic statistics view 'Robot'".\
                                format(view_create_interval))
                    time.sleep(view_create_interval)
                else:
                    logger.info("Custom IxNetwork traffic statistics view 'Robot' "
                                "is ready.")
                    break
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to create custom IxNetwork traffic "
                                "statistics view 'Robot' page.") from e


    @isconnected
    def check_traffic_loss(self, traffic_streams=[], max_outage=120, loss_tolerance=15, rate_tolerance=5, check_iteration=10, check_interval=60, outage_dict={}):
        '''Check traffic loss for each traffic stream configured on Ixia
            using statistics/data from 'Traffic Item Statistics' view'''

        for i in range(check_iteration):
            logger.info("\nAttempt #{}: Checking for traffic outage/loss".format(i+1))
            overall_result = {}
            # Get and display 'Robot' traffic statistics table containing outage/loss values
            traffic_table = self.create_traffic_streams_table()
            # Check all streams for traffic outage/loss
            for row in traffic_table:
                # Strip headers and borders
                row.header = False ; row.border = False
                # Get data
                stream = row.get_string(fields=["Traffic Item"]).strip()
                src_dest_pair = row.get_string(fields=["Source/Dest Port Pair"]).strip()
                # Skip other streams if list of stream provided
                if traffic_streams and stream not in traffic_streams:
                    continue

                # Skip checks if traffic stream is not of type l2l3
                ti_type = self.get_traffic_stream_attribute(traffic_stream=stream,
                                                            attribute='trafficItemType')
                if ti_type != 'l2L3':
                    logger.warning("SKIP: Traffic stream '{}' is not of type L2L3 "
                                "- skipping traffic loss checks".format(stream))
                    continue

                # Skip checks if traffic stream from Robot table not in configuration
                if stream not in self.get_traffic_stream_names():
                    logger.warning("SKIP: Traffic stream '{}' not found in current"
                                " configuration".format(stream))
                    continue

                # Determine outage values for this traffic stream
                if outage_dict and 'traffic_streams' in outage_dict and \
                    stream in outage_dict['traffic_streams']:
                    given_max_outage=outage_dict['traffic_streams'][stream]['max_outage']
                    given_loss_tolerance=outage_dict['traffic_streams'][stream]['loss_tolerance']
                    given_rate_tolerance=outage_dict['traffic_streams'][stream]['rate_tolerance']
                else:
                    given_max_outage=max_outage
                    given_loss_tolerance=loss_tolerance
                    given_rate_tolerance=rate_tolerance

                # --------------
                # BEGIN CHECKING
                # --------------
                logger.info("Checking traffic stream: '{s} | {t}'".\
                                format(s=src_dest_pair, t=stream))

                # 1- Verify traffic Outage (in seconds) is less than tolerance threshold
                logger.info("1. Verify traffic outage (in seconds) is less than "
                            "tolerance threshold of '{}' seconds".format(given_max_outage))
                current_outage = row.get_string(fields=["Outage (seconds)"]).strip()
                if float(current_outage) <= float(given_max_outage):
                    logger.info("* Traffic outage of '{c}' seconds is within "
                                "expected maximum outage threshold of '{g}' seconds".\
                                format(c=current_outage, g=given_max_outage))
                    outage_check = True
                else:
                    outage_check = False
                    logger.error("* Traffic outage of '{c}' seconds is *NOT* within "
                                "expected maximum outage threshold of '{g}' seconds".\
                                format(c=current_outage, g=given_max_outage))

                # 2- Verify current loss % is less than tolerance threshold
                logger.info("2. Verify current loss % is less than tolerance "
                            "threshold of '{}' %".format(given_loss_tolerance))
                if row.get_string(fields=["Loss %"]).strip() != '':
                    current_loss_percentage = row.get_string(fields=["Loss %"]).strip()
                else:
                    current_loss_percentage = 0
                if float(current_loss_percentage) <= float(given_loss_tolerance):
                    logger.info("* Current traffic loss of {l}% is within"
                                " maximum expected loss tolerance of {g}%".\
                                format(l=current_loss_percentage, g=given_loss_tolerance))
                    loss_check = True
                else:
                    loss_check = False
                    logger.error("* Current traffic loss of {l}% is *NOT* within"
                                " maximum expected loss tolerance of {g}%".\
                                format(l=current_loss_percentage, g=given_loss_tolerance))

                # 3- Verify difference between Tx Rate & Rx Rate is less than tolerance threshold
                logger.info("3. Verify difference between Tx Rate & Rx Rate is less "
                            "than tolerance threshold of '{}' pps".format(given_rate_tolerance))
                tx_rate = row.get_string(fields=["Tx Frame Rate"]).strip()
                rx_rate = row.get_string(fields=["Rx Frame Rate"]).strip()
                if abs(float(tx_rate) - float(rx_rate)) <= float(given_rate_tolerance):
                    logger.info("* Difference between Tx Rate '{t}' and Rx Rate"
                                " '{r}' is within expected maximum rate loss"
                                " threshold of '{g}' packets per second".\
                                format(t=tx_rate, r=rx_rate, g=given_rate_tolerance))
                    rate_check = True
                else:
                    rate_check = False
                    logger.error("* Difference between Tx Rate '{t}' and Rx Rate"
                                " '{r}' is *NOT* within expected maximum rate loss"
                                " threshold of '{g}' packets per second".\
                                format(t=tx_rate, r=rx_rate, g=given_rate_tolerance))

                # Set overall result
                if outage_check and loss_check and rate_check:
                    continue
                else:
                    overall_result.setdefault('streams', {})['{s} | {t}'.\
                                    format(s=src_dest_pair, t=stream)] =\
                                    "FAIL"

            # Check if iteration required based on results
            if 'streams' not in overall_result:
                logger.info("\nSuccessfully verified traffic outages/loss is within "
                            "tolerance for given traffic streams")
                break
            elif i == check_iteration or i == check_iteration-1:
                # End of iterations, raise Exception and exit
                raise AssertionError("Unexpected traffic outage/loss is observed")
            else:
                # Traffic loss observed, sleep and recheck
                logger.error("\nTraffic loss/outage observed for streams:")
                for item in overall_result['streams']:
                    logger.error("* {}".format(item))
                logger.error("Sleeping '{s}' seconds and rechecking streams for "
                            "traffic outage/loss".format(s=check_interval))
                time.sleep(check_interval)


    @isconnected
    def create_traffic_streams_table(self, set_golden=False, clear_stats=False, clear_stats_time=30, view_create_interval=30, view_create_iteration=5):
        '''Returns traffic profile of configured streams on Ixia'''

        # Init
        traffic_table = PrettyTable()

        # If robot view and page has not been created before, create one
        if 'Robot' not in self.get_all_statistics_views():
            self.create_robot_statistics_view(view_create_interval=view_create_interval,
                                                view_create_iteration=view_create_iteration)

        # Clear stats and wait
        if clear_stats:
            self.clear_statistics(wait_time=clear_stats_time)

        try:
            # Traffic table headers
            headers = self.ixNet.getAttribute(self._robot_page, '-columnCaptions')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get Column Captions from custom view 'Robot'")

        # Add column for Outage
        headers.append('Outage (seconds)')
        # Arrange data to fit into table as required in final format:
        # ['Source/Dest Port Pair', 'Traffic Item', 'Tx Frames', 'Rx Frames', 'Frames Delta', 'Tx Frame Rate', 'Rx Frame Rate', 'Loss %', 'Outage (seconds)']
        del headers[0]
        headers[1], headers[0] = headers[0], headers[1]
        headers[5], headers[7] = headers[7], headers[5]
        headers[6], headers[5] = headers[5], headers[6]
        traffic_table.field_names = headers

        required_headers = ['Source/Dest Port Pair', 'Traffic Item',
                            'Tx Frames', 'Rx Frames', 'Frames Delta',
                            'Tx Frame Rate', 'Rx Frame Rate', 'Loss %',
                            'Outage (seconds)']
        # Check that all the expected headers were found
        for item in required_headers:
            try:
                assert item in headers
            except AssertionError as e:
                raise AssertionError("Column '{}' is missing from custom created 'Robot' view".format(item))

        # Increase page size for Robot view to max size
        try:
            build_number = self.ixNet.getAttribute('/globals', '-buildNumber')
            if '7.40' in build_number or '7.50' in build_number:
                max_pagesize = 200
            else:
                max_pagesize = 2048
            self.ixNet.setAttribute(self._robot_page, '-pageSize', max_pagesize)
            self.ixNet.commit()
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to set 'Robot' view page size to max "
                                "value of {}".format(max_pagesize))

        # Get total number of pages
        try:
            total_pages = int(self.ixNet.getAttribute(self._robot_page, '-totalPages'))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get count of all pages in 'Robot' view")
        else:
            logger.info("Total number of pages in 'Robot' view is '{}'".\
                        format(total_pages))

        # Loop over all pages and add values
        for i in range(1, total_pages+1):

            # Set current page to i
            try:
                self.ixNet.setAttribute(self._robot_page, '-currentPage', i)
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to proceed to 'Robot' view page '{}'".\
                                    format(i))
            else:
                logger.info("Reading data from 'Robot' view page {i}/{t}".\
                            format(i=i, t=total_pages))

            # Get row data from current page
            try:
                all_rows = self.ixNet.getAttribute(self._robot_page, '-rowValues')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get row data from 'Robot' "
                                    "view page '{}'".format(i))

            # Populate table with row data from current page
            for item in all_rows:
                # Get row value data
                row_item = item[0]
                # Arrange data to fit into table as required in final format:
                # ['Source/Dest Port Pair', 'Traffic Item', 'Tx Frames', 'Rx Frames', 'Frames Delta', 'Tx Frame Rate', 'Rx Frame Rate', 'Loss %', 'Outage (seconds)']
                del row_item[0]
                row_item[1], row_item[0] = row_item[0], row_item[1]
                row_item[5], row_item[7] = row_item[7], row_item[5]
                row_item[6], row_item[5] = row_item[5], row_item[6]
                # Calculate outage in seconds from 'Frames Delta' and add to row
                frames_delta = row_item[4]
                tx_frame_rate = row_item[5]
                if tx_frame_rate == '0.000' or tx_frame_rate == '0':
                    outage_seconds = 0.0
                else:
                    outage_seconds = round(float(frames_delta)/float(tx_frame_rate), 3)
                row_item.append(str(outage_seconds))
                # Add data to traffic_table
                traffic_table.add_row(row_item)

        # Align and print profile table in the logs
        traffic_table.align = "l"
        logger.info(traffic_table)

        # If flag set, reset the golden profile
        if set_golden:
            logger.info("\nSetting golden traffic profile\n")
            self._golden_profile = traffic_table

        # Return profile table to caller
        return traffic_table


    @isconnected
    def compare_traffic_profile(self, profile1, profile2, loss_tolerance=5, rate_tolerance=2):
        '''Compare two Ixia traffic profiles'''
        logger.info("Comparing traffic profiles")
        # Check profile1
        if not isinstance(profile1, PrettyTable) or not profile1.field_names:
            raise AssertionError("Profile1 is not in expected format or missing data")
        else:
            logger.info("Profile1 is in expected format with data")

        # Check profile2
        if not isinstance(profile2, PrettyTable) or not profile2.field_names:
            raise AssertionError("Profile2 is not in expected format or missing data")
        else:
            logger.info("Profile2 is in expected format with data")

        # Compare both profiles

        # Check number of traffic items provided are the same
        profile1_ti = 0 ; profile2_ti = 0
        for row in profile1:
            if row.get_string(fields=['Traffic Item']):
                profile1_ti += 1
        for row in profile2:
            if row.get_string(fields=['Traffic Item']):
                profile2_ti += 1
        if profile2_ti != profile1_ti:
            raise AssertionError("Profiles do not have the same traffic items")

        # Traffic profile column headers
        # ['Source/Dest Port Pair', 'Traffic Item', 'Tx Frames', 'Rx Frames', 'Frames Delta', 'Tx Frame Rate', 'Rx Frame Rate', 'Loss %', 'Outage (seconds)']
        names = ['src_dest_pair', 'traffic_item', 'tx_frames', 'rx_frames', 'frames_delta', 'tx_rate', 'rx_rate', 'loss', 'outage']

        # Begin comparison between profiles
        compare_profile_failed = False
        for profile1_row, profile2_row in zip(profile1, profile2):
            profile1_row.header = False ; profile2_row.header = False
            profile1_row_values = {} ; profile2_row_values = {}
            for item, name in zip(profile1_row._rows[0], names):
                profile1_row_values[name] = item
            for item, name in zip(profile2_row._rows[0], names):
                profile2_row_values[name] = item

            # Ensure profiles have traffic data/content
            if profile1_row_values and profile2_row_values:
                # Compare traffic profiles
                if profile1_row_values['src_dest_pair'] == profile2_row_values['src_dest_pair'] and\
                    profile1_row_values['traffic_item'] == profile2_row_values['traffic_item']:

                    # Begin comparison
                    logger.info("Comparing profiles for traffic item '{}'".format(profile1_row_values['traffic_item']))

                    # Compare Tx Frames Rate between two profiles
                    try:
                        assert abs(float(profile1_row_values['tx_rate']) - float(profile2_row_values['tx_rate'])) <= float(rate_tolerance)
                    except AssertionError as e:
                        compare_profile_failed = True
                        logger.error("* Tx Frames Rate for profile 1 '{p1}' and "
                                    "profile 2 '{p2}' is more than expected "
                                    "tolerance of '{t}'".\
                                    format(p1=profile1_row_values['tx_rate'],
                                            p2=profile2_row_values['tx_rate'],
                                            t=rate_tolerance))
                    else:
                        logger.info("* Tx Frames Rate difference between "
                                    "profiles is less than threshold of '{}'".\
                                    format(rate_tolerance))

                    # Compare Rx Frames Rate between two profiles
                    try:
                        assert abs(float(profile1_row_values['rx_rate']) - float(profile2_row_values['rx_rate'])) <= float(rate_tolerance)
                    except AssertionError as e:
                        compare_profile_failed = True
                        logger.error("* Rx Frames Rate for profile 1 '{p1}' and"
                                    " profile 2 '{p2}' is more than expected "
                                    "tolerance of '{t}'".\
                                    format(p1=profile1_row_values['rx_rate'],
                                            p2=profile2_row_values['rx_rate'],
                                            t=rate_tolerance))
                    else:
                        logger.info("* Rx Frames Rate difference between "
                                    "profiles is less than threshold of '{}'".\
                                    format(rate_tolerance))

                    # Check if loss % in profile1 is not ''
                    try:
                        float(profile1_row_values['loss'])
                    except ValueError:
                        profile1_row_values['loss'] = 0
                    # Check if loss % in profile2 is not ''
                    try:
                        float(profile2_row_values['loss'])
                    except ValueError:
                        profile2_row_values['loss'] = 0
                    # Compare Loss % between two profiles
                    try:
                        assert abs(float(profile1_row_values['loss']) - float(profile2_row_values['loss'])) <= float(loss_tolerance)
                    except AssertionError as e:
                        compare_profile_failed = True
                        logger.error("* Loss % for profile 1 '{p1}' and "
                                    "profile 2 '{p2}' is more than expected "
                                    "tolerance of '{t}'".\
                                    format(p1=profile1_row_values['loss'],
                                            p2=profile2_row_values['loss'],
                                            t=loss_tolerance))
                    else:
                        logger.info("* Loss % difference between profiles "
                                    "is less than threshold of '{}'".\
                                    format(loss_tolerance))
                else:
                    logger.error("WARNING: The source/dest port pair and traffic"
                                " item are mismatched - skipping check")
            else:
                raise AssertionError("Profiles provided for comparison do not "
                                    "contain relevant traffic data")
        # Final result of comparison
        if compare_profile_failed:
            raise AssertionError("Comparison failed for traffic items between profiles")
        else:
            logger.info("Comparison passed for all traffic items between profiles")


    #--------------------------------------------------------------------------#
    #                               Utils                                      #
    #--------------------------------------------------------------------------#

    @isconnected
    def save_statistics_snapshot_csv(self, view_name, csv_windows_path="C:\\Users\\", csv_file_name="Ixia_Statistics"):
        ''' Save 'Flow Statistics' or 'Traffic Item Statistics' snapshot as a CSV '''

        # Print message that this does not work for Ixia version <= 8.40
        try:
            build_number = self.ixNet.getAttribute('/globals', '-buildNumber')
        except Exception as e:
            raise AssertionError("Unable to get IxNetwork version number")
        if '7.40' in build_number or '7.50' in build_number or '8.10' in build_number:
            raise AssertionError("CSV snapshot functionality not supported on "
                                "current Ixia version - {}".format(build_number))

        # Check valid view name provided
        try:
            assert view_name in ['Flow Statistics', 'Traffic Item Statistics']
        except AssertionError as e:
            logger.error(e)
            raise AssertionError("Invalid view '{}' provided for CSV data dumping".\
                                format(view_name))

        logger.info("Save '{}' snapshot CSV".format(view_name))

        logger.info("\n\nNOTE: Using csv_windows_path='{}' to save snapshot CSV."
                    "\nPlease provide alternate directory if unreachable\n\n".\
                    format(csv_windows_path))

        # Get 'Flow Statistics' view page object
        if view_name == 'Flow Statistics':
            page_obj = self.find_flow_statistics_page_obj()
        elif view_name == 'Traffic Item Statistics':
            page_obj = self.find_traffic_item_statistics_page_obj()

        # Change page size to some high value so that we get all the stats on one page
        max_pagesize = 2048
        try:
            self.ixNet.setAttribute(page_obj, '-pageSize', max_pagesize)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to change pageSize to {p} for '{v}' "
                                "view".format(p=max_pagesize, v=view_name))

        # Enable CSV logging
        logger.info("Enable CSV logging on Ixia...")
        try:
            self.ixNet.setAttribute('::ixNet::OBJ-/statistics', '-enableCsvLogging', 'true')
            self.ixNet.setAttribute('::ixNet::OBJ-/statistics', '-csvFilePath', csv_windows_path)
            self.ixNet.setAttribute('::ixNet::OBJ-/statistics', '-pollInterval', 1)
            self.ixNet.commit()
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while enabling CSV logging on Ixia")
        else:
            logger.info("Successfully enabled CSV logging on Ixia")

        # Get snapshot options
        logger.info("Get list of all snapshot options...")
        try:
            opts = self.ixNet.execute('GetDefaultSnapshotSettings')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get CSV snapshot options")
        else:
            logger.info("Successfully retreived options available")

        # Configure options settings
        filePathToChange = 'Snapshot.View.Csv.Location: ' + csv_windows_path
        opts[1] = filePathToChange
        generatingModeToChange= 'Snapshot.View.Csv.GeneratingMode: "kOverwriteCSVFile"'
        opts[2] = generatingModeToChange
        fileNameToAppend = 'Snapshot.View.Csv.Name: ' + csv_file_name
        opts.append(fileNameToAppend)

        # Save snapshot to location provided
        logger.info("Save CSV snapshot of '{v}' view to '{path}\\{file}.csv'...".\
                    format(v=view_name, path=csv_windows_path, file=csv_file_name))
        try:
            self.ixNet.execute('TakeViewCSVSnapshot', ["{}".format(view_name)], opts)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to take CSV snapshot of '{}' view".\
                                format(view_name))
        else:
            logger.info("Successfully saved CSV snapshot of '{}' view to:".format(view_name))
            logger.info("{path}\\{file}".format(path=csv_windows_path, file=csv_file_name))

        # Set local and copy file paths
        windows_stats_csv = csv_windows_path + '\\' + csv_file_name + '.csv'
        stats_csv_file = "/tmp/" + csv_file_name + '.csv'

        # Copy file to /tmp/
        logger.info("Copy '{v}' CSV to '{f}'".format(v=view_name, f=stats_csv_file))
        try:
            self.ixNet.execute('copyFile',
                                self.ixNet.readFrom(windows_stats_csv, '-ixNetRelative'),
                                self.ixNet.writeTo(stats_csv_file, '-overwrite'))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to copy '{v}' CSV snapshot to '{f}'".\
                                format(v=view_name, f=stats_csv_file))
        else:
            logger.info("Successfully copied '{v}' CSV snapshot to '{f}'".\
                        format(v=view_name, f=stats_csv_file))

        # Return to caller
        return stats_csv_file


    @isconnected
    def get_all_statistics_views(self):
        '''Returns all the statistics views/tabs currently present on IxNetwork'''
        all_views = []
        try:
            # Views from the 613
            views = self.ixNet.getList('/statistics', 'view')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get a list of all statistics views "
                                "(tabs) present on IxNetwork client")
        else:
            for item in views:
                all_views.append(item.\
                    replace("::ixNet::OBJ-/statistics/view:", "").\
                    replace("\"", ""))
            return all_views


    #--------------------------------------------------------------------------#
    #                               Traffic                                    #
    #--------------------------------------------------------------------------#

    @isconnected
    def get_traffic_attribute(self, attribute):
        '''Returns the specified attribute for the given traffic configuration'''
        # Sample attributes
        # ['state', 'isApplicationTrafficRunning', 'isTrafficRunning']
        try:
            return self.ixNet.getAttribute('/traffic', '-{}'.format(attribute))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to check attribute '{}'".\
                                format(attribute)) from e


    @isconnected
    def get_traffic_items_from_robot_view(self, traffic_table):
        '''Returns list of all traffic items from within the Robot view traffic table'''
        # Init
        traffic_streams = []
        # Loop over traffic table provided
        for row in traffic_table:
            row.header = False
            row.border = False
            traffic_streams.append(row.get_string(fields=["Traffic Item"]).strip())
        # Return to caller
        return traffic_streams


    @isconnected
    def enable_flow_tracking_filter(self, tracking_filter):
        '''Enable specific flow tracking filters for traffic streams'''
        # Check valid tracking_filter passed in
        assert tracking_filter in ['trackingenabled0',
                                    'sourceDestPortPair0',
                                    'sourceDestValuePair0',
                                    ]
        # Init
        filter_added = False
        # Mapping for filter names
        map_dict = {
            'trackingenabled0': "'Traffic Items'",
            'sourceDestPortPair0': "'Source/Dest Port Pair'",
            'sourceDestValuePair0': "'Source/Dest Value Pair"
            }
        logger.info("Checking if {} filter present in L2L3 traffic streams...".\
                    format(map_dict[tracking_filter]))
        # Get all traffic stream objects in configuration
        traffic_streams = self.get_traffic_stream_objects()
        if not traffic_streams:
            raise AssertionError("Unable to find traffic streams for configuration")
        # Initial state
        initial_state = self.get_traffic_attribute(attribute='state')
        for ti in traffic_streams:
            # Get traffic stream type
            ti_type = None ; ti_name = None
            try:
                ti_type = self.ixNet.getAttribute(ti, '-trafficItemType')
                ti_name = self.ixNet.getAttribute(ti, '-name')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get traffic item '{}'"
                                    " attributes".format(ti))
            # If traffic streams is not of type 'l2l3' then skip to next stream
            if ti_type != 'l2L3':
                continue
            # Get the status of 'trackingenabled' filter
            trackByList = []
            try:
                trackByList = self.ixNet.getAttribute(ti + '/tracking', '-trackBy')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while checking status of filter '{f}'"
                                    " for traffic stream '{t}'".format(t=ti_name,
                                    f=tracking_filter))
            # If tracking_filter is already present then skip to next stream
            if tracking_filter in trackByList:
                continue
            # At this point, tracking_filter is not found, add it manually
            # Stop the traffic
            state = self.get_traffic_attribute(attribute='state')
            if state != 'stopped' and state != 'unapplied':
                self.stop_traffic(wait_time=15)

            logger.info("Adding '{f}' filter to traffic stream '{t}'".\
                        format(f=tracking_filter, t=ti_name))

            # Add tracking_filter
            trackByList.append(tracking_filter)
            try:
                self.ixNet.setMultiAttribute(ti + '/tracking', '-trackBy', trackByList)
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while adding '{f}' filter to traffic"
                                    " stream '{t}'".format(t=ti_name,
                                    f=tracking_filter))
            else:
                filter_added = True

        # Loop exhausted, if tracking_filter added, commit+apply+start traffic
        if filter_added:
            self.ixNet.commit()
            self.apply_traffic(wait_time=15)
            if initial_state == 'started':
                self.start_traffic(wait_time=15)
        else:
            logger.info("Filter '{}' previously configured for all L2L3 traffic "
                        "streams".format(tracking_filter))


    @isconnected
    def get_golden_profile(self):
        ''' Returns golden profile'''
        return self._golden_profile


    #--------------------------------------------------------------------------#
    #                           Virtual Ports                                  #
    #--------------------------------------------------------------------------#

    @isconnected
    def assign_ixia_ports(self, wait_time=15):
        '''Assign physical Ixia ports from the loaded configuration to the corresponding virtual ports'''

        logger.info("Assigning Ixia ports")

        # Get list of physical ports
        logger.info("Getting a list of physical ports...")
        self.physical_ports = []
        for item in self.ixia_port_list:
            logger.info("-> {}".format(item))
            ixnet_port = []
            lc, port = item.split('/')
            for tmpvar in self.ixia_chassis_ip, lc, port:
                ixnet_port.append(tmpvar)
            self.physical_ports.append(ixnet_port)

        # Add the chassis
        logger.info("Adding chassis...")
        try:
            self.chassis = self.ixNet.add(self.ixNet.getRoot() + \
                                            'availableHardware',\
                                            'chassis', '-hostname',\
                                            self.ixia_chassis_ip)
            self.ixNet.commit()
            self.chassis = self.ixNet.remapIds(self.chassis)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while adding chassis '{}'".\
                                format(self.ixia_chassis_ip))
        else:
            logger.info("Successfully added chassis '{}'".\
                        format(self.ixia_chassis_ip))

        # Get virtual ports
        logger.info("Getting virtual ports...")
        try:
            self.virtual_ports = self.ixNet.getList(self.ixNet.getRoot(), 'vport')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while getting virtual ports from "
                                "the loaded configuration")
        else:
            logger.info("Found virtual ports from loaded configuration:")
            for item in self.virtual_ports:
                logger.info("-> {}".format(item))

        # Assign ports
        logger.info("Assign physical ports to virtual ports...")
        try:
            self.ixNet.execute('assignPorts', self.physical_ports, [],
                                self.virtual_ports, True)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to assign physical ports to virtual ports")
        else:
            logger.info("Successfully assigned physical ports to virtual ports")
            logger.info("Waiting {} seconds after assigning ports...".format(wait_time))
            time.sleep(wait_time)

        # Verify ports are up and connected
        logger.info("Verify ports are up and connected...")
        for vport in self.virtual_ports:
            # Get the name
            try:
                name = self.ixNet.getAttribute(vport, '-name')
            except Exception as e:
                raise AssertionError("Unable to get 'name' for virtual port"
                                    " '{}'".format(vport))
            # Verify port is up
            try:
                state = self.ixNet.getAttribute(vport, '-state')
                assert state == 'up'
            except AssertionError as e:
                logger.warning("Port '{}' is not 'up', sending ARP and rechecking state...")
                # Send ARP on port
                try:
                    self.send_arp(wait_time=wait_time)
                except AssertionError as e:
                    logger.error(e)
                    raise AssertionError("Port '{n}' is '{s}' and not 'up' after"
                                        " sending ARP".format(n=name, s=state))
            else:
                logger.info("Port '{}' is up as expected".format(name))

            # Verify port is connected
            try:
                assert self.ixNet.getAttribute(vport, '-isConnected') == 'true'
            except AssertionError as e:
                raise AssertionError("Port '{}' is not connected".format(name))
            else:
                logger.info("Port '{}' is connected".format(name))

        # If all pass
        logger.info("Assigned the following physical Ixia ports to virtual ports:")
        for port in self.ixia_port_list:
            logger.info("-> Ixia Port: '{}'".format(port))


    @isconnected
    def set_ixia_virtual_ports(self):
        '''Set virtual Ixia ports for this configuration'''

        try:
            # Set virtual Ixia ports
            self.virtual_ports = self.ixNet.getList(self.ixNet.getRoot(), 'vport')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get virtual ports on Ixia")


    @isconnected
    def get_ixia_virtual_port(self, port_name):
        '''Return virtual Ixia port object from port_name'''

        # Set virtual Ixia ports if not previously set
        if not self.virtual_ports:
            self.set_ixia_virtual_ports()

        # Get vport object from port_name
        for item in self.virtual_ports:
            if port_name == self.get_ixia_virtual_port_attribute(item, 'name'):
                return item


    @isconnected
    def get_ixia_virtual_port_attribute(self, vport, attribute):
        '''Get attibute for virtual Ixia port'''

        try:
            # Extract Ixia virtual port settings/attribute
            value = self.ixNet.getAttribute(vport, '-{}'.format(attribute))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get attribute '{a}'' for ixia"
                                " port '{p}'".format(a=attribute, p=vport))
        else:
            return value


    #--------------------------------------------------------------------------#
    #                           Packet Capture                                 #
    #--------------------------------------------------------------------------#

    @isconnected
    def get_ixia_virtual_port_capture(self, port_name):

        # Get virtual Ixia port object
        try:
            vportObj = self.get_ixia_virtual_port(port_name=port_name)
        except:
            raise AssertionError("Unable to get virtual Ixia port object for "
                                "port '{}'".format(port_name))

        # Get captureObj for this virtual port
        try:
            return self.ixNet.getList(vportObj, 'capture')[0]
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get captureObj for port '{}'".\
                                format(port_name))


    @isconnected
    def enable_data_packet_capture(self, ports):
        '''Enable data packet capture on ports specified'''

        for port in ports.split(', '):

            # Get virtual Ixia port capture object
            captureObj = self.get_ixia_virtual_port_capture(port_name=port)

            # Enable data packet capture on port/node
            logger.info("Enabling data packet capture on port '{}'".format(port))
            try:
                self.ixNet.setAttribute(captureObj, '-hardwareEnabled', 'true')
                self.ixNet.commit()
            except Exception as e:
                raise AssertionError("Error while enabling data packet capture "
                                    "on port '{}'".format(port))


    @isconnected
    def disable_data_packet_capture(self, ports):
        '''Disable data packet capture on ports specified'''

        for port in ports.split(', '):

            # Get virtual Ixia port capture object
            captureObj = self.get_ixia_virtual_port_capture(port_name=port)

            # Enable data packet capture on port/node
            logger.info("Disabling data packet capture on port '{}'".format(port))
            try:
                self.ixNet.setAttribute(captureObj, '-hardwareEnabled', 'false')
                self.ixNet.commit()
            except Exception as e:
                raise AssertionError("Error while enabling data packet capture "
                                    "on port '{}'".format(port))


    @isconnected
    def enable_control_packet_capture(self, ports):
        '''Enable data packet capture on ports specified'''

        for port in ports.split(', '):

            # Get virtual Ixia port capture object
            captureObj = self.get_ixia_virtual_port_capture(port_name=port)

            # Enable data packet capture on port/node
            logger.info("Enabling control packet capture on port '{}'".format(port))
            try:
                self.ixNet.setAttribute(captureObj, '-softwareEnabled', 'true')
                self.ixNet.commit()
            except Exception as e:
                raise AssertionError("Error while enabling data packet capture "
                                    "on port '{}'".format(port))


    @isconnected
    def disable_control_packet_capture(self, ports):
        '''Disable data packet capture on ports specified'''

        for port in ports.split(', '):

            # Get virtual Ixia port capture object
            captureObj = self.get_ixia_virtual_port_capture(port_name=port)

            # Enable data packet capture on port/node
            logger.info("Disabling data packet capture on port '{}'".format(port))
            try:
                self.ixNet.setAttribute(captureObj, '-softwareEnabled', 'false')
                self.ixNet.commit()
            except Exception as e:
                raise AssertionError("Error while enabling data packet capture "
                                    "on port '{}'".format(port))


    @isconnected
    def start_packet_capture(self, capture_time=60):
        '''Start capturing packets for a specified amount of time'''

        logger.info("Starting packet capture...")
        try:
            # Start capturing packets
            self.ixNet.execute('startCapture')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to start packet capture")

        # Time to wait after capturing packets
        logger.info("Waiting for '{}' seconds after starting packet capture".\
                                                        format(capture_time))
        time.sleep(capture_time)


    @isconnected
    def stop_packet_capture(self):
        '''Stop capturing packets'''

        logger.info("Stopping packet capture...")
        try:
            # Start capturing packets
            self.ixNet.execute('stopCapture')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to start packet capture")


    @isconnected
    def get_packet_capture_count(self, port_name, pcap_type):
        ''' Get the total count of packets captured during packet capture'''

        # Verify user has provided correct packet type to count
        assert pcap_type in ['data', 'control']

        # Get virtual Ixia port capture object
        captureObj = self.get_ixia_virtual_port_capture(port_name=port_name)

        if pcap_type == 'control':

            logger.info("Getting total count of Control Packets...")
            try:
                packet_count = self.ixNet.getAttribute(captureObj, '-controlPacketCounter')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting total contol packets"
                                    " during packet capture")
            else:
                return packet_count

        elif pcap_type == 'data':

            logger.info("Getting total count of Data Packets...")
            try:
                packet_count = self.ixNet.getAttribute(captureObj, '-dataPacketCounter')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting total contol packets"
                                    " during packet capture")
            else:
                return packet_count


    @isconnected
    def get_packet_capture_data(self, port_name):
        '''Search inside packet collected from pcap for specific data'''

        # Get virtual Ixia port capture object
        captureObj = self.get_ixia_virtual_port_capture(port_name=port_name)

        # Get current packet stack
        logger.info("Getting packet capture stack on port '{}".format(port_name))
        try:
            current_packet = self.ixNet.getList(captureObj, 'currentPacket')[0]
            status = self.ixNet.execute('getPacketFromDataCapture', current_packet, 11)
            stacklist = self.ixNet.getList(current_packet, 'stack')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while getting packet capture stack")

        # Get information inside packet capture stack
        logger.info("Extracting packet capture data")

        for stack in stacklist:
            try:
                # Get name of stack
                stack_name = self.ixNet.getAttribute(stack, "-displayName")
                logger.info(stack_name)

                # List of all the elements within data capture
                for field in self.ixNet.getList(stack, 'field'):
                    # Get the value of the field
                    name = self.ixNet.getAttribute(field, "-displayName")
                    value = self.ixNet.getAttribute(field, "-fieldValue")
                    logger.info("{n} : {v}".format(n=name, v=value))
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while extracting data of packet capture")


    @isconnected
    def save_packet_capture_file(self, port_name, pcap_type, filename, directory='C:/Results'):
        '''Save packet capture file as specified filename to desired location'''

        # Verify user has provided correct packet type to count
        assert pcap_type in ['data', 'control']

        pcap_dict = {
            'data': 'HW',
            'control': 'SW',
            }

        logger.info("Saving packet capture file...")
        try:
            # Save file to C:
            assert self.ixNet.execute('saveCapture', directory, '_{}'.\
                                                format(filename)) == _PASS
        except AssertionError as e:
            logger.info(e)
            raise AssertionError("Unable to save packet capture file as '{}'".\
                                                            format(filename))

        # Return pcap file to caller
        return 'C:/Results/{port_name}_{pcap}_{f}.cap'.\
            format(port_name=port_name, pcap=pcap_dict[pcap_type], f=filename)


    @isconnected
    def export_packet_capture_file(self, src_file, dest_file):
        '''Export packet capture file as specified filename to desired location'''

        logger.info("Exporting packet capture file...")
        try:
            self.ixNet.execute('copyFile',
                                self.ixNet.readFrom(src_file, '-ixNetRelative'),
                                self.ixNet.writeTo(dest_file, '-overwrite'))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to copy '{s}' to '{d}'".\
                                                format(s=src_file, d=dest_file))


    #--------------------------------------------------------------------------#
    #                        Traffic Item (Stream)                             #
    #--------------------------------------------------------------------------#

    @isconnected
    def get_traffic_stream_names(self):
        '''Returns a list of all traffic stream names present in current configuration'''

        # Init
        traffic_streams = []

        # Get traffic stream names from Ixia
        try:
            for item in self.get_traffic_stream_objects():
                traffic_streams.append(self.ixNet.getAttribute(item, '-name'))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while retrieving traffic streams from "
                                "configuration.")
        else:
            # Return to caller
            return traffic_streams


    @isconnected
    def get_traffic_stream_objects(self):
        '''Returns a list of all traffic stream objects present in current configuration'''

        # Get traffic streams from Ixia
        try:
            return self.ixNet.getList('/traffic', 'trafficItem')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while retrieving traffic streams from "
                                "configuration.")


    @isconnected
    def find_traffic_stream_object(self, traffic_stream):
        '''Finds the given stream name's traffic stream object'''

        # Init
        ti_obj = None

        # Find traffic stream object of the given traffic stream
        for item in self.get_traffic_stream_objects():
            try:
                if self.ixNet.getAttribute(item, '-name') == traffic_stream:
                    ti_obj = item
                    break
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get traffic stream object name")

        # Return to caller
        if ti_obj:
            return ti_obj
        else:
            raise AssertionError("Unable to find ::ixNet:: object for traffic "
                                "stream '{}'".format(traffic_stream))


    @isconnected
    def get_traffic_stream_attribute(self, traffic_stream, attribute):
        '''Returns the specified attribute for the given traffic stream'''

        # Sample attributes
        # ['name', 'state', 'txPortName', 'txPortId', 'rxPortName', 'rxPortId', 'trafficItemType']

        # Find traffic stream object
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        # Return the attribute specified for this traffic stream
        try:
            return self.ixNet.getAttribute(ti_obj, '-{}'.format(attribute))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get '{a}' for traffic stream '{t}'".\
                                format(a=attribute, t=traffic_stream))


    @isconnected
    def start_traffic_stream(self, traffic_stream, check_stream=True, wait_time=15):
        '''Start specific traffic stream on Ixia'''

        logger.info("Starting L2/L3 traffic for traffic stream '{}'".\
                        format(traffic_stream))

        # Find traffic stream object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        try:
            # Start traffic for this stream
            self.ixNet.execute('startStatelessTraffic', ti_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while starting traffic for traffic"
                                " stream '{}'".format(traffic_stream))

        # Wait for user specified interval
        logger.info("Waiting for '{t}' seconds after starting traffic stream"
                    " '{s}'".format(t=wait_time, s=traffic_stream))
        time.sleep(wait_time)

        if check_stream:
            # Verify traffic stream state is now 'started'
            logger.info("Verify traffic stream '{}' state is now 'started'".\
                        format(traffic_stream))
            try:
                assert 'started' == self.get_traffic_stream_attribute(traffic_stream=traffic_stream, attribute='state')
            except AssertionError as e:
                raise AssertionError("Traffic stream '{}' state is not 'started'".\
                                    format(traffic_stream))
            else:
                logger.info("Traffic stream '{}' state is 'started'".format(traffic_stream))

            # Verify Tx Frame Rate for this stream is > 0 after starting it
            logger.info("Verify Tx Frame Rate > 0 for traffic stream '{}'".\
                        format(traffic_stream))
            try:
                assert float(self.get_traffic_items_statistics_data(traffic_stream=traffic_stream, traffic_data_field='Tx Frame Rate')) > 0.0
            except AssertionError as e:
                raise AssertionError("Tx Frame Rate is not greater than 0 after "
                                    "starting traffic for traffic stream '{}'".\
                                    format(traffic_stream))
            else:
                logger.info("Tx Frame Rate is greater than 0 after starting traffic "
                            "for traffic stream '{}'".format(traffic_stream))


    @isconnected
    def stop_traffic_stream(self, traffic_stream, wait_time=15):
        '''Stop specific traffic stream on Ixia'''

        logger.info("Stopping L2/L3 traffic for traffic stream '{}'".\
                        format(traffic_stream))

        # Find traffic stream object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        try:
            # Stop traffic fo this stream
            self.ixNet.execute('stopStatelessTraffic', ti_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while stopping traffic for traffic"
                                " stream '{}'".format(traffic_stream))

        # Wait for user specified interval
        logger.info("Waiting for '{t}' seconds after stopping traffic stream"
                    " '{s}'".format(t=wait_time, s=traffic_stream))
        time.sleep(wait_time)

        # Verify traffic stream state is now 'stopped'
        logger.info("Verify traffic stream '{}' state is now 'stopped'".\
                    format(traffic_stream))
        try:
            assert 'stopped' == self.get_traffic_stream_attribute(traffic_stream=traffic_stream, attribute='state')
        except AssertionError as e:
            raise AssertionError("Traffic stream '{}' state is not 'stopped'".\
                                format(traffic_stream))
        else:
            logger.info("Traffic stream '{}' state is 'stopped'".format(traffic_stream))

        # Verify Tx Frame Rate for this stream is > 0 after starting it
        logger.info("Verify Tx Frame Rate == 0 for traffic stream '{}'".\
                    format(traffic_stream))
        try:
            assert float(self.get_traffic_items_statistics_data(traffic_stream=traffic_stream, traffic_data_field='Tx Frame Rate')) == 0.0
        except AssertionError as e:
            raise AssertionError("Tx Frame Rate is greater than 0 after "
                                "stopping traffic for traffic stream '{}'".\
                                format(traffic_stream))
        else:
            logger.info("Tx Frame Rate == 0 after stopping traffic for traffic "
                        "stream '{}'".format(traffic_stream))


    @isconnected
    def generate_traffic_stream(self, traffic_stream, wait_time=15):
        '''Generate traffic for a given traffic stream'''

        logger.info("Generating L2/L3 traffic for traffic stream '{}'".\
                        format(traffic_stream))

        # Find traffic stream object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        # Generate traffic
        try:
            self.ixNet.execute('generate', ti_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while generating traffic for traffic "
                                "stream '{}'".format(traffic_stream))

        # Unset Robot view
        self._robot_view = None
        self._robot_page = None

        # Wait for user specified interval
        logger.info("Waiting for '{t}' seconds after generating traffic stream"
                    " '{s}'".format(t=wait_time, s=traffic_stream))
        time.sleep(wait_time)

        # Check if traffic is in 'unapplied' state
        logger.info("Checking if traffic is in 'unapplied' state...")
        try:
            assert self.get_traffic_attribute(attribute='state') == 'unapplied'
        except AssertionError as e:
            logger.error(e)
            raise AssertionError("Traffic is not in 'unapplied' state")
        else:
            logger.info("Traffic is in 'unapplied' state")


    #--------------------------------------------------------------------------#
    #                       Traffic Item Statistics                            #
    #--------------------------------------------------------------------------#

    @isconnected
    def get_traffic_items_statistics_data(self, traffic_stream, traffic_data_field):
        '''Get value of traffic_data_field of traffic_tream from "Traffic Item Statistics" '''

        # Get all stream data for given traffic_stream
        try:
            return self.ixNet.execute('getValue', 
                    '::ixNet::OBJ-/statistics/view:"Traffic Item Statistics"',
                    traffic_stream, traffic_data_field)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while retrieving '{data}' for traffic "
                                "stream '{stream}' from 'Traffic Item Statistics'".\
                                format(data=traffic_data_field, stream=traffic_stream))


    @isconnected
    def find_traffic_item_statistics_page_obj(self):
        '''Returns the page object for "Traffic Item Statistics" view'''

        # Get the page object
        try:
            return self.ixNet.getList('::ixNet::OBJ-/statistics/view:"Traffic Item Statistics"', 'page')[0]
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while finding 'Traffic Item Statistics' view page object")


    @isconnected
    def get_traffic_item_statistics_table(self, traffic_stats_columns=None):
        ''' Create table of "Traffic Item Statistics" view'''

        # Init
        traffic_items_table = PrettyTable()

        # Save 'Traffic Item Statistics' view CSV snapshot
        csv_file = self.save_statistics_snapshot_csv(view_name="Traffic Item Statistics")
        # Convert CSV file into PrettyTable
        all_traffic_item_data = from_csv(open(csv_file))

        # Determine columns we want to print in the table
        if not traffic_stats_columns:
            traffic_items_table.field_names = ["Traffic Item",
                                                "Tx Frames",
                                                "Rx Frames",
                                                "Frames Delta",
                                                "Loss %",
                                                "Tx Frame Rate",
                                                "Rx Frame Rate",
                                                ]
        else:
            # Make list
            if not isinstance(traffic_stats_columns, list):
                traffic_stats_columns = [traffic_stats_columns]
            # Add "Traffic Items" default column
            traffic_stats_columns.insert(0, "Traffic Item")
            # Set fields
            traffic_items_table.field_names = traffic_stats_columns

        # Create a table with only the values we need
        for row in all_traffic_item_data:

            # Strip headers and borders and init
            row.header = False ; row.border = False
            table_values = []

            # Get all the data for this row
            for item in traffic_items_table.field_names:
                table_values.append(row.get_string(fields=[item]).strip())

            # Add data to the smaller table to display to user
            traffic_items_table.add_row(table_values)

        # Delete CSV snapshot file
        try:
            os.remove(csv_file)
        except Exception as e:
            logger.error("Unable to remove CSV snapshot file '{}'".format(csv_file))
        else:
            logger.info("Deleted CSV snapshot file '{}'".format(csv_file))

        # Align and print flow groups table in the logs
        traffic_items_table.align = "l"
        logger.info(traffic_items_table)
        self._traffic_statistics_table = traffic_items_table

        # Return to caller
        return traffic_items_table


    #--------------------------------------------------------------------------#
    #                            Flow Groups                                   #
    #--------------------------------------------------------------------------#

    @isconnected
    def get_flow_group_names(self, traffic_stream):
        '''Returns a list of all the flow group names for the given traffic stream present in current configuration'''

        # Init
        flow_groups = []

        # Get flow group objects of given traffic stream from Ixia
        try:
            for item in self.get_flow_group_objects():
                flow_groups.append(self.ixNet.getAttribute(item, '-name'))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while retrieving flow groups for traffic"
                                " stream '{}' from configuration.".\
                                format(traffic_stream))
        else:
            # Return to caller
            return flow_groups


    @isconnected
    def get_flow_group_objects(self, traffic_stream):
        '''Returns a list of flow group objects for the given traffic stream present in current configuration'''

        # Get traffic item object from traffic stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        # Return list of flow group highLevelStream objects
        try:
            return self.ixNet.getList(ti_obj, 'highLevelStream')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Flow groups not found in configuration for "
                                "traffic stream '{}'".format(traffic_stream))


    @isconnected
    def find_flow_group_object(self, traffic_stream, flow_group):
        '''Finds the flow group object when given the flow group name and traffic stream'''

        # Init
        fg_obj = None

        # Get flow group object of the given flow group name and traffic stream
        for item in self.get_flow_group_objects(traffic_stream=traffic_stream):
            try:
                if self.ixNet.getAttribute(item, '-name') == flow_group:
                    fg_obj = item
                    break
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get Quick Flow Group object name")

        # Return to caller
        if fg_obj:
            return fg_obj
        else:
            raise AssertionError("Unable to find ::ixNet:: object for Quick "
                                "Flow Group '{}'".format(flow_group))


    @isconnected
    def get_flow_group_attribute(self, traffic_stream, flow_group, attribute):
        '''Returns the specified attribute for the given flow group of the traffic stream'''

        # Sample attributes
        # ['name', 'state', 'txPortName', 'txPortId', 'rxPortName', 'rxPortId']

        # Find flow group object
        fg_obj = self.find_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

        # Return the attribute specified for this Quick Flow Group
        try:
            return self.ixNet.getAttribute(fg_obj, '-{}'.format(attribute))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get '{a}' for Quick Flow Group '{f}'".\
                                format(a=attribute, f=flow_group))


    @isconnected
    def start_flow_group(self, traffic_stream, flow_group, wait_time=15):
        '''Start given flow group under of traffic stream on Ixia'''

        logger.info("Starting traffic for flow group '{}'".\
                        format(flow_group))

        # Find flow group object from flow group name
        fg_obj = self.find_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

        try:
            # Start traffic for this flow group
            self.ixNet.execute('startStatelessTraffic', fg_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while starting traffic for flow group"
                                " '{}'".format(flow_group))

        # Wait for user specified interval
        logger.info("Waiting for '{t}' seconds after starting traffic for flow "
                    "group '{f}'".format(t=wait_time, f=flow_group))
        time.sleep(wait_time)

        # Verify flow group state is now 'started'
        logger.info("Verify flow group '{}' state is now 'started'".\
                    format(flow_group))
        try:
            assert 'started' == self.get_flow_group_attribute(traffic_stream=traffic_stream, flow_group=flow_group, attribute='state')
        except AssertionError as e:
            raise AssertionError("Flow group '{}' state is not 'started'".\
                                format(flow_group))
        else:
            logger.info("Flow group '{}' state is 'started'".format(flow_group))


    @isconnected
    def stop_flow_group(self, traffic_stream, flow_group, wait_time=15):
        '''Stop given flow group under of traffic stream on Ixia'''

        logger.info("Stopping traffic for flow group '{}'".\
                        format(flow_group))

        # Find flow group object from flow group name
        fg_obj = self.find_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

        try:
            # Stop traffic for this flow group
            self.ixNet.execute('stopStatelessTraffic', fg_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while stopping traffic for flow group"
                                " '{}'".format(flow_group))

        # Wait for user specified interval
        logger.info("Waiting for '{t}' seconds after stopping traffic for flow "
                    "group '{f}'".format(t=wait_time, f=flow_group))
        time.sleep(wait_time)

        # Verify flow group state is now 'stopped'
        logger.info("Verify flow group '{}' state is now 'stopped'".\
                    format(flow_group))
        try:
            assert 'stopped' == self.get_flow_group_attribute(traffic_stream=traffic_stream, flow_group=flow_group, attribute='state')
        except AssertionError as e:
            raise AssertionError("Flow group '{}' state is not 'stopped'".\
                                format(flow_group))
        else:
            logger.info("Flow group '{}' state is 'stopped'".format(flow_group))


    #--------------------------------------------------------------------------#
    #                          Quick Flow Groups                               #
    #--------------------------------------------------------------------------#

    @isconnected
    def get_quick_flow_group_names(self):
        '''Returns a list of all the Quick Flow Group names present in current configuration'''

        # Init
        quick_flow_groups = []

        # Get Quick Flow Group objects from Ixia
        try:
            for item in self.get_quick_flow_group_objects():
                quick_flow_groups.append(self.ixNet.getAttribute(item, '-name'))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while retrieving Quick Flow Groups from "
                                "configuration.")
        else:
            # Return to caller
            return quick_flow_groups


    @isconnected
    def get_quick_flow_group_objects(self):
        '''Returns a list of all Quick Flow Group objects present in current configuration'''

        # Init
        qfg_traffic_item = None

        # Get Quick Flow Group 'traffic stream' object
        for item in self.get_traffic_stream_objects():
            try:
                if self.ixNet.getAttribute(item, '-name') == 'Quick Flow Groups':
                    qfg_traffic_item = item
                    break
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get Quick Flow Group "
                                    "corresponding 'traffic stream' object")

        # Return list of Quick Flow Group highLevelStream objects
        if qfg_traffic_item:
            try:
                return self.ixNet.getList(qfg_traffic_item, 'highLevelStream')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Quick Flow Groups not found in configuration")
        else:
            raise AssertionError("Quick Flow Groups not found in configuration")


    @isconnected
    def find_quick_flow_group_object(self, quick_flow_group):
        '''Finds the Quick Flow Group object when given the Quick Flow Group name'''

        # Init
        qfg_obj = None

        # Get Quick Flow Group object of the given Quick Flow Group name
        for item in self.get_quick_flow_group_objects():
            try:
                if self.ixNet.getAttribute(item, '-name') == quick_flow_group:
                    qfg_obj = item
                    break
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get Quick Flow Group object name")

        # Return to caller
        if qfg_obj:
            return qfg_obj
        else:
            raise AssertionError("Unable to find ::ixNet:: object for Quick "
                                "Flow Group '{}'".format(quick_flow_group))


    @isconnected
    def get_quick_flow_group_attribute(self, quick_flow_group, attribute):
        '''Returns the specified attribute for the given Quick Flow Group'''

        # Sample attributes
        # ['name', 'state', 'txPortName', 'txPortId', 'rxPortName', 'rxPortId']

        # Find Quick Flow Group object
        qfg_obj = self.find_quick_flow_group_object(quick_flow_group=quick_flow_group)

        # Return the attribute specified for this Quick Flow Group
        try:
            return self.ixNet.getAttribute(qfg_obj, '-{}'.format(attribute))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get '{a}' for Quick Flow Group '{q}'".\
                                format(a=attribute, q=quick_flow_group))


    @isconnected
    def start_quick_flow_group(self, quick_flow_group, wait_time=15):
        '''Start given Quick Flow Group on Ixia'''

        logger.info("Starting traffic for Quick Flow Group '{}'".\
                        format(quick_flow_group))

        # Find flow group object from flow group name
        qfg_obj = self.find_quick_flow_group_object(quick_flow_group=quick_flow_group)

        try:
            # Start traffic for this Quick Flow Group
            self.ixNet.execute('startStatelessTraffic', qfg_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while starting traffic for Quick Flow "
                                "Group '{}'".format(quick_flow_group))

        # Wait for user specified interval
        logger.info("Waiting for '{t}' seconds after starting traffic for Quick "
                    "Flow Group '{q}'".format(t=wait_time, q=quick_flow_group))
        time.sleep(wait_time)

        # Verify Quick Flow Group state is now 'started'
        logger.info("Verify Quick Flow Group '{}' state is now 'started'".\
                    format(quick_flow_group))
        try:
            assert 'started' == self.get_quick_flow_group_attribute(quick_flow_group=quick_flow_group, attribute='state')
        except AssertionError as e:
            raise AssertionError("Quick Flow Group '{}' state is not 'started'".\
                                format(quick_flow_group))
        else:
            logger.info("Quick Flow Group '{}' state is 'started'".\
                        format(quick_flow_group))


    @isconnected
    def stop_quick_flow_group(self, quick_flow_group, wait_time=15):
        '''Stop given Quick Flow Group on Ixia'''

        logger.info("Stopping traffic for Quick Flow Group '{}'".\
                        format(quick_flow_group))

        # Find flow group object from flow group name
        qfg_obj = self.find_quick_flow_group_object(quick_flow_group=quick_flow_group)

        try:
            # Stop traffic for this Quick Flow Group
            self.ixNet.execute('stopStatelessTraffic', qfg_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while stopping traffic for Quick Flow "
                                "Group '{}'".format(quick_flow_group))

        # Wait for user specified interval
        logger.info("Waiting for '{t}' seconds after stopping traffic for Quick "
                    "Flow Group '{q}'".format(t=wait_time, q=quick_flow_group))
        time.sleep(wait_time)

        # Verify Quick Flow Group state is now 'stopped'
        logger.info("Verify Quick Flow Group '{}' state is now 'stopped'".\
                    format(quick_flow_group))
        try:
            assert 'stopped' == self.get_quick_flow_group_attribute(quick_flow_group=quick_flow_group, attribute='state')
        except AssertionError as e:
            raise AssertionError("Quick Flow Group '{}' state is not 'stopped'".\
                                format(quick_flow_group))
        else:
            logger.info("Quick Flow Group '{}' state is 'stopped'".\
                        format(quick_flow_group))


    #--------------------------------------------------------------------------#
    #                          Flow Statistics                                 #
    #--------------------------------------------------------------------------#

    @isconnected
    def get_flow_statistics_data(self, traffic_stream, flow_data_field):
        '''Get value of flow_data_field of traffic_tream from "Flow Statistics" '''

        # Get all stream data for given traffic_stream
        try:
            return self.ixNet.execute('getValue',
                            '::ixNet::OBJ-/statistics/view:"Flow Statistics"',
                            traffic_stream, flow_data_field)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while retrieving '{data}' for traffic "
                                "stream '{stream}' from 'Flow Statistics'".\
                                format(data=flow_data_field,
                                        stream=traffic_stream))


    @isconnected
    def find_flow_statistics_page_obj(self):
        '''Returns the page object for "Flow Statistics View"'''

        # Get the page object
        try:
            return self.ixNet.getList('::ixNet::OBJ-/statistics/view:"Flow Statistics"', 'page')[0]
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while finding 'Flow Statistics' view page object")


    @isconnected
    def check_flow_groups_loss(self, traffic_streams=[], max_outage=120,
                                loss_tolerance=15, rate_tolerance=5,
                                csv_windows_path="C:\\Users\\",
                                csv_file_name="Flow_Statistics", verbose=False,
                                display=True, export_to_filename=""):
        '''Checks traffic loss for all flow groups configured on Ixia using
            'Flow Statistics' view data'''

        # Init
        flow_group_table = PrettyTable()
        flow_group_table.field_names = ["Flow Group Traffic Item",
                                        "VLAN:VLAN-ID",
                                        "Source/Dest Port Pair",
                                        "Tx Frame Rate",
                                        "Rx Frame Rate",
                                        "Frames Delta",
                                        "Loss %",
                                        "Outage (seconds)",
                                        "Overall Result"]

        # Save 'Flow Statistics' view CSV snapshot
        csv_file = self.save_statistics_snapshot_csv(view_name="Flow Statistics",
                                                        csv_windows_path=csv_windows_path,
                                                        csv_file_name=csv_file_name)
        # Convert CSV file into PrettyTable
        all_flow_group_data = from_csv(open(csv_file))

        # Create a table with only the values we need
        result_failed = False
        for row in all_flow_group_data:

            # Strip headers and borders and init
            row.header = False ; row.border = False

            # Get all the data for this row
            flow_group_name = row.get_string(fields=["Traffic Item"]).strip()
            vlan_id = row.get_string(fields=["VLAN:VLAN-ID"]).strip()
            src_dest_port_pair = row.get_string(fields=["Source/Dest Port Pair"]).strip()
            tx_frame_rate = row.get_string(fields=["Tx Frame Rate"]).strip()
            rx_frame_rate = row.get_string(fields=["Rx Frame Rate"]).strip()
            frames_delta = row.get_string(fields=["Frames Delta"]).strip()
            loss_percentage = row.get_string(fields=["Loss %"]).strip()

            # Skip other streams if list of stream provided
            if traffic_streams and flow_group_name not in traffic_streams:
                continue

            # Check row for loss/outage within tolerance
            if verbose:
                logger.info("Checking flow group: '{t} | {vlan} | {pair}'".\
                                format(t=flow_group_name, vlan=vlan_id, pair=src_dest_port_pair))

            # 1- Verify current loss % is less than tolerance threshold
            # Get loss % value
            if row.get_string(fields=["Loss %"]).strip() != '':
                loss_percentage = row.get_string(fields=["Loss %"]).strip()
            else:
                loss_percentage = 0
            # Check traffic loss
            if float(loss_percentage) <= float(loss_tolerance):
                if verbose:
                    logger.info("* Current traffic loss of {l}% is within"
                                " maximum expected loss tolerance of {t}%".\
                                format(t=loss_tolerance, l=loss_percentage))
                loss_check = True
            else:
                loss_check = False
                result_failed = True
                if verbose:
                    logger.error("* Current traffic loss of {l}% is *NOT* within"
                                " maximum expected loss tolerance of {t}%".\
                                format(t=loss_tolerance, l=loss_percentage))

            # 2- Verify difference between Tx Rate & Rx Rate is less than tolerance threshold
            # Get Tx and Rx Frame Rates
            tx_rate = row.get_string(fields=["Tx Frame Rate"]).strip()
            rx_rate = row.get_string(fields=["Rx Frame Rate"]).strip()
            if abs(float(tx_rate) - float(rx_rate)) <= float(rate_tolerance):
                if verbose:
                    logger.info("* Difference between Tx Rate '{t}' and Rx Rate"
                                " '{r}' is within expected maximum rate loss"
                                " threshold of '{m}' packets per second".\
                            format(t=tx_rate, r=rx_rate, m=rate_tolerance))
                rate_check = True
            else:
                rate_check = False
                result_failed = True
                if verbose:
                    logger.error("* Difference between Tx Rate '{t}' and Rx Rate"
                                " '{r}' is *NOT* within expected maximum rate loss"
                                " threshold of '{m}' packets per second".\
                            format(t=tx_rate, r=rx_rate, m=rate_tolerance))

            # 3- Verify traffic Outage (in seconds) is less than tolerance threshold
            # Calculate the outage
            if tx_frame_rate == '0.000' or tx_frame_rate == '0':
                outage_seconds = 0.0
            else:
                try:
                    fd = float(frames_delta)
                    tx = float(tx_frame_rate)
                except ValueError:
                    outage_seconds = 0.0
                else:
                    outage_seconds = round(fd/tx, 3)
            # Check outage
            if float(outage_seconds) <= float(max_outage):
                if verbose:
                    logger.info("* Traffic outage of '{o}' seconds is within "
                                "expected maximum outage threshold of '{s}' seconds".\
                                format(o=outage_seconds, s=max_outage))
                outage_check = True
            else:
                outage_check = False
                result_failed = True
                if verbose:
                    logger.error("* Traffic outage of '{o}' seconds is *NOT* within "
                                "expected maximum outage threshold of '{s}' seconds".\
                                format(o=outage, s=max_outage))

            # Do checks to determine overall result
            if loss_check and rate_check and outage_check:
                overall_result = "PASS"
            else:
                overall_result = "FAIL"

            # Add data to the smaller table to display to user
            flow_group_table.add_row([flow_group_name,
                                        vlan_id,
                                        src_dest_port_pair,
                                        tx_frame_rate,
                                        rx_frame_rate,
                                        frames_delta,
                                        loss_percentage,
                                        outage_seconds,
                                        overall_result])

        # Align and print flow groups table in the logs
        flow_group_table.align = "l"
        if display:
            logger.info(flow_group_table)
        self._flow_statistics_table = flow_group_table

        # Export the file if user requested
        if export_to_filename:
            try:
                self.ixNet.execute('copyFile',
                                    self.ixNet.readFrom(csv_file, '-ixNetRelative'),
                                    self.ixNet.writeTo(export_to_filename, '-overwrite'))
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to export 'Flow Statistics' CSV "
                                    "snapshot file to '{}'".\
                                    format(export_to_filename))

        # Delete CSV snapshot file
        try:
            os.remove(csv_file)
        except Exception as e:
            logger.error("Unable to remove CSV snapshot file '{}'".format(csv_file))
        else:
            logger.info("Deleted CSV snapshot file '{}'".format(csv_file))

        # Check if iteration required based on results
        if not result_failed:
            logger.info("\nSuccessfully verified traffic outages/loss is within "
                        "tolerance for all flow groups")
        else:
            raise AssertionError("\nUnexpected traffic outage/loss is observed "
                                "for flow groups")

        # Return table to caller
        return flow_group_table


    @isconnected
    def get_flow_statistics_table(self):
        '''Returns the last Flow Statistics table created'''

        return self._flow_statistics_table


    @isconnected
    def create_flow_statistics_table(self, flow_stats_columns=None, display=True, export_to_filename=""):
        ''' Create table of "Flow Statistics" view'''

        # Init
        flow_stats_table = PrettyTable()

        # Save 'Flow Statistics' view CSV snapshot
        csv_file = self.save_statistics_snapshot_csv(view_name="Flow Statistics")
        # Convert CSV file into PrettyTable
        all_flow_stats_data = from_csv(open(csv_file))

        # Determine columns we want to print in the table
        if not flow_stats_columns:
            flow_stats_table.field_names = ["Traffic Item",
                                            "Source/Dest Port Pair",
                                            "Tx Frames",
                                            "Rx Frames",
                                            "Frames Delta",
                                            "Loss %",
                                            "Tx Frame Rate",
                                            "Rx Frame Rate",
                                            ]
        else:
            # Make list
            if not isinstance(flow_stats_columns, list):
                flow_stats_columns = [flow_stats_columns]
            # Add "Traffic Items" default column
            flow_stats_columns.insert(0, "Traffic Item")
            # Set fields
            flow_stats_table.field_names = flow_stats_columns

        # Create a table with only the values we need
        for row in all_flow_stats_data:

            # Strip headers and borders and init
            row.header = False ; row.border = False
            table_values = []

            # Get all the data for this row
            for item in flow_stats_table.field_names:
                table_values.append(row.get_string(fields=[item]).strip())

            # Add data to the smaller table to display to user
            flow_stats_table.add_row(table_values)

        # Delete CSV snapshot file
        try:
            os.remove(csv_file)
        except Exception as e:
            logger.error("Unable to remove CSV snapshot file '{}'".format(csv_file))
        else:
            logger.info("Deleted CSV snapshot file '{}'".format(csv_file))

        # Align and set class object for the table
        flow_stats_table.align = "l"
        self._flow_statistics_table = flow_stats_table

        # Print if user requested
        if display:
            logger.info(flow_stats_table)

        # Export the file if user requested
        if export_to_filename:
            try:
                self.ixNet.execute('copyFile',
                                    self.ixNet.readFrom(csv_file, '-ixNetRelative'),
                                    self.ixNet.writeTo(export_to_filename, '-overwrite'))
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to export 'Flow Statistics' CSV "
                                    "snapshot file to '{}'".\
                                    format(export_to_filename))


        # Return to caller
        return flow_stats_table


    #--------------------------------------------------------------------------#
    #                     Line / Packet / Layer2-bit Rate                      #
    #--------------------------------------------------------------------------#

    @isconnected
    def set_line_rate(self, traffic_stream, rate, flow_group='', stop_traffic_time=15, generate_traffic_time=15, apply_traffic_time=15, start_traffic=True, start_traffic_time=15):
        '''Set the line rate for given traffic stream or given flow group of a traffic stream'''

        # Verify rate value provided is <=100 as line rate is a percentage
        try:
            assert rate in range(100)
        except AssertionError as e:
            raise AssertionError("Invalid input rate={} provided. Line rate must"
                                " be between 0 to 100%".format(rate))

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        if flow_group:
            # Set the line rate for given flow group of this traffic item
            logger.info("Setting flow group '{f}' of traffic stream '{t}' "
                            "line rate to '{r}' %".format(f=flow_group,
                                                        t=traffic_stream,
                                                        r=rate))

            # Get flow group object of the given traffic stream
            flowgroupObj = self.get_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

            # Change the line rate as required
            try:
                self.ixNet.setMultiAttribute(flowgroupObj + '/frameRate',
                                                '-rate', rate,
                                                '-type', 'percentLineRate')
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while changing flow group '{f}' of "
                                    "traffic stream '{t}' line rate to '{r}' %".\
                                    format(f=flow_group, t=traffic_stream, r=rate))
            else:
                logger.info("Successfully changed flow group '{f}' of traffic "
                            "stream '{t}' line rate to '{r}'".format(f=flow_group,
                                                                    t=traffic_stream,
                                                                    r=rate))
        else:
            # Set the line rate for the entire traffic stream
            logger.info("Setting traffic stream '{t}' line rate to '{r}' %".\
                            format(t=traffic_stream, r=rate))

            # Initial state
            initial_state = self.get_traffic_attribute(attribute='state')

            # Stop traffic for the given stream
            if initial_state == 'started':
                self.stop_traffic(wait_time=stop_traffic_time)
            else:
                self.stop_traffic_stream(traffic_stream=traffic_stream, wait_time=stop_traffic_time)

            # Get config element object
            try:
                config_elements = self.ixNet.getList(ti_obj, 'configElement')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get config elements for traffic "
                                    "stream '{}'".format(traffic_stream))

            for config_element in config_elements:
                try:
                    self.ixNet.setMultiAttribute(config_element + '/frameRate',
                                                    '-rate', rate,
                                                    '-type', 'percentLineRate')
                    self.ixNet.commit()
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while changing traffic stream "
                                        "'{t}' line rate to '{r}' %".\
                                        format(t=traffic_stream, r=rate))
                else:
                    logger.info("Successfully changed traffic stream '{t}' line "
                                "rate to '{r}' %".format(t=traffic_stream, r=rate))

            # Generate traffic
            self.generate_traffic_stream(traffic_stream=traffic_stream, wait_time=generate_traffic_time)

            # Apply traffic
            self.apply_traffic(wait_time=apply_traffic_time)

            # Start traffic
            if start_traffic:
                if initial_state == 'started':
                    self.start_traffic(wait_time=start_traffic_time)
                else:
                    self.start_traffic_stream(traffic_stream=traffic_stream, wait_time=start_traffic_time)


    @isconnected
    def set_packet_rate(self, traffic_stream, rate, flow_group='', stop_traffic_time=15, generate_traffic_time=15, apply_traffic_time=15, start_traffic=True, start_traffic_time=15):
        '''Set the packet rate for given traffic stream or given flow group of a traffic stream'''

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        if flow_group:
            # Set the packet rate for given flow group of this traffic item
            logger.info("Setting flow group '{f}' of traffic stream '{t}' "
                            "packet rate to '{r}' frames per second".\
                            format(f=flow_group, t=traffic_stream, r=rate))

            # Get flow group object of the given traffic stream
            flowgroupObj = self.get_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

            # Change the packet rate as required
            try:
                self.ixNet.setMultiAttribute(flowgroupObj + '/frameRate',
                                                '-rate', rate,
                                                '-type', 'framesPerSecond')
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while changing flow group '{f}' of "
                                    "traffic stream '{t}' packet rate to '{r}'".\
                                    format(f=flow_group, t=traffic_stream, r=rate))
            else:
                logger.info("Successfully changed flow group '{f}' of traffic "
                            "stream '{t}' packet rate to '{r}' frames per second".\
                            format(f=flow_group, t=traffic_stream, r=rate))
        else:
            # Set the packet rate for the entire traffic stream
            logger.info("Setting traffic stream '{t}' packet rate to '{r}'"
                            " frames per second".format(t=traffic_stream, r=rate))

            # Initial state
            initial_state = self.get_traffic_attribute(attribute='state')

            # Stop traffic for the given stream
            if initial_state == 'started':
                self.stop_traffic(wait_time=stop_traffic_time)
            else:
                self.stop_traffic_stream(traffic_stream=traffic_stream, wait_time=stop_traffic_time)

            # Get config element object
            try:
                config_elements = self.ixNet.getList(ti_obj, 'configElement')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get config elements for traffic "
                                    "stream '{}'".format(traffic_stream))

            for config_element in config_elements:
                try:
                    self.ixNet.setMultiAttribute(config_element + '/frameRate',
                                                    '-rate', rate,
                                                    '-type', 'framesPerSecond')
                    self.ixNet.commit()
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while changing traffic stream "
                                        "'{t}' packet rate to '{r}' frames per "
                                        "second".format(t=traffic_stream, r=rate))
                else:
                    logger.info("Successfully changed traffic stream '{t}' packet "
                                "rate to '{r}' frames per second".\
                                format(t=traffic_stream, r=rate))

            # Generate traffic
            self.generate_traffic_stream(traffic_stream=traffic_stream, wait_time=generate_traffic_time)

            # Apply traffic
            self.apply_traffic(wait_time=apply_traffic_time)

            # Start traffic
            if start_traffic:
                if initial_state == 'started':
                    self.start_traffic(wait_time=start_traffic_time)
                else:
                    self.start_traffic_stream(traffic_stream=traffic_stream, wait_time=start_traffic_time)


    @isconnected
    def set_layer2_bit_rate(self, traffic_stream, rate, rate_unit, flow_group='', stop_traffic_time=15, generate_traffic_time=15, apply_traffic_time=15, start_traffic=True, start_traffic_time=15):
        '''Set the Layer2 bit rate for given traffic stream or given flow group
            within the traffic stream'''

        # Define units_dict
        units_dict = {
            'bps': 'bitsPerSec',
            'Kbps': 'kbitsPerSec',
            'Mbps': 'mbitsPerSec',
            'Bps': 'bytesPerSec',
            'KBps': 'kbytesPerSec',
            'MBps': 'mbytesPerSec',
            }

        # Verify valid units have been passed in
        try:
            assert rate_unit in ['bps', 'Kbps', 'Mbps', 'Bps', 'KBps', 'MBps']
        except AssertionError as e:
            raise AssertionError("Invalid unit '{}' passed in for layer2 bit rate".\
                                format(rate_unit))

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        if flow_group:
            # Set the layer2 bit rate for given flow group of this traffic item
            logger.info("Setting flow group '{f}' of traffic stream '{t}' "
                            "layer2 bit rate to '{r}' {u}".format(f=flow_group,
                                                                    t=traffic_stream,
                                                                    r=rate,
                                                                    u=rate_unit))

            # Get flow group object of the given traffic stream
            flowgroupObj = self.get_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

            # Change the layer2 bit rate as required
            try:
                self.ixNet.setMultiAttribute(flowgroupObj + '/frameRate',
                                                '-rate', rate,
                                                '-bitRateUnitsType', units_dict[rate_unit],
                                                '-type', 'bitsPerSecond')
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while changing flow group '{f}' of "
                                    "traffic stream '{t}' layer2 bit rate to "
                                    "'{r}' {u}".format(f=flow_group,
                                                        t=traffic_stream,
                                                        r=rate,
                                                        u=rate_unit))
            else:
                logger.info("Successfully changed flow group '{f}' of traffic "
                            "stream '{t}' layer2 bit rate to '{r}' {u}".\
                            format(f=flow_group, t=traffic_stream, r=rate, u=rate_unit))
        else:
            # Set the layer2 bit rate for the entire traffic stream
            logger.info("Setting traffic stream '{t}' layer2 bit rate to"
                            " '{r}' {u}".format(t=traffic_stream, r=rate, u=rate_unit))

            # Initial state
            initial_state = self.get_traffic_attribute(attribute='state')

            # Stop traffic for the given stream
            if initial_state == 'started':
                self.stop_traffic(wait_time=stop_traffic_time)
            else:
                self.stop_traffic_stream(traffic_stream=traffic_stream, wait_time=stop_traffic_time)

            # Get config element object
            try:
                config_elements = self.ixNet.getList(ti_obj, 'configElement')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get config elements for traffic "
                                    "stream '{}'".format(traffic_stream))

            for config_element in config_elements:
                try:
                    self.ixNet.setMultiAttribute(config_element + '/frameRate',
                                                    '-rate', rate,
                                                    '-bitRateUnitsType', units_dict[rate_unit],
                                                    '-type', 'bitsPerSecond')
                    self.ixNet.commit()
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while changing traffic stream "
                                        "'{t}' layer2 bit rate to '{r}' {u}".\
                                        format(t=traffic_stream,
                                                r=rate,
                                                u=rate_unit))
                else:
                    logger.info("Successfully changed traffic stream '{t}' layer2 "
                                "bit rate to '{r}' {u}".format(t=traffic_stream,
                                                            r=rate,
                                                            u=rate_unit))

            # Generate traffic
            self.generate_traffic_stream(traffic_stream=traffic_stream, wait_time=generate_traffic_time)

            # Apply traffic
            self.apply_traffic(wait_time=apply_traffic_time)

            # Start traffic
            if start_traffic:
                if initial_state == 'started':
                    self.start_traffic(wait_time=start_traffic_time)
                else:
                    self.start_traffic_stream(traffic_stream=traffic_stream, wait_time=start_traffic_time)


    @isconnected
    def set_packet_size_fixed(self, traffic_stream, packet_size, stop_traffic_time=15, generate_traffic_time=15, apply_traffic_time=15, start_traffic=True, start_traffic_time=15):
        '''Set the packet size for given traffic stream'''

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        # Set the packet size for the traffic stream
        logger.info("Setting traffic stream '{t}' packet size to '{p}'".\
                        format(t=traffic_stream, p=packet_size))

        # Initial state
        initial_state = self.get_traffic_attribute(attribute='state')

        # Stop traffic for the given stream
        if initial_state == 'started':
            self.stop_traffic(wait_time=stop_traffic_time)
        else:
            self.stop_traffic_stream(traffic_stream=traffic_stream, wait_time=stop_traffic_time)

        # Get config element object
        try:
            config_elements = self.ixNet.getList(ti_obj, 'configElement')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get config elements for traffic "
                                "stream '{}'".format(traffic_stream))

        for config_element in config_elements:
            try:
                self.ixNet.setMultiAttribute(config_element + '/frameSize',
                                                '-fixedSize', packet_size)
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while changing traffic stream "
                                    "'{t}' packet size to '{p}'".\
                                    format(t=traffic_stream, p=packet_size))
            else:
                logger.info("Successfully changed traffic stream '{t}' packet "
                            "size to '{p}'".format(t=traffic_stream, p=packet_size))

        # Generate traffic
        self.generate_traffic_stream(traffic_stream=traffic_stream, wait_time=generate_traffic_time)

        # Apply traffic
        self.apply_traffic(wait_time=apply_traffic_time)

        # Start traffic
        if start_traffic:
            if initial_state == 'started':
                self.start_traffic(wait_time=start_traffic_time)
            else:
                self.start_traffic_stream(traffic_stream=traffic_stream, wait_time=start_traffic_time)


    @isconnected
    def get_line_rate(self, traffic_stream, flow_group=''):
        '''Returns the line rate for given traffic stream or flow group'''

        # Init
        line_rate = None

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        if flow_group:
            # Get flow group object of the given traffic stream
            flowgroupObj = self.get_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

            # Set attribute to be the line rate
            try:
                self.ixNet.setAttribute(flowgroupObj + '/frameRate',
                                        '-type', 'percentLineRate')
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting line rate for flow "
                                    "group '{}'".format(flow_group))

            # Get the line rate
            try:
                line_rate = self.ixNet.getAttribute(flowgroupObj, '-rate')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting line rate for flow "
                                    "group '{}'".format(flow_group))

            # Return to caller
            if line_rate:
                return line_rate
            else:
                raise AssertionError("Unable to find line rate for flow "
                                    "group '{}".format(flow_group))
        else:
            # Get config element object
            try:
                config_elements = self.ixNet.getList(ti_obj, 'configElement')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get config elements for traffic "
                                    "stream '{}'".format(traffic_stream))

            for config_element in config_elements:
                # Set attribute to be the line rate
                try:
                    self.ixNet.setAttribute(config_element + '/frameRate',
                                            '-type', 'percentLineRate')
                    self.ixNet.commit()
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while getting line rate for "
                                        "traffic stream '{}'".format(traffic_stream))

                # Get the line rate
                try:
                    line_rate = self.ixNet.getAttribute(config_element + '/frameRate', '-rate')
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while getting line rate for "
                                        "traffic stream '{}'".format(traffic_stream))

            # Return to caller
            if line_rate:
                return line_rate
            else:
                raise AssertionError("Unable to find line rate for traffic "
                                    "stream '{}".format(traffic_stream))


    @isconnected
    def get_packet_rate(self, traffic_stream, flow_group=''):
        '''Returns the packet rate for given traffic stream or flow group'''

        # Init
        packet_rate = None

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        if flow_group:
            # Get flow group object of the given traffic stream
            flowgroupObj = self.get_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

            # Set attribute to be the packet rate
            try:
                self.ixNet.setAttribute(flowgroupObj + '/frameRate',
                                        '-type', 'framesPerSecond')
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting packet rate for flow "
                                    "group '{}'".format(flow_group))

            # Get the packet rate
            try:
                packet_rate = self.ixNet.getAttribute(flowgroupObj, '-rate')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting packet rate for flow "
                                    "group '{}'".format(flow_group))

            # Return to caller
            if packet_rate:
                return packet_rate
            else:
                raise AssertionError("Unable to find packet rate for flow "
                                    "group '{}".format(flow_group))
        else:
            # Get config element object
            try:
                config_elements = self.ixNet.getList(ti_obj, 'configElement')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get config elements for traffic "
                                    "stream '{}'".format(traffic_stream))

            for config_element in config_elements:
                # Set attribute to be the packet rate
                try:
                    self.ixNet.setAttribute(config_element + '/frameRate',
                                            '-type', 'framesPerSecond')
                    self.ixNet.commit()
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while getting packet rate for "
                                        "traffic stream '{}'".format(traffic_stream))

                # Get the packet rate
                try:
                    packet_rate = self.ixNet.getAttribute(config_element + '/frameRate', '-rate')
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while getting packet rate for "
                                        "traffic stream '{}'".format(traffic_stream))

            # Return to caller
            if packet_rate:
                return packet_rate
            else:
                raise AssertionError("Unable to find packet rate for traffic "
                                    "stream '{}".format(traffic_stream))


    @isconnected
    def get_layer2_bit_rate(self, traffic_stream, flow_group=''):
        '''Returns the layer2 bit rate given traffic stream or flow group'''

        # Init
        layer2bit_rate = None

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        if flow_group:
            # Get flow group object of the given traffic stream
            flowgroupObj = self.get_flow_group_object(traffic_stream=traffic_stream, flow_group=flow_group)

            # Set attribute to be the layer2 bit rate
            try:
                self.ixNet.setAttribute(flowgroupObj + '/frameRate',
                                        '-type', 'bitsPerSecond')
                self.ixNet.commit()
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting layer2 bit rate for "
                                    "flow group '{}'".format(flow_group))

            # Get the layer2 bit rate
            try:
                layer2bit_rate = self.ixNet.getAttribute(flowgroupObj, '-rate')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting layer2 bit rate for "
                                    "flow group '{}'".format(flow_group))

            # Return to caller
            if layer2bit_rate:
                return layer2bit_rate
            else:
                raise AssertionError("Unable to find layer2 bit rate for flow "
                                    "group '{}".format(flow_group))
        else:
            # Get config element object
            try:
                config_elements = self.ixNet.getList(ti_obj, 'configElement')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to get config elements for traffic "
                                    "stream '{}'".format(traffic_stream))

            for config_element in config_elements:
                # Set attribute to be the layer2 bit rate
                try:
                    self.ixNet.setAttribute(config_element + '/frameRate',
                                            '-type', 'bitsPerSecond')
                    self.ixNet.commit()
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while getting layer2 bit rate for "
                                        "traffic stream '{}'".format(traffic_stream))

                # Get the layer2 bit rate
                try:
                    layer2bit_rate = self.ixNet.getAttribute(config_element + '/frameRate', '-rate')
                except Exception as e:
                    logger.error(e)
                    raise AssertionError("Error while getting layer2 bit rate for "
                                        "traffic stream '{}'".format(traffic_stream))

            # Return to caller
            if layer2bit_rate:
                return layer2bit_rate
            else:
                raise AssertionError("Unable to find packet rate for traffic "
                                    "stream '{}".format(traffic_stream))


    @isconnected
    def get_packet_size(self, traffic_stream):
        '''Returns the packet size for given traffic stream'''

        # Init
        packet_size = None

        # Get traffic item object from stream name
        ti_obj = self.find_traffic_stream_object(traffic_stream=traffic_stream)

        # Get config element object
        try:
            config_elements = self.ixNet.getList(ti_obj, 'configElement')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get config elements for traffic "
                                "stream '{}'".format(traffic_stream))

        for config_element in config_elements:
            try:
                packet_size = self.ixNet.getAttribute(config_element + '/frameSize', '-fixedSize')
            except Exception as e:
                logger.error(e)
                raise AssertionError("Error while getting the packet size for"
                                    " '{p}'".format(t=traffic_stream))

        # Return to caller
        if packet_size:
            return packet_size
        else:
            raise AssertionError("Unable to find packet rate for traffic "
                                "stream '{}".format(traffic_stream))


    #--------------------------------------------------------------------------#
    #                               QuickTest                                  #
    #--------------------------------------------------------------------------#

    @isconnected
    def find_quicktest_object(self, quicktest):
        '''Finds and returns the QuickTest object for the specific test'''

        # Ensure valid QuickTest types have been passed in
        try:
            assert quicktest in self.valid_quicktests
        except AssertionError as e:
            raise AssertionError("Invalid QuickTest '{q}' provided.\nValid "
                                "options are {l}".format(q=quicktest, l=self.valid_quicktests))

        # Get QuickTest root
        qt_root = None
        try:
            qt_root = self.ixNet.getList(self.ixNet.getRoot(), 'quickTest')[0]
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get QuickTest root object")

        # Get list of QuickTests configured on Ixia
        try:
            qt_list = self.ixNet.getAttribute(qt_root, '-testIds')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get list of QuickTests configured")

        # Get specific QuickTest test
        qt_obj = None
        for item in qt_list:
            if quicktest in item:
                qt_obj = item
                break

        # Return to caller
        if qt_obj:
            return qt_obj
        else:
            raise AssertionError("Unable to find ::ixNet:: object for QuickTest "
                                "'{}'".format(quicktest))


    @isconnected
    def get_quicktest_results_attribute(self, quicktest, attribute):
        '''Returns the value of the specified Quicktest results object attribute.'''

        # Verify valid attribute provided
        try:
            assert attribute in ['isRunning',
                                    'status',
                                    'progress',
                                    'result',
                                    'resultPath',
                                    'startTime',
                                    'duration']
        except AssertionError as e:
            raise AssertionError("Invalid attribute '{}' provided for Quicktest "
                                "results".format(attribute))

        # Get QuickTest object
        qt_obj = self.find_quicktest_object(quicktest=quicktest)

        # Return attribute value
        try:
            return self.ixNet.getAttribute(qt_obj+'/results', '-{}'.format(attribute))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to get value of Quicktest results "
                                "attribute '{}'".format(attribute))


    @isconnected
    def load_quicktest_configuration(self, configuration, wait_time=30):
        '''Load QuickTest configuration file'''

        logger.info("Loading Quicktest configuration...")

        # Load the QuickTest configuration file onto Ixia
        try:
            load_config = self.ixNet.execute('loadConfig',
                                                self.ixNet.readFrom(configuration))
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to load Quicktest configuration file "
                                "'{f}' onto device '{d}'".format(f=configuration,
                                d=self.name)) from e

        # Verify return
        try:
            assert load_config == _PASS
        except AssertionError as e:
            logger.error(load_config)
            raise AssertionError("Unable to load Quicktest configuration file "
                                "'{f}' onto device '{d}'".format(f=configuration,
                                d=self.name)) from e
        else:
            logger.info("Successfully loaded Quicktest configuration file '{f}' "
                        "onto device '{d}'".format(f=configuration,
                        d=self.name))

        # Wait after loading configuration file
        logger.info("Waiting for '{}' seconds after loading configuration...".\
                    format(wait_time))
        time.sleep(wait_time)

        # Verify traffic is in 'unapplied' state
        logger.info("Verify traffic is in 'unapplied' state after loading configuration")
        try:
            assert self.get_traffic_attribute(attribute='state') == 'unapplied'
        except AssertionError as e:
            raise AssertionError("Traffic is not in 'unapplied' state after "
                                "loading configuration onto device '{}'".\
                                format(self.name)) from e
        else:
            logger.info("Traffic in 'unapplied' state after loading configuration "
                        "onto device '{}'".format(self.name))


    @isconnected
    def execute_quicktest(self, quicktest, apply_wait=60, exec_wait=1800, exec_interval=300, save_location="C:\\Users\\"):
        '''Execute specific RFC QuickTest'''

        logger.info("Prepare execution of Quicktest '{}'...".\
                        format(quicktest))

        # Get QuickTest object
        qt_obj = self.find_quicktest_object(quicktest=quicktest)

        # Apply QuickTest configuration
        logger.info("Apply QuickTest '{}' configuration".format(quicktest))
        try:
            apply_qt = self.ixNet.execute('apply', qt_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to apply traffic configuration for "
                                "QuickTest '{}'".format(quicktest))

        # Verify QuickTest configuration application passed
        try:
            assert apply_qt == _PASS
        except AssertionError as e:
            logger.error(apply_qt)
            raise AssertionError("Unable to apply QuickTest '{}' configuration".\
                                format(quicktest))
        else:
            logger.info("Successfully applied QuickTest '{}' configuration".\
                        format(quicktest))

        # Wait after applying QuickTest configuration
        logger.info("Waiting '{}' seconds after applying QuickTest "
                    "configuration".format(apply_wait))
        time.sleep(apply_wait)

        # Enable QuickTest report
        logger.info("Enable QuickTest '{}' report generation".format(quicktest))
        try:
            self.ixNet.setMultiAttribute('::ixNet::OBJ-/quickTest/globals',
                                            '-enableGenerateReportAfterRun', 'true',
                                            '-useDefaultRootPath', 'false',
                                            '-outputRootPath', save_location,
                                            '-titlePageComments',
                                            "QuickTest {} Robot Test Result".\
                                            format(quicktest))
            self.ixNet.commit()
        except Exception as e:
            logger.error(e)
            raise AssertionError("Error while enabling PDF report genaration")
        else:
            logger.info("Successfully enabled QuickTest '{}' report generation".\
                        format(quicktest))

        # Start QuickTest execution
        logger.info("Start execution of QuickTest '{}'".format(quicktest))
        try:
            start_qt = self.ixNet.execute('start', qt_obj)
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to start execution of Quicktest"
                                " '{}'".format(quicktest))

        # Verify QuickTest successfully started
        try:
            assert start_qt == _PASS
        except AssertionError as e:
            logger.error(start_qt)
            raise AssertionError("Unable to start execution of QuickTest '{}'".\
                                format(quicktest))
        else:
            logger.info("Successfully started execution of QuickTest '{}'".\
                        format(quicktest))

        # Poll until execution has completed
        logger.info("Poll until Quicktest '{}' execution completes".format(quicktest))
        timeout = Timeout(max_time=exec_wait, interval=exec_interval)
        while timeout.iterate():
            if self.get_quicktest_results_attribute(quicktest=quicktest, attribute='isRunning') == 'false':
                break

        # Print test exeuction duration to user
        duration = self.get_quicktest_results_attribute(quicktest=quicktest, attribute='duration')
        start_time = self.get_quicktest_results_attribute(quicktest=quicktest, attribute='startTime')
        result = self.get_quicktest_results_attribute(quicktest=quicktest, attribute='result')
        logger.info("Quicktest '{}' execution completed:".format(quicktest))
        logger.info("-> Test Duration = {d}\n"
                    "-> Start Time = {s}\n"
                    "-> Overall Result = {r}".\
                    format(q=quicktest, d=duration, s=start_time, r=result))


    @isconnected
    def generate_export_quicktest_report(self, quicktest, report_wait=300, report_interval=60, export=True, dest_dir='', dest_file="TestReport.pdf"):
        '''Generate QuickTest PDF report and return the location'''

        logger.info("Generating PDF report for Quicktest {}...".\
                        format(quicktest))

        # Get QuickTest object
        qt_obj = self.find_quicktest_object(quicktest=quicktest)

        # Generate the PDF report
        logger.info("Start generating PDF report...")
        try:
            self.ixNet.execute('generateReport', '/reporter/generate')
        except Exception as e:
            logger.error(e)
            raise AssertionError("Unable to start generating PDF report for "
                                "Quicktest '{}'".format(quicktest))
        else:
            logger.info("Successfully started generating PDF report for "
                        "Quicktest '{}'".format(quicktest))

        # Poll until report has successfully generated
        logger.info("Poll until Quicktest '{}' PDF report is generated...".\
                    format(quicktest))
        timeout = Timeout(max_time=report_wait, interval=report_interval)
        while timeout.iterate():
            if self.ixNet.getAttribute(self.ixNet.getRoot() +'/reporter/generate', '-state') == 'done':
                break

        # Get QuickTest report results path
        qt_pdf_path = self.get_quicktest_results_attribute(quicktest=quicktest, attribute='resultPath')
        # Set filenames
        qt_pdf_file = qt_pdf_path + "\\\\TestReport.pdf"
        dest_pdf_file = dest_dir + "/" + dest_file
        temp_file = "/tmp/" + dest_file
        logger.info("Quicktest '{q}' PDF report successfully generated at: {d}".\
                    format(q=quicktest, d=qt_pdf_file))

        # Export file if enabled by user
        if export:
            logger.info("Exporting Quicktest '{}' PDF report".format(quicktest))

            # Exporting the QuickTest PDF file to /tmp on running server
            try:
                self.ixNet.execute('copyFile',
                                    self.ixNet.readFrom(qt_pdf_file, '-ixNetRelative'),
                                    self.ixNet.writeTo(temp_file, '-overwrite'))
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to export Quicktest '{q}' PDF report".\
                                    format(q=quicktest))

            # Now copy from /tmp to runtime.directory
            try:
                copyfile(temp_file, dest_pdf_file)
            except Exception as e:
                logger.error(e)
                raise AssertionError("Unable to export Quicktest '{q}' PDF "
                                    "report to '{d}'".format(q=quicktest,
                                                                d=dest_pdf_file))
            else:
                logger.info("Successfully exported Quicktest '{q}' PDF report to "
                            "'{d}'".format(q=quicktest, d=dest_pdf_file))