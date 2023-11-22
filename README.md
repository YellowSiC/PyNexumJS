# PyNexumJS

Connect Python to JavaScript Bidirectional

<p align="center">
  <a href="https://www.yellow-sic.com/">
    <img width="100" src="logo.png" alt="PyNexumJS Logo">
  </a>
</p>

<h2 align="center" style="color: blue; font-size: 24px;">PyNexumJS is a FastAPI capsule library that facilitates server functions and introduces various features.</h2>

<div align="center">
  <p>
    With PyNexumJS, you can seamlessly call Python functions from JavaScript and vice versa. 
    Send arbitrary data from JavaScript to the Python side, and vice versa, enabling real-time bidirectional communication without the need for Ajax.
  </p>

  <p>
    Similar to MQTT, PyNexumJS allows the publication and subscription of arbitrary data via topics.
  </p>
</div>

## 🖥 Environment Support

- Modern browsers
- Client-side Rendering

## Browsers support

| ![IE / Edge](https://raw.githubusercontent.com/alrra/browser-logos/master/src/edge/edge_48x48.png) | ![Firefox](https://raw.githubusercontent.com/alrra/browser-logos/master/src/firefox/firefox_48x48.png) | ![Chrome](https://raw.githubusercontent.com/alrra/browser-logos/master/src/chrome/chrome_48x48.png) | ![Safari](https://raw.githubusercontent.com/alrra/browser-logos/master/src/safari/safari_48x48.png) | ![iOS Safari](https://raw.githubusercontent.com/alrra/browser-logos/master/src/safari-ios/safari-ios_48x48.png) | ![Samsung](https://raw.githubusercontent.com/alrra/browser-logos/master/src/samsung-internet/samsung-internet_48x48.png) | ![Opera](https://raw.githubusercontent.com/alrra/browser-logos/master/src/opera/opera_48x48.png) |
| --- | --- | --- | --- | --- | --- | --- |
| IE11, Edge| last 2 versions| last 2 versions| last 2 versions| last 2 versions| last 2 versions| last 2 versions 

## 📦 Install

```bash
pip install pynexumjs

```

### index.html
```html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>PyNexumJS</title>

  <link href="https://cdn.jsdelivr.net/npm/daisyui@2.31.0/dist/full.css" rel="stylesheet" type="text/css">
  <script src="https://cdn.tailwindcss.com?plugins=forms,typography,aspect-ratio,line-clamp"></script>

  <script src="https://cdn.jsdelivr.net/npm/daisyui@2.31.0/dist/full.js"></script>

  <link rel="icon" type="image/x-icon" href="http://localhost:8000/favicon.ico">
  <script src="/PySocket.js"></script>
  <script src="/JsPyFunction.js"></script>
</head>
<body>
    <div class="d-flex flex-column w-full">
      <header class="bg-primary text-white">
        <h1>PyNexumJS</h1>
      </header>
  
      <main class="content">
        <div class="card">
          <h2>Call python function</h2>
  
          <h3>Behavior of python function</h3>
          The operation is the same for both "normal_call" and "exclusive_call".
  
          <ul>
            <li>Print entry message with call ID on the server console.</li>
            <li>async sleep for 10 second.</li>
            <li>Print exit message with call ID on the server console.</li>
          </ul>
  
          When "normal" calls, it immediately executes.
          <br>When "exclusive" calls, it will be accepted later
          if it is running in another process.
          <br>Press the button multiple times and look at the server console.
          <br>Notice the difference between "normal" and "exclusive".<br><br>
  
          <em>Next call ID: <span id="call_id">1</span></em><br>
          <button type="button" class="btn btn-primary" id="normal_call">Call normal</button><br>
          <button type="button" class="btn btn-outline" id="exclusive_call">Call exclusive</button>
        </div>
  
        <div class="card">
          <h2>Get function return from python</h2>
  
          <div class="mb-3">
            <label for="key_name">Key name of function:</label>
            <input type="text" value="" width="30" id="key_name" placeholder="py_sum"><br>
          </div>
  
          <div class="mb-3">
            <label for="args">List of variable length arguments(JSON):</label>
            <input type="text" value="" width="30" id="args" placeholder="[12, 10, 9]"><br>
          </div>
  
          <button type="button" class="btn btn-primary" id="command_run">Call</button><br><br>
          <span id="command_ack"></span>
        </div>
      </main>
  

  <script>
    let call_id = 1;
    let normal_id = document.querySelector("#call_id");
    let normal_call = document.querySelector("#normal_call");
    let exclusive_call = document.querySelector("#exclusive_call");

    normal_call.addEventListener("click", (event) => {
        JsPyFunction.call_nowait("py_normal")(call_id);
        normal_id.innerText = ++call_id;
    });
    exclusive_call.addEventListener("click", (event) => {
        JsPyFunction.call_nowait("py_exclusive")(call_id);
        normal_id.innerText = ++call_id;
    });

    let key_name = document.querySelector("#key_name");
    let args = document.querySelector("#args");
    let command_run = document.querySelector("#command_run");
    let command_ack = document.querySelector("#command_ack");

    command_run.addEventListener("click", async function (event){
        try{
            let params = JSON.parse(args.value);
            let val = await JsPyFunction.call(key_name.value, 20)(...params);
            command_ack.innerText = val;
        }
        catch(e){
            command_ack.innerText = e.message;
        }
    });

    // Callback function when websocket is closed
    function disable_button(){
        normal_call.disabled = true;
        exclusive_call.disabled = true;
        command_run.disabled = true;
    }
    // Register the callback function when websocket is closed
    JsPyTextSocket.add_close_event(disable_button);

    // Example: javascript exposed function
    function js_sum(a,b,c){
        if(a<0 || b<0 || c<0){
            throw new Error("Error: Nagative argument");
        }
        return(a+b+c);
    }
    // Expose for the server
    JsPyFunction.expose("js_sum", js_sum);
</script>
</body>
<footer class="bg-light text-dark">
    <p>Copyright &copy; 2023</p>
  </footer>
</html>
```

### main.py

```python

from pynexumjs import (
    PyNexumJS, 
    expose, 
    clear,
    call,
    call_nowait,
    callable,
    clear_all,
    clear_callback,
    exclusive_callable,
    WebSocketManager,
    is_running, 
    add_callback,
    get_keys,
    has, 
    remove,
    remove_all,
    JsPyError,
    BrowserModule,
    JsPyBinarySocket
    )
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json, asyncio





app = PyNexumJS()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@callable
async def py_normal(title: str):
    print(f'Enter py_normal: {title}')
    await asyncio.sleep(10)
    print(f'Exit  py_normal: {title}')
    return True

@exclusive_callable
async def py_exclusive(title: str):
    print(f'Enter py_exclusive: {title}')
    await asyncio.sleep(10)
    print(f'Exit  py_exclusive: {title}')
    return True

def positive_sum3(a: int, b: int, c: int=0):
    if a<0 or b<0 or c<0:
        raise Exception('Error: Negative argument')
    return a+b+c
expose('py_sum', positive_sum3)

@callable
async def reverse_call(name:str, key:str, args:list):
    if name == 'get_socket_id':
        # Get a tuple of currently connected socket ID.
        return WebSocketManager.get_socket_id()
    elif name == 'number_of_connections':
        # Get the number of currently connected sockets.
        return WebSocketManager.number_of_connections()
    elif name == 'set_connection_limit':
        # Set socket quantity limit.
        WebSocketManager.set_connection_limit(*args)
        return True
    elif name == 'clear':
        clear('py_normal')
        clear('py_exclusive')
        clear('py_sum')
        return True
    elif name == 'expose':
        expose('py_normal', py_normal)
        expose('py_exclusive', py_exclusive, True)
        expose('py_sum', positive_sum3)
        return True
    elif name == 'is_running':
        run1 = is_running('py_normal')
        run2 = is_running('py_exclusive')
        run3 = is_running('py_sum')
        return (f'py_normal: {run1}, py_exclusive: {run2}, '
                f'py_sum: {run3}')
    elif name == 'get_keys':
        all_names = get_keys()
        return all_names
    elif name == 'has':
        return has(*args)
    elif name == 'call_nowait':
        call_nowait(key)(*args)
        return True
    elif name == 'call':
        # timeout 25sec
        call_ack = await call(key, 25)(*args)
        return json.dumps(call_ack, cls=JsPyError.JSONEncoder)
    else:
        return False

def print_socket_event(id: int, event: str):
    """Print out socket open and close."""
    print(f'Socket {id}: {event}')
WebSocketManager.add_socket_event(print_socket_event)

@app.get('/call_nowait')
def page_call_nowait(request:Request):
    if 'key' in request.query_params and\
       'args' in request.query_params:
        key = request.query_params['key']
        param = json.loads(request.query_params['args'])
        call_nowait(key)(*param)
        return PlainTextResponse('OK')

@app.get('/call')
async def page_call(request:Request):
    if 'key' in request.query_params and\
       'args' in request.query_params:
        key = request.query_params['key']
        param = json.loads(request.query_params['args'])
        ret = await call(key)(*param)
        return PlainTextResponse(json.dumps(ret))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)
   
```
### In November 2023, PyNexumJS was just publicly released by software architecture Malek Ali at Yellow-SiC Group and is in alpha stage.
<p>Anyone can install and use Hybrid. There may be issues, but we are actively working to resolve them</p>


## 🤝 Contributing [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
