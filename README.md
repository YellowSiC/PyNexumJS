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

@app.route('/call_nowait', ['GET'])
def page_call_nowait(request):
    if 'key' in request.query_params and\
       'args' in request.query_params:
        key = request.query_params['key']
        param = json.loads(request.query_params['args'])
        call_nowait(key)(*param)
        return PlainTextResponse('OK')

@app.route('/call', ['GET'])
async def page_call(request):
    if 'key' in request.query_params and\
       'args' in request.query_params:
        key = request.query_params['key']
        param = json.loads(request.query_params['args'])
        ret = await call(key)(*param)
        return PlainTextResponse(json.dumps(ret))
   
```
### In November 2023, PyNexumJS was just publicly released by software architecture Malek Ali at Yellow-SiC Group and is in alpha stage.
<p>Anyone can install and use Hybrid. There may be issues, but we are actively working to resolve them</p>


## 🤝 Contributing [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
