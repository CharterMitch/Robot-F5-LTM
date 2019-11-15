ltm rule /Common/nettool {
    when HTTP_REQUEST { 
        if { [HTTP::uri] equals "/"} {
                HTTP::redirect "https://[HTTP::host]/ibm/console/"  
                 }
            }
}