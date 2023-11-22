# coding: utf-8
import typing
import asyncio
import json
import queue
from starlette.websockets import WebSocket
from .socket_mennager import WebSocketManager, JsPyError




_exposed_function = {}
_call_id = 0
_CALL_ID_MAX = 0XFFFFFFFF
_call_memory = {}

__all__ = [
    'expose', 
    'callable', 
    'exclusive_callable', 
    'clear',
    'is_running', 
    'get_keys', 
    'has', 
    'call_nowait', 
    'call'
]




def expose(key: str, func: typing.Callable, exclusive: bool=False) -> bool:
    global _exposed_function

    if (key in _exposed_function) and _exposed_function[key][2]:
        return False
    _exposed_function[key] = [func,asyncio.iscoroutinefunction(func),False,queue.Queue() if exclusive else None]
    return True





def callable(func: typing.Callable) -> typing.Callable:
    global _exposed_function

    if func.__name__ not in _exposed_function:
        _exposed_function[func.__name__] = [func,asyncio.iscoroutinefunction(func),False,None]
        return func
    else:
        raise KeyError('The exposed function "{}" is invalid @python'.format(
            func.__name__))






def exclusive_callable(func: typing.Callable) -> typing.Callable:
    global _exposed_function

    if func.__name__ not in _exposed_function:
        _exposed_function[func.__name__] = [func,asyncio.iscoroutinefunction(func),False,queue.Queue()]
        return func
    else:
        raise KeyError('The exposed function "{}" is invalid @python'.format(
            func.__name__))






def clear(key: str) -> bool:
    global _exposed_function
    if (key in _exposed_function) and (not _exposed_function[key][2]):
        del _exposed_function[key]
        return True
    else:
        return False






def is_running(key: str) -> bool:
    global _exposed_function

    if key in _exposed_function:
        return _exposed_function[key][2]
    else:
        return False
    



def get_keys() -> typing.List[str]:
    global _exposed_function

    return list(_exposed_function.keys())





def has(key: str) -> bool:
    global _exposed_function

    return(key in _exposed_function)





def call_nowait(key: str,target: typing.Union[int,typing.List[int],typing.Tuple[int],typing.Set[int],None]=None) -> typing.Callable:
    def inner_nowait(*args) -> None:
        global _call_id, _CALL_ID_MAX
        nonlocal key, target
        _call_id += 1
        if _call_id > _CALL_ID_MAX:
            _call_id = 1
        this_id = _call_id
        send_dic = {'protocol': 'function', 'key': key,'id': this_id, 'data': args, 'exception': None}
        WebSocketManager.reservecast(send_dic, target)
    return inner_nowait






def call(key: str,timeout: typing.Union[int, float, None]=0,target: typing.Union[int,typing.List[int],typing.Tuple[int],typing.Set[int],None]=None) -> typing.Callable:
    async def inner(*args) -> dict:
        global _call_id, _call_memory, _CALL_ID_MAX
        nonlocal key, timeout, target

        _call_id += 1
        if _call_id > _CALL_ID_MAX:
            _call_id = 1
        this_id = _call_id

        target_sockets = []
        if target is None:
            target_sockets = WebSocketManager.get_socket_id()
        elif isinstance(target, int):
            all_sockets = WebSocketManager.get_socket_id()
            if target in all_sockets:
                target_sockets = [target]
        elif isinstance(target, (tuple, list, set)):
            all_sockets = WebSocketManager.get_socket_id()
            target_sockets = [i for i in target if (i in all_sockets)]
        if len(target_sockets) == 0:
            return {}
        send_dic = {'protocol': 'function_call', 'key': key,'id': this_id, 'data': args, 'exception': None}
        this_loop = asyncio.get_running_loop()
        this_futures = [this_loop.create_future() for i in target_sockets]
        _call_memory[this_id] = this_futures
        WebSocketManager.multicast(send_dic, target_sockets)
        if (timeout is not None) and (timeout <= 0):
            timeout = None
        done, pending = await asyncio.wait(this_futures, timeout=timeout)
        return_value = {}
        for ft in done:
            try:
                value = ft.result()
                return_value[value[0]] = value[1]
            except JsPyError as e:
                return_value[e.get_socket_id()] = e
        del _call_memory[this_id]
        return return_value
    return inner










def _return_from_js(ws: WebSocket, socket_id: int, dict_data: dict) -> None:
    global _call_memory

    protocol = dict_data.get('protocol')
    key = dict_data.get('key')
    id = dict_data.get('id')
    data = dict_data.get('data')
    excpt = dict_data.get('exception')
    if isinstance(id, int) and (id in _call_memory):
        for ft in _call_memory[id]:
            if ft.done():
                continue
            else:
                if excpt is not None:
                    ft.set_exception(JsPyError(excpt, protocol, key, id, socket_id))
                else:
                    ft.set_result((socket_id, data))
                break
    # else: ignore







async def _call_from_js(ws: WebSocket, socket_id: int, dict_data: dict) -> None:
    global _exposed_function

    protocol = dict_data.get('protocol')
    key = dict_data.get('key')
    id = dict_data.get('id')
    send_dic = {'protocol': 'function_return', 'key': key, 'id': id,'data': None, 'exception': None}
    if (not isinstance(key, str)) or (key not in _exposed_function):
        send_dic['data'] = None
        send_dic['exception'] = 'Function key name is not registered @python'
    else:
        func = _exposed_function[key][0]
        iscoroutine = _exposed_function[key][1]
        isrunning = _exposed_function[key][2]
        exclusive = _exposed_function[key][3]
        if exclusive and isrunning:
            this_loop = asyncio.get_running_loop()
            this_future = this_loop.create_future()
            exclusive.put_nowait(this_future)
            await this_future

        _exposed_function[key][2] = True    # function running
        await asyncio.sleep(0)
        if iscoroutine:
            try:
                send_dic['data'] = await func(*dict_data.get('data'))
            except Exception as e:
                send_dic['data'] = None
                send_dic['exception'] = str(e) + ' @python'
        else:
            try:
                send_dic['data'] = func(*dict_data.get('data'))
            except Exception as e:
                send_dic['data'] = None
                send_dic['exception'] = str(e) + ' @python'
        await asyncio.sleep(0)
        _exposed_function[key][2] = False   # function not running
        if exclusive and (not exclusive.empty()):
            exclusive.get_nowait().set_result(True)
            _exposed_function[key][2] = True    # soon running
    if protocol == 'function_call':
        try:
            send_text = json.dumps(send_dic)
        except Exception as e:
            send_dic['exception'] = str(e) + ' @python'
            send_dic['data'] = None
            send_text = json.dumps(send_dic)
        await ws.send_text(send_text)








WebSocketManager.add_protocol('function_return', _return_from_js)
WebSocketManager.add_protocol('function_call', _call_from_js)
WebSocketManager.add_protocol('function', _call_from_js)
