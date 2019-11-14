*** Settings ***
Documentation    Setup virtual servers, nodes and pool for F5 testing.
Resource        ../common.resource
Variables       settings.yaml
Library         ../F5Rest.py    ${f5_primary}     ${user}
Suite Setup     Configure F5
Suite Teardown  Teardown

*** Keywords ***
Configure F5
    [Documentation]     Setup nodes, pools and virtual servers to use
    ...                 in Load Balancing test cases.
    ...                 Variables are from the settings.yaml file in this folder.
    [tags]  Setup
    Log variables
    # Configure v4 Nodes and Pools
    tmsh create ltm node ${node_1} address ${node_1}
    tmsh create ltm node ${node_2} address ${node_2}
    tmsh create ltm pool ${pool} { members add { ${node_1}:80 ${node_2}:80 } monitor none }
    tmsh create ltm virtual ${virtual_server} destination ${virtual_server}:80 mask 255.255.255.255 ip-protocol tcp pool ${pool}
    tmsh create ltm virtual https-${virtual_server} destination ${virtual_server}:443 mask 255.255.255.255 ip-protocol tcp pool ${pool} profiles add { clientssl { context clientside }}
    tmsh modify ltm virtual-address ${virtual_server} route-advertisement selective
    # Configure V6 Nodes and Pools
    tmsh create ltm node ${v6_node_1} address ${v6_node_1}
    tmsh create ltm node ${v6_node_2} address ${v6_node_2}
    tmsh create ltm pool ${v6_pool} { members add { ${v6_node_1}.80 ${v6_node_2}.80 } monitor none }
    tmsh create ltm virtual ${v6_virtual_server} destination ${v6_virtual_server_ip}.80 ip-protocol tcp pool ${v6_pool}
    tmsh create ltm virtual https-${v6_virtual_server} destination ${v6_virtual_server_ip}.443 ip-protocol tcp pool ${v6_pool} profiles add { clientssl { context clientside }}
    tmsh modify ltm virtual-address ${v6_virtual_server_ip} route-advertisement selective

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    # Delete v4 config
    tmsh delete ltm virtual ${virtual_server}
    tmsh delete ltm virtual https-${virtual_server}
    tmsh delete ltm pool ${pool}
    tmsh delete ltm node ${node_1}
    tmsh delete ltm node ${node_2}
    # Delete v6 config
    tmsh delete ltm virtual ${v6_virtual_server}
    tmsh delete ltm virtual https-${v6_virtual_server}
    tmsh delete ltm pool ${v6_pool}
    tmsh delete ltm node ${v6_node_1}
    tmsh delete ltm node ${v6_node_2}