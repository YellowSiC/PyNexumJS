
JsPyQueue = {};
// constants ***************************
JsPyQueue.VERSION = '0.0.0';
// valiable ****************************
JsPyQueue._queue_id = 0;
JsPyQueue._queue_stack = new Map();
JsPyQueue._queue_memory = new Map();
JsPyQueue._queue_callbacks = [];

JsPyQueue.push_nowait = (key) => {
    function inner(data){
        JsPyQueue._queue_id += 1;
        if(JsPyQueue._queue_id > SiC._MAX_ID){
            JsPyQueue._queue_id = 1;
        }
        let this_id = JsPyQueue._queue_id;
        send_obj = {'protocol': 'queue', 'key': key, 'id': this_id,
                    'data': data, 'exception': null};
        if(! SiC.send_json(send_obj)){
            throw new Error("Could not send to server @javascript")
        }
    }
    return(inner);
};

JsPyQueue.push = (key, timeout=0) => {
    async function inner(data){
        JsPyQueue._queue_id += 1;
        if(JsPyQueue._queue_id > SiC._MAX_ID){
            JsPyQueue._queue_id = 1;
        }
        let this_id = JsPyQueue._queue_id;
        let send_obj = {'protocol': 'queue_call', 'key': key, 'id': this_id,
                        'data': data, 'exception': null};
        let call_promise = new Promise((resolve, reject) => {
            JsPyQueue._queue_memory.set(this_id, [resolve, reject]);
            if(! SiC.send_json(send_obj)){
                reject("Unable to communicate with the server @javascript");
            }
        });
        try{
            if(timeout === null || timeout <= 0){
                await call_promise;
            }
            else{
                await Promise.race([call_promise, SiC._time_raise(timeout)]);
            }
        }
        catch(error){
            return(false);
        }
        finally{
            JsPyQueue._queue_memory.delete(this_id);
        }
        return(true);
    }
    return(inner);
};

JsPyQueue.pop = (key, default_value=undefined) => {
    if(JsPyQueue._queue_stack.has(key)){
        let key_array = JsPyQueue._queue_stack.get(key);
        if(key_array.length == 0){
            return(default_value);
        }
        else{
            return(key_array.pop());
        }
    }
    else{
        return(default_value);
    }
};

JsPyQueue.shift = (key, default_value=undefined) => {
    if(JsPyQueue._queue_stack.has(key)){
        let key_array = JsPyQueue._queue_stack.get(key);
        if(key_array.length == 0){
            return(default_value);
        }
        else{
            return(key_array.shift());
        }
    }
    else{
        return(default_value);
    }
};

JsPyQueue.add_callback = (func) => {
    JsPyQueue._queue_callbacks.push(func);
};

JsPyQueue.clear_callback = () => {
    JsPyQueue._queue_callbacks.length = 0;
};

JsPyQueue.is_empty = (key) => {
    if(JsPyQueue._queue_stack.has(key)){
        return(JsPyQueue._queue_stack.get(key).length == 0);
    }
    else{
        return(true);
    }
};

JsPyQueue.get_keys = () => {
    return(Array.from(JsPyQueue._queue_stack.keys()));
};

JsPyQueue.has = (key) => {
    return(JsPyQueue._queue_stack.has(key));
};

JsPyQueue.clear = (key) => {
    if(JsPyQueue._queue_stack.has(key)){
        JsPyQueue._queue_stack.get(key).length = 0;
    }
};

JsPyQueue.clear_all = () => {
    for(let key of JsPyQueue._queue_stack.keys()){
        JsPyQueue._queue_stack.get(key).length = 0;
    }
};

JsPyQueue.remove = (key) => {
    JsPyQueue._queue_stack.delete(key);
};

JsPyQueue.remove_all = () => {
    JsPyQueue._queue_stack.clear();
};

JsPyQueue._queue = (obj_data) => {
    if(JsPyQueue._queue_stack.has(obj_data['key'])){
        JsPyQueue._queue_stack.get(obj_data['key']).push(obj_data['data']);
    }
    else{
        JsPyQueue._queue_stack.set(obj_data['key'], [obj_data['data']]);
    }
    if(obj_data['protocol'] === 'queue_call'){
        send_obj = {'protocol': 'queue_return', 'key': obj_data['key'],
                    'id': obj_data['id'], 'data': null, 'exception': null};
        SiC.send_json(send_obj);
    }
    for(let callback of JsPyQueue._queue_callbacks){
        try{
            callback(obj_data['key']);
        }
        catch(e){
            // Do nothing
        }
    }
};

JsPyQueue._queue_return = (obj_data) => {
    let id = obj_data['id'];
    let success = (obj_data['exception'] === null);
    if(JsPyQueue._queue_memory.has(id)){
        if(success){
            // resolve(true);
            JsPyQueue._queue_memory.get(id)[0](true);
        }
        else{
            // reject("error message...")
            JsPyQueue._queue_memory.get(id)[1](obj_data['exception']);
        }
    }
};

SiC._add_protocol('queue', JsPyQueue._queue);
SiC._add_protocol('queue_call', JsPyQueue._queue);
SiC._add_protocol('queue_return', JsPyQueue._queue_return);
