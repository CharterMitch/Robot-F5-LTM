from pysnmp.hlapi import setCmd, SnmpEngine, CommunityData, UdpTransportTarget
from pysnmp.hlapi import ContextData, ObjectType, ObjectIdentity, Unsigned32
from robot.api.deco import keyword
from robot.api import logger


@keyword("Cross-connect polatis port ${port} to ${oxc}")
def polatis_oxc(port, oxc):
    """ Use SNMP to run cross-connects on a Polatis optical switch.
    To delete a cross-connect set oxc to 0.

    Example: polatis_oxc(2,194) connects Ingress port 2 with Egress port 194
    """
    # logger.warn('Polatis SNMP cross-connect {},{}'.format(port, oxc))
    polatis = 'mts01sqsccc.spoc.charterlab.com'
    oid = '1.3.6.1.4.1.26592.2.2.2.1.2.1.2.{}'
    g = setCmd(SnmpEngine(),
               CommunityData('private'),
               UdpTransportTarget((polatis, 161)),
               ContextData(),
               ObjectType(
                   # First Port
                   ObjectIdentity(oid.format(port)),
                   # Second Port
                   Unsigned32(oxc)
               ))
    next(g)
