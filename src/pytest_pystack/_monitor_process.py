import os

from ._debug_detect import debug_detected
from ._monitor import monitor
from ._multiprocessing_context import MP_CTX

_queue = MP_CTX.Queue()
_process = None


def start(config):
    global _process
    _process = MP_CTX.Process(
        target=monitor,
        args=(
            config,
            os.getpid(),
            _queue,
            debug_detected,
        ),
        name="pystack_monitor",
    )
    _process.start()
    return _queue


def stop():
    if _process:
        _queue.put_nowait(None)
        _process.join(timeout=5)
        if _process.is_alive():
            _process.kill()
