# coding: utf-8
import asyncio
import queue
import typing

__all__ = ['register_function']

_func_queue = queue.Queue()

_startup_task = None

def register_function(func: typing.Callable,param: typing.Union[list, tuple, set]) -> None:
    global _func_queue
    _func_queue.put_nowait((func, param))

async def startup_handler() -> None:
    """Start a background process in event loop thread"""
    global _startup_task
    _startup_task = asyncio.create_task(_event_loop())

async def shutdown_handler() -> None:
    """Shutdown processing when the server is shutdown"""
    global _startup_task
    if _startup_task:
        _startup_task.cancel()
        _startup_task = None

async def _event_loop() -> None:
    """Background process in event loop thread"""
    global _func_queue
    while True:
        if not _func_queue.empty():
            reserve = _func_queue.get_nowait()
            try:
                if asyncio.iscoroutinefunction(reserve[0]):
                    await reserve[0](*reserve[1])
                else:
                    reserve[0](*reserve[1])
            except asyncio.CancelledError:
                break
            except:
                pass
        await asyncio.sleep(0)
