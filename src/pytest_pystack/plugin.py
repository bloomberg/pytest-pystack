import pytest

from . import _config
from . import _monitor_process
from ._debug_detect import debug_detected


@pytest.hookimpl
def pytest_enter_pdb():  # This needs to be in the plugin.py file to work
    """Prevents running pystack when we entered pdb.

    This disables the plugin logic when pytest's builtin pdb
    support notices we entered pdb.
    """
    # Since pdb.set_trace happens outside of any pytest control, we don't have
    # any pytest ``item`` here, so we cannot use timeout_teardown. Thus, we
    # need another way to signify that pystack should not be run.
    debug_detected.set()


def pytest_addoption(parser) -> None:
    group = parser.getgroup("pystack")
    threshold_help = "Generate a pystack report after a threshold in seconds."
    group.addoption(
        "--pystack-threshold",
        type=float,
        required=False,
        help=threshold_help,
    )
    parser.addini("pystack_threshold", threshold_help)

    output_file_help = "Output file. Results will be appended."
    group.addoption(
        "--pystack-output-file",
        type=str,
        required=False,
        help=output_file_help,
    )
    parser.addini("pystack_output_file", output_file_help)

    pystack_path_help = "Path to the pystack executable."
    group.addoption(
        "--pystack-path",
        type=str,
        required=False,
        default="pystack",
        help=pystack_path_help,
    )
    parser.addini("pystack_path", pystack_path_help)

    pystack_args_help = (
        "String with additional args to pass to 'pystack remote'. E.g: '--native'."
    )
    group.addoption(
        "--pystack-args",
        type=str,
        required=False,
        help=pystack_args_help,
    )
    parser.addini("pystack_args", pystack_args_help)


@pytest.hookimpl
def pytest_runtest_makereport(item, call):
    if call.when in {"setup", "teardown"} and item.config._pystack_queue:
        item.config._pystack_queue.put(item.name)


def _get_cli_or_file_value(pytest_config, key):
    ret = pytest_config.getoption(key)
    if ret is not None:
        return ret
    return pytest_config.getini(key)


@pytest.hookimpl
def pytest_configure(config) -> None:
    config._pystack_queue = None
    config._pystack_config = None
    threshold = _get_cli_or_file_value(config, "pystack_threshold")
    if not threshold:
        return  # not configured

    output_file = _get_cli_or_file_value(config, "pystack_output_file")
    pystack_args = _get_cli_or_file_value(config, "pystack_args")
    pystack_path = _get_cli_or_file_value(config, "pystack_path")

    pystack_config = _config.PystackConfig(
        threshold=float(threshold),
        output_file=output_file or None,
        pystack_path=pystack_path,
        pystack_args=pystack_args or None,
        print_stderr=True,
    )
    config._pystack_queue = _monitor_process.start(pystack_config)
