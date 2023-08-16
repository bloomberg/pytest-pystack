import multiprocessing
import os
import shlex
import subprocess
import sys
from queue import Empty

from ._config import PystackConfig
from ._debug_detect import debug_detected

_queue = multiprocessing.Queue()
_process = None


def start(config):
    global _process
    _process = multiprocessing.Process(
        target=_run_monitor,
        args=(
            config,
            os.getpid(),
            _queue,
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


def _run_monitor(config: PystackConfig, pid, queue):
    pystack_cmd = [
        config.pystack_path,
        "remote",
    ]
    if config.pystack_args:
        pystack_cmd += shlex.split(config.pystack_args)
    handled_test_cases = set()
    while True:
        testcase = queue.get()
        if testcase is None:
            break

        if testcase in handled_test_cases:
            continue
        handled_test_cases.add(testcase)

        try:
            if queue.get(timeout=config.threshold) != testcase:
                raise Exception(
                    "new test should not start before previous test finished"
                )
        except Empty:
            output = ""
            output += f"\n\n**** PYSTACK  -- {testcase} ***\n"
            output += f"Timed out waiting for process {pid} to finish {testcase}:"
            proc = subprocess.run(
                [*pystack_cmd, str(pid)],
                stdout=subprocess.PIPE,
                text=True,
            )
            output += proc.stdout
            output += "**** PYSTACK  ***\n"
            is_debug = debug_detected.is_set()
            debug_detected.clear()
            if config.print_stderr and not is_debug:
                print(output, file=sys.__stderr__)
            if config.output_file:
                with open(config.output_file, "a") as f:
                    print(output, file=f)
