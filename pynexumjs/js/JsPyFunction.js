
JsPyFunction = {};
// constants ***************************
JsPyFunction.VERSION = '0.0.0';
// valiable ****************************
JsPyFunction._exposed_function = new Map();
JsPyFunction._call_id = 0;
JsPyFunction._call_memory = new Map();

JsPyFunction.expose = (key, func, exclusive=false) => {
    if(JsPyFunction._exposed_function.has(key) && JsPyFunction._exposed_function.get(key)[2]){
        return(false);
    }
    JsPyFunction._exposed_function.set(key, [func, func.constructor.name === "AsyncFunction", false, exclusive ? []: null]);
    return(true);
};

JsPyFunction.clear = (key) => {
    if(JsPyFunction._exposed_function.has(key) && ! JsPyFunction._exposed_function.get(key)[2]){
        JsPyFunction._exposed_function.delete(key);
        return(true);
    }
    return(false);
};

JsPyFunction.is_running = (key) => {
    if(JsPyFunction._exposed_function.has(key)){
        return(JsPyFunction._exposed_function.get(key)[2]);
    }
    return(false);
};

JsPyFunction.get_keys = () => {
    return(Array.from(JsPyFunction._exposed_function.keys()));
};

JsPyFunction.has = (key) => {
    return(JsPyFunction._exposed_function.has(key));
};

JsPyFunction.call_nowait = (key) => {
    function inner(){
        JsPyFunction._call_id += 1;
        if(JsPyFunction._call_id > SiC._MAX_ID){
            JsPyFunction._call_id = 1;
        }
        let this_id = JsPyFunction._call_id;
        let send_obj = {'protocol': 'function', 'key': key, 'id': this_id,
                        'data': Array.from(arguments), 'exception': null};
        if(! SiC.send_json(send_obj)){
            throw new Error("Could not send to server @javascript");
        }
    }
    return(inner);
};

JsPyFunction.call = (key, timeout=0) => {
    async function inner(){
        JsPyFunction._call_id += 1;
        if(JsPyFunction._call_id > SiC._MAX_ID){
            JsPyFunction._call_id = 1;
        }
        let this_id = JsPyFunction._call_id;
        let send_obj = {'protocol': 'function_call', 'key': key, 'id': this_id,
                        'data': Array.from(arguments), 'exception': null};
        let call_promise = new Promise((resolve, reject) => {
            JsPyFunction._call_memory.set(this_id, [resolve, reject]);
            if(! SiC.send_json(send_obj)){
                reject("Unable to communicate with the server @javascript");
            }
        });

        let return_value;
        try{
            if(timeout === null || timeout <= 0){
                return_value = await call_promise;
            }
            else{
                return_value = await Promise.race([call_promise, SiC._time_raise(timeout)]);
            }
        }
        catch(error){
            throw new Error(error);
        }
        finally{
            JsPyFunction._call_memory.delete(this_id);
        }
        return(return_value);
    }
    return(inner);
};

JsPyFunction._return_from_py = (obj_data) => {
    let id = obj_data['id'];
    let data = obj_data['data'];
    let except = obj_data['exception'];
    if(JsPyFunction._call_memory.has(id)){
        if(!except){
            // resolve(data);
            JsPyFunction._call_memory.get(id)[0](data);
        }
        else{
            // reject(except);
            JsPyFunction._call_memory.get(id)[1](except);
        }
    }
};

SiC._add_protocol('function_return', JsPyFunction._return_from_py);
/**
 * Processes data with protocol 'function_call', 'function'
 */
JsPyFunction._call_from_py = async (obj_data) => {
    let key = obj_data['key'];
    let protocol = obj_data['protocol'];
    let send_obj = {'protocol': 'function_return', 'key': key,
                     'id': obj_data['id'], 'data': null, 'exception': null};
    if(! JsPyFunction._exposed_function.has(key)){
        send_obj['exception'] = 'Function key name is not registered @javascript';
    }
    else{
        let functional_set = JsPyFunction._exposed_function.get(key);
        let func = functional_set[0];
        let is_async = functional_set[1];
        let is_running = functional_set[2];
        let exclusive = functional_set[3];
        if(exclusive !== null && is_running){
            await(new Promise((resolve) => {exclusive.push(resolve);}));
        }
        functional_set[2] = true;
        try{
            if(is_async){
                send_obj['data'] = await func(...obj_data['data']);
            }
            else{
                send_obj['data'] = func(...obj_data['data']);
            }
        }
        catch(e){
            send_obj['data'] = null;
            send_obj['exception'] = "Javascript function raised exception @javascript";
        }
        if(exclusive !== null && exclusive.length > 0){
            exclusive.shift()(true);
        }
        else{
            functional_set[2] = false;
        }
    }
    if(protocol === 'function_call'){
        if(! SiC.send_json(send_obj)){
            send_obj['data'] = null;
            send_obj['exception'] = "Javascript function return value does not conform to JSON format @javascript";
            SiC.send_json(send_obj);
        }
    }
};

SiC._add_protocol('function_call', JsPyFunction._call_from_py);
SiC._add_protocol('function', JsPyFunction._call_from_py);
