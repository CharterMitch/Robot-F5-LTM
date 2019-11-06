*** Settings ****
Variables   settings.yaml
Library     Polatis.py
Library     IxLoadRobot.py   ${ixload}[site_url]   ${ixload}[ixload_version]

*** Keywords ***
Start Ixia Test
    [Documentation]     Start an IXIA test given an .rxf file name.
    [Arguments]         ${rxf_file}  
    #Load rxf '${ixia_test_dir}\\${rxf_file}'
    Load rxf 'C:\\Users\\mmahan\\Documents\\${rxf_file}'
    start ixload test

Stop Ixia Test
    [Documentation]     Gravefully stop a running IXIA test.
    stop ixload test