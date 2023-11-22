let SiC = {};
SiC.VERSION = '0.0.0';
SiC._URL_PATH = '/jsmeetspy/textsocket';
SiC._MAX_ID = 0XFFFFFFFF;
SiC._protocol_table = new Map();
SiC._socket_events = new Array();
SiC._socket_id = null;
SiC._disconnect_reason = 'It has not been initialized yet.';
SiC._websocket = null;
SiC._url = null;

SiC.reconnect = (url) => {
    if(SiC._websocket !== null && SiC._websocket.readyState !== WebSocket.CLOSED){
        return(false);
    }
    try{
        SiC._websocket = new WebSocket(url);
    }
    catch(e){
        SiC._websocket = null;
        SiC._socket_id = null;
        SiC._disconnect_reason = 'It has not been initialized yet.';
        return(false);
    }
    SiC._websocket.onmessage = (event) => {
        try{
            let msg_obj = JSON.parse(event.data);
            if('protocol' in msg_obj && 'key' in msg_obj && 'id' in msg_obj &&
                'data' in msg_obj && 'exception' in msg_obj && SiC._protocol_table.has(msg_obj['protocol'])){
                SiC._protocol_table.get(msg_obj['protocol'])(msg_obj);
            }
        }
        catch(e){
            // Do nothing
        }
    };
    SiC._websocket.onclose = (event) => {
        for(let fn of SiC._socket_events){
            try{
                fn();
            }
            catch(e){
                // Do nothing
            }
        }
        SiC._socket_id = null;
    };
    return(true);
};

SiC.init = SiC.reconnect;

SiC.close = () => {
    if(SiC._websocket !== null && SiC._websocket.readyState === WebSocket.OPEN){
        SiC._websocket.close();
        return(true);
    }
    else{
        return(false);
    }
}

SiC.ready = () => {
    return(SiC._websocket !== null && SiC._websocket.readyState === WebSocket.OPEN);
};

SiC.send_json = (send_obj) => {
    if(SiC._websocket !== null && SiC._websocket.readyState === WebSocket.OPEN){
        try{
            SiC._websocket.send(JSON.stringify(send_obj));
            return(true);
        }
        catch(e){
            return(false);
        }
    }
    else{
        return(false);
    }
};

SiC.get_socket_id = () => {
    return(SiC._socket_id);
};

SiC._add_protocol = (protocol, func) => {
    SiC._protocol_table.set(protocol, func);
};

SiC.add_close_event = (func) => {
    SiC._socket_events.push(func);
};

SiC.clear_close_event = () => {
    SiC._socket_events.length = 0;
};
// Processes data with protocol 'system'
SiC._add_protocol('system', (obj_data) => {
    if(obj_data['key'] === 'connect'){
        let data = obj_data['data'];
        let except = obj_data['exception'];
        if(except){
            SiC._socket_id = null;
            SiC._disconnect_reason = except;
        }
        else{
            SiC._socket_id = data;
            SiC._disconnect_reason = '';
        }
    }
});

SiC._time_raise = (wake_sec) => {
    return(new Promise((resolve, reject) => {
           setTimeout(() => {reject("A timeout has occurred @javascript");}, Math.floor(wake_sec*1000));
    }));
};

// Initial settings
// Initial settings
if(window.location.protocol === 'http:'){
    SiC._url = 'ws://'+window.location.host+SiC._URL_PATH;
    SiC.init(SiC._url);
}
else if(window.location.protocol === 'https:'){
    SiC._url = 'wss://'+window.location.host+SiC._URL_PATH;
    SiC.init(SiC._url);
}
else{
    SiC._url = null;
}