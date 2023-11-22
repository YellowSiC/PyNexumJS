
JsPyPubsub = {};
// constants ***************************
JsPyPubsub.VERSION = '0.0.0';
// valiable ****************************
JsPyPubsub._pubsub_id = 0;
JsPyPubsub._topic_callback = new Map();
JsPyPubsub._call_memory = new Map();

JsPyPubsub.subscribe = async (topic, func, timeout=0) => {
    JsPyPubsub._pubsub_id += 1;
    if(JsPyPubsub._pubsub_id > SiC._MAX_ID){
        JsPyPubsub._pubsub_id = 1;
    }
    let this_id = JsPyPubsub._pubsub_id;
    let send_obj = {'protocol': 'sub_call', 'key': topic, 'id': this_id,
                    'data': null, 'exception': null};
    if(! SiC.send_json(send_obj)){
        return(false);
    }
    let call_promise = new Promise((resolve, reject) => {
        JsPyPubsub._call_memory.set(this_id, [resolve, reject]);
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
        JsPyPubsub._call_memory.delete(this_id);
    }
    JsPyPubsub._topic_callback.set(topic, func);
    return(true);
};

JsPyPubsub.unsubscribe = async (topic, timeout=0) => {
    if(! JsPyPubsub._topic_callback.has(topic)){
        return(false);
    }
    JsPyPubsub._pubsub_id += 1;
    if(JsPyPubsub._pubsub_id > SiC._MAX_ID){
        JsPyPubsub._pubsub_id = 1;
    }
    let this_id = JsPyPubsub._pubsub_id;
    let send_obj = {'protocol': 'unsub_call', 'key': topic, 'id': this_id,
                    'data': null, 'exception': null};
    if(! SiC.send_json(send_obj)){
        return(false);
    }
    let call_promise = new Promise((resolve, reject) => {
        JsPyPubsub._call_memory.set(this_id, [resolve, reject]);
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
        JsPyPubsub._call_memory.delete(this_id);
    }
    JsPyPubsub._topic_callback.delete(topic);
    return(true);
};

JsPyPubsub.publish = (topic, suppress=false, timeout=0) => {
    async function inner(data){
        JsPyPubsub._pubsub_id += 1;
        if(JsPyPubsub._pubsub_id > SiC._MAX_ID){
            JsPyPubsub._pubsub_id = 1;
        }
        let this_id = JsPyPubsub._pubsub_id;
        let send_obj = {'protocol': 'pub_call', 'key': topic, 'id': this_id,
                        'data': data, 'exception': suppress};
        if(! SiC.send_json(send_obj)){
            return(false);
        }
        let call_promise = new Promise((resolve, reject) => {
            JsPyPubsub._call_memory.set(this_id, [resolve, reject]);
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
            JsPyPubsub._call_memory.delete(this_id);
        }
        return(true);
    }
    return(inner);
};

JsPyPubsub.get_topics = () => {
    return(Array.from(JsPyPubsub._topic_callback.keys()));
};

JsPyPubsub._return_call = (obj_data) => {
    let id = obj_data['id'];
    let success = (obj_data['exception'] === null);
    if(JsPyPubsub._call_memory.has(id)){
        if(success){
            // resolve(true);
            JsPyPubsub._call_memory.get(id)[0](true);
        }
        else{
            // reject("error message...")
            JsPyPubsub._call_memory.get(id)[1](obj_data['exception']);
        }
    }
};

JsPyPubsub._pub = (obj_data) => {
    let topic = obj_data['key'];
    let data = obj_data['data'];
    try{
        if(JsPyPubsub._topic_callback.has(topic)){
            JsPyPubsub._topic_callback.get(topic)(topic, data);
        }
    }
    catch(e){
        // Do nothing
    }
};

SiC._add_protocol('pub_return', JsPyPubsub._return_call);
SiC._add_protocol('sub_return', JsPyPubsub._return_call);
SiC._add_protocol('unsub_return', JsPyPubsub._return_call);
SiC._add_protocol('pub', JsPyPubsub._pub);
