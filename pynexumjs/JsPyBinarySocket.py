# coding: utf-8
import typing
import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi import status
from . import JsPyBackground



class JsPyBinarySocket():
    SERIAL_MAX = 0xFFFFFFFF

    def __init__(self, url_path: str = '/jsmeetspy/binarysocket') -> None:
        self._url_path = url_path
        self._connected = 0
        self._connection_limit = 0
        self._socket_serial = 0
        self._socket_pool = {}
        self._socket_events = set()
        self._message_handler = lambda a, b, c: None

    def url_path(self) -> str:
        """Returns the websocket URL pathname"""
        return self._url_path

    # Not implemented
    # async def startup_handler(self) -> None
    # async def shutdown_handler(self) -> None

    def endpoint(self):
        """Return websocket endpoint"""
        return self.socket_handler

    def set_connection_limit(self, limit: int = 0) -> None:
        self._connection_limit = limit if limit >= 0 else 0

    def number_of_connections(self) -> int:
        return self._connected

    def get_socket_id(self) -> tuple:
        return tuple(self._socket_pool.keys())

    def close_socket(self, socket_id: int) -> bool:
        if socket_id in self._socket_pool:
            JsPyBackground.register_function(self._socket_pool[socket_id].close, [])
            return True
        else:
            return False

    def add_socket_event(self, func: typing.Callable) -> None:
        self._socket_events.add(func)

    def clear_socket_event(self) -> None:
        self._socket_events.clear()

    def set_message_handler(self, callback: typing.Callable) -> None:
        self._message_handler = callback

    def reservecast(
        self,
        data: bytes,
        socket: typing.Union[None, int, typing.List[int], typing.Tuple[int], typing.Set[int]] = None
    ) -> None:
        JsPyBackground.register_function(self.multicast, (data, socket))

    def broadcast(self, data: bytes) -> typing.Awaitable:
        cor_list = []
        for socket_id in self._socket_pool:
            cor_list.append(self._socket_pool[socket_id].send_bytes(data))
        return asyncio.gather(*cor_list, return_exceptions=True)

    def multicast(
        self,
        data: bytes,
        socket: typing.Union[None, int, typing.List[int], typing.Tuple[int], typing.Set[int]] = None
    ) -> typing.Awaitable:
        cor_list = []
        if socket is None:
            return self.broadcast(data)
        elif isinstance(socket, int):
            if socket in self._socket_pool:
                cor_list.append(self._socket_pool[socket].send_bytes(data))
        elif isinstance(socket, (tuple, list, set)):
            for i in socket:
                if i in self._socket_pool:
                    cor_list.append(self._socket_pool[i].send_bytes(data))
        return asyncio.gather(*cor_list, return_exceptions=True)

    def _append_socket(self, ws: WebSocket) -> int:
        self._socket_serial += 1
        if self._socket_serial > JsPyBinarySocket.SERIAL_MAX:
            self._socket_serial = 1
        while self._socket_serial in self._socket_pool:
            self._socket_serial += 1
            if self._socket_serial > JsPyBinarySocket.SERIAL_MAX:
                self._socket_serial = 1
        self._socket_pool[self._socket_serial] = ws
        return self._socket_serial

    def _delete_socket(self, socket_id: int) -> None:
        if socket_id in self._socket_pool:
            del self._socket_pool[socket_id]

    async def socket_handler(self, ws: WebSocket):
        self._connected += 1
        await ws.accept()
        _socket_id = self._append_socket(ws)
        if self._connection_limit > 0 and self._connected > self._connection_limit:
            await ws.close()
        else:
            for callback in self._socket_events:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(_socket_id, 'connect'))
                    else:
                        callback(_socket_id, 'connect')
                except:
                    pass
            try:
                while True:
                    message = await ws.receive_text()
                    try:
                        if not self._message_handler:
                            pass
                        elif asyncio.iscoroutinefunction(self._message_handler):
                            asyncio.create_task(self._message_handler(ws, _socket_id, message))
                        else:
                            self._message_handler(ws, _socket_id, message)
                    except:
                        pass
            except:
                pass
        self._delete_socket(_socket_id)
        self._connected -= 1
        for callback in self._socket_events:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(_socket_id, 'disconnect'))
                else:
                    callback(_socket_id, 'disconnect')
            except:
                pass



