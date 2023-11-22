from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
import typing
from . import JsPyBackground
from starlette.endpoints import WebSocketEndpoint




class JsPyError(Exception):
    def __init__(self, msg: str, protocol: str,key: str, id: int, socket_id: int):
        self._protocol = protocol
        self._key = key
        self._id = id
        self._socket_id = socket_id
        self._msg = msg
        super().__init__(self.report())

    def __repr__(self):
        return self._msg

    def message(self) -> str:
        """Explanation of the cause of the exception"""
        return self._msg

    def report(self) -> str:
        """Detailed explanation of the cause of the exception """
        return(self._msg+' in {protocol: '+self._protocol+', key: '+self._key+
               ', id: '+str(self._id)+', socket_id: '+str(self._socket_id)+'}')

    def get_socket_id(self) -> int:
        """Get socket ID of the place where the exception occurred

        Returns
        ----------
        int
            This is the socket ID that has propagated the exception.
            The socket ID is a unique number that is assigned to the client
            by the server when websocket communication is established.
            This is an identification number uniquely assigned to the
            connected client. Assigned from 1 in connection order.
            Socket ID 0 means server.
        """
        return self._socket_id

    class JSONEncoder(json.JSONEncoder):
        """JSON encoder for exception instances

        When JsPyError() instance or Exception() instance is JSON encoded,
        it is replaced with a character string.

        Examples
        ----------
        import json
        from JsMeetsStarlette import JsPyError

        json_str = json.dumps(some_obj, cls=JsPyError.JSONEncoder)
        """
        def default(self, obj):
            if isinstance(obj, JsPyError):
                return '<'+obj.__class__.__name__+'>: '+obj.report()
            elif isinstance(obj, Exception):
                return '<'+obj.__class__.__name__+'>: '+str(obj.args)
            else:
                return json.JSONEncoder.default(self, obj)
            



class WebSocketManager(WebSocketEndpoint):
    _SOCKET_PATH = '/jsmeetspy/textsocket'
    _socket_serial = 0 
    SERIAL_MAX = 0XFFFFFFFF
    _protocol_table = {}
    _socket_pool ={}
    _connected = 0             
    _connection_limit = 0        
    _socket_events = set()

    @classmethod
    def url_path(cls) -> str:
        """Returns the websocket URL pathname"""
        return cls._SOCKET_PATH

    # Not implemented
    # async def startup_handler(self) -> None
    # async def shutdown_handler(self) -> None

    @classmethod
    def endpoint(cls):
        """Return websocket endpoint"""
        return cls
    def set_connection_limit(self, limit: int=0) -> None:
        self._connection_limit = limit if limit >= 0 else 0

    def number_of_connections(self) -> int:
        """Get the number of currently connected sockets."""
        return self._connected
    
    @classmethod
    def get_socket_id(cls) -> tuple:
        return tuple(cls._socket_pool.keys())
    

    
    @classmethod
    def close_socket(cls, socket_id: int) -> bool:
        if socket_id in cls._socket_pool:
            JsPyBackground.register_function(
                cls._socket_pool[socket_id].close, [])
            # on_disconnect() is called immediately by close()
            return(True)
        else:
            return(False)

    @classmethod
    def add_protocol(cls, protocol: str, func: typing.Callable) -> None:
      cls._protocol_table[protocol] = func

    @classmethod
    def add_socket_event(cls, func: typing.Callable) -> None:
        cls._socket_events.add(func)

    @classmethod
    def clear_socket_event(cls) -> None:
        cls._socket_events.clear()

    @classmethod
    def reservecast(cls, data, socket: typing.Union[
                    None, int, typing.List[int],
                    typing.Tuple[int], typing.Set[int]]=None) -> None:
        JsPyBackground.register_function(cls.multicast, (data, socket))

    @classmethod
    def broadcast(cls, data) -> typing.Awaitable:
        text_data = json.dumps(data)
        cor_list = []
        for socket_id in cls._socket_pool:
            cor_list.append(cls._socket_pool[socket_id].send_text(text_data))
        return asyncio.gather(*cor_list, return_exceptions=True)

    @classmethod
    def multicast(cls, data, socket: typing.Union[None, int, typing.List[int],typing.Tuple[int], typing.Set[int]]=None) -> typing.Awaitable:
        cor_list = []
        text_data = json.dumps(data)
        if socket is None:
            return cls.broadcast(data)
        elif isinstance(socket, int):
            if socket in cls._socket_pool:
                cor_list.append(cls._socket_pool[socket].send_text(text_data))
        elif isinstance(socket, (tuple, list, set)):
            for i in socket:
                if i in cls._socket_pool:
                    cor_list.append(
                        cls._socket_pool[i].send_text(text_data))
        return asyncio.gather(*cor_list, return_exceptions=True)

    @classmethod
    def _append_socket(cls, ws: WebSocket) -> int:
        cls._socket_serial += 1
        if cls._socket_serial > cls.SERIAL_MAX:
            cls._socket_serial = 1
        while cls._socket_serial in cls._socket_pool:
            cls._socket_serial += 1
            if cls._socket_serial > cls.SERIAL_MAX:
                cls._socket_serial = 1
        cls._socket_pool[cls._socket_serial] = ws
        return cls._socket_serial
    


    @classmethod
    def _delete_socket(cls, socket_id: int) -> None:
        if socket_id in cls._socket_pool:
            del cls._socket_pool[socket_id]




    async def on_connect(self, ws: WebSocket):
        self._connected += 1
        await ws.accept()
        self._socket_id = self._append_socket(ws)
        if self._connection_limit > 0 and\
           self._connected > self._connection_limit:
            send_dict = {'protocol': 'system', 'key': 'connect', 'id': 0,
                         'data': None, 'exception':
                         'Connection refused due to connection limit @python'}
            await ws.send_json(send_dict)
            await ws.close()
            # on_disconnect() is called immediately by ws.close().
        else:
            send_dict = {'protocol': 'system', 'key': 'connect', 'id': 0,
                         'data': self._socket_id, 'exception': None}
            await ws.send_json(send_dict)
        for callback in self._socket_events:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(self._socket_id, 'connect'))
                else:
                    callback(self._socket_id, 'connect')
            except:
                pass


    async def on_receive(self, ws: WebSocket, data: str):
        """Processing when data is received"""
        try:
            dict_data = json.loads(data)
            
            if('protocol' in dict_data and 'key' in dict_data and
               'id' in dict_data and 'data' in dict_data and
               'exception' in dict_data):
                call_func = self._protocol_table[dict_data['protocol']]
                if(asyncio.iscoroutinefunction(call_func)):
                    asyncio.create_task(call_func(ws, self._socket_id, dict_data))
                else:
                    print(dict_data)
                    call_func(ws, self._socket_id, dict_data)
        except:
            pass

    async def on_disconnect(self, ws: WebSocket, close_code: int):
        """Processing when websocket is disconnected"""
        self._delete_socket(self._socket_id)
        self._connected -= 1
        for callback in self._socket_events:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(self._socket_id, 'disconnect'))
                else:
                    callback(self._socket_id, 'disconnect')
            except:
                pass



#socket_mennager = WebSocketManager()














