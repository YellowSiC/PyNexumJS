from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from .socket_mennager import WebSocketManager
from . import JsPyBackground
from starlette.types import Scope, Receive, Send
import json



class PyNexumJS(FastAPI):
    def __init__(self,logo_path='default', *args, **kwargs):

        if 'extended_sockets' in kwargs:
            extended_sockets = kwargs['extended_sockets']
            if not extended_sockets:
                extended_sockets = []
            del kwargs['extended_sockets']
        else:
            extended_sockets = [WebSocketManager]
        self.logo_path = logo_path
        super().__init__(*args, **kwargs)
        for i in extended_sockets:
            self.add_socket(i)
        self.add_middleware(CORSMiddleware, allow_origins=["*"])
        # Register routes
        self.add_api_routes()
        # Register event handlers
        self.add_event_handler('startup', JsPyBackground.startup_handler)
        self.add_event_handler('shutdown', JsPyBackground.shutdown_handler)

    def get_js_file(self, js_filename: str):
        folder_path = Path(__file__).parent / 'js'
        files = list(folder_path.rglob(js_filename))

        if files:
            file_path = files[0]
            return FileResponse(path=file_path, media_type='text/javascript')
        else:
            print(f'Die Datei {js_filename} wurde nicht gefunden.')
            return {"error": f"Datei {js_filename} nicht gefunden"}

    def add_api_routes(self):
        self.add_api_route("/PySocket.js", endpoint=self.get_sic_socket_js)
        self.add_api_route("/JsPyBinarySocket.js", endpoint=self.get_binary_socket_js)
        self.add_api_route("/JsPyFunction.js", endpoint=self.get_function_js)
        self.add_api_route("/JsPyPubsub.js", endpoint=self.get_pubsub_js)
        self.add_api_route("/JsPyQueue.js", endpoint=self.get_queue_js)
        self.add_api_route("/RingArray.js", endpoint=self.get_ring_array_js)
        self.add_api_route("/RingTypedArray.js", endpoint=self.get_ring_typed_array_js)
        self.add_api_route("/favicon.ico", endpoint=self.getapplogo)

    def add_socket(self, endpoint) -> None:
        self.add_websocket_route(endpoint.url_path(), endpoint.endpoint())
        if hasattr(endpoint, 'startup_handler'):
            self.add_event_handler('startup', endpoint.startup_handler)
        if hasattr(endpoint, 'shutdown_handler'):
            self.add_event_handler('shutdown', endpoint.shutdown_handler)

    async def get_sic_socket_js(self):
        return self.get_js_file("PySocket.js")

    async def get_binary_socket_js(self):
        return self.get_js_file("JsPyBinarySocket.js")

    async def getapplogo(self):
        if self.logo_path == 'default':
            return self.get_js_file("logo.png")
        else:
            self.get_js_file(self.logo_path)
    
    async def get_function_js(self):
        return self.get_js_file("JsPyFunction.js")

    async def get_pubsub_js(self):
        return self.get_js_file("JsPyPubsub.js")

    async def get_queue_js(self):
        return self.get_js_file("JsPyQueue.js")

    async def get_ring_array_js(self):
        return self.get_js_file("RingArray.js")

    async def get_ring_typed_array_js(self):
        return self.get_js_file("RingTypedArray.js")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.root_path:
            scope["root_path"] = self.root_path
        await super().__call__(scope, receive, send)
        #homeDir = pathlib.Path(__main__.__file__).resolve().parent











