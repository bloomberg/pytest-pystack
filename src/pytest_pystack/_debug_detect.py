import inspect  # used for introspection of module name
import multiprocessing
import sys

debug_detected = multiprocessing.Event()
# bdb covers pdb, ipdb, and possibly others
# pydevd covers PyCharm, VSCode, and possibly others
KNOWN_DEBUGGING_MODULES = {"pydevd", "bdb", "pydevd_frame_evaluator"}


# Replace settrace to record the tracefunc
original_settrace = sys.settrace


def fake_settrace(tracefunc):
    if tracefunc and is_debugging(tracefunc):
        debug_detected.set()
    original_settrace(tracefunc)


sys.settrace = fake_settrace


def is_debugging(tracefunc):
    """Detect if a debugging session is in progress.
    This looks at both pytest's builtin pdb support as well as
    externally installed debuggers using some heuristics.
    This is done by checking if the module that is the origin
    of the trace function is in KNOWN_DEBUGGING_MODULES.
    """
    global KNOWN_DEBUGGING_MODULES
    if tracefunc and inspect.getmodule(tracefunc):
        parts = inspect.getmodule(tracefunc).__name__.split(".")
        for name in KNOWN_DEBUGGING_MODULES:
            if any(part.startswith(name) for part in parts):
                return True
    return False
