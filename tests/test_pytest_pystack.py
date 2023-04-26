import subprocess
import sys
import textwrap

import pytest

SLEEPING_TEST_TEMPLATE = """
import time
def test_sleeping_test():
    print("start")
    time.sleep({sleep_seconds})
    print("finished")
"""

DEBUGGING_TEST = """
def test_debugging_test():
    print("start")
    breakpoint()
    print("finished")
"""

NON_DEBUGGING_TEST = """
import time
def test_non_debugging_test():
    print("start")
    time.sleep(5)
    print("finished")
"""

SKIPPED_TEST = """
import pytest
@pytest.mark.skip
def test_to_skip():
    pass
"""

ERROR_TEST = """
def test_error(doesnt_exist):
    pass
"""


def USER_INPUT_GENERATOR(nb_inputs=1):
    result = ["import time"]
    result += ["time.sleep(5)", "print('continue')"] * nb_inputs
    return "\n".join(result)


TEST_FAILING_AFTER_TIMEOUT = """
import time
def test_failing_after_timeout():
    time.sleep(5)
    assert False
"""

TEST_FAILING_BEFORE_TIMEOUT = """
import time
def test_failing_before_timeout():
    assert False
    time.sleep(5)
"""

SLEEPING_TEST_1S = SLEEPING_TEST_TEMPLATE.format(sleep_seconds=1)
SLEEPING_TEST_5S = SLEEPING_TEST_TEMPLATE.format(sleep_seconds=5)

USER_INPUT_GENERATOR_1 = USER_INPUT_GENERATOR(nb_inputs=1)
USER_INPUT_GENERATOR_2 = USER_INPUT_GENERATOR(nb_inputs=2)


def test_default_pystack_options(testdir, monkeypatch, capfd):
    monkeypatch.chdir(testdir.tmpdir)
    testdir.makepyfile(SLEEPING_TEST_5S)

    testdir.runpytest("--pystack-threshold=1", "-s")

    # Outputs to stderr
    _, stderr = capfd.readouterr()
    assert "PYSTACK  -- test_sleeping_test" in stderr
    assert "time.sleep(5)" in stderr


def serialize_config(pystack_config):
    return textwrap.dedent(
        f"""
        [tool.pytest.ini_options]
        {pystack_config}
    """
    )


def test_silent_when_debugging_by_default(testdir, monkeypatch):
    monkeypatch.chdir(testdir.tmpdir)
    testdir.makepyfile(DEBUGGING_TEST)

    # Simulating user interaction taking a long time
    user_process = subprocess.Popen(
        [sys.executable, "-c", USER_INPUT_GENERATOR_1],
        stdout=subprocess.PIPE,
        text=True,
    )
    pytest_process = subprocess.Popen(
        ["pytest", "--pystack-threshold=1", "-s"],
        stdin=user_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    user_process.wait()
    pytest_process.wait()
    stderr = pytest_process.stderr.read()

    # Does *NOT* output to stderr
    assert not stderr


def test_silent_only_in_debugging_tests(testdir, monkeypatch):
    monkeypatch.chdir(testdir.tmpdir)

    # The order is important here: test_debugging should be first and
    # test_non_debugging should be second, so that we test that the debugging
    # test didn't suppress the output of the second test.
    testdir.makepyfile(
        test_debugging=DEBUGGING_TEST,
        test_non_debugging=NON_DEBUGGING_TEST,
    )

    # Simulating user interaction taking a long time
    user_process = subprocess.Popen(
        [sys.executable, "-c", USER_INPUT_GENERATOR_1],
        stdout=subprocess.PIPE,
        text=True,
    )
    pytest_process = subprocess.Popen(
        ["pytest", "--pystack-threshold=1", "-s"],
        stdin=user_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    user_process.wait()
    pytest_process.wait()
    stderr = pytest_process.stderr.read()

    # Only the non debugging test should have a pystack output
    assert "PYSTACK  -- test_debugging_test" not in stderr
    assert "PYSTACK  -- test_non_debugging_test" in stderr
    assert stderr.count("time.sleep(5)") == 1


def test_silent_in_debugged_tests_failing_before_timeout(testdir, monkeypatch):
    monkeypatch.chdir(testdir.tmpdir)

    # TODO is the order important here?
    testdir.makepyfile(TEST_FAILING_BEFORE_TIMEOUT + TEST_FAILING_AFTER_TIMEOUT)

    # Simulating user interaction taking a long time
    user_process = subprocess.Popen(
        [sys.executable, "-c", USER_INPUT_GENERATOR_2],
        stdout=subprocess.PIPE,
        text=True,
    )
    pytest_process = subprocess.Popen(
        ["pytest", "--pystack-threshold=1", "--pdb", "-s"],
        stdin=user_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    user_process.wait()
    pytest_process.wait()
    stderr = pytest_process.stderr.read()

    # Only the non debugging test should have a pystack output
    assert "PYSTACK  -- test_failing_before_timeout" not in stderr
    assert "PYSTACK  -- test_failing_after_timeout" in stderr
    assert stderr.count("time.sleep(5)") == 1


@pytest.mark.parametrize(
    ["pytestarg", "pytestconfig"],
    [
        ("--pystack-threshold=1", ""),  # configured in CLI
        ("", "pystack_threshold=1"),  # configured in config file
        ("--pystack-threshold=1", "pystack_threshold=10"),  # CLI takes preference
    ],
)
@pytest.mark.parametrize(
    "pystack_is_triggered", [True, False], ids=["Triggered", "Not triggered"]
)
def test_threshold_option(
    testdir, monkeypatch, capfd, pytestarg, pytestconfig, pystack_is_triggered
):
    monkeypatch.chdir(testdir.tmpdir)
    test_file = SLEEPING_TEST_5S if pystack_is_triggered else SLEEPING_TEST_1S
    testdir.makepyfile(test_file)

    config_file = testdir.makepyprojecttoml(serialize_config(pytestconfig))
    testdir.runpytest(pytestarg, "-s", f"-c={config_file}")

    # Outputs to stderr
    _, stderr = capfd.readouterr()
    if pystack_is_triggered:
        assert "PYSTACK  -- test_sleeping_test" in stderr
        assert "time.sleep(5)" in stderr
    else:
        assert not stderr


@pytest.mark.parametrize(
    ["pytestarg", "pytestconfig"],
    [
        ("--pystack-output-file=./pystack_output.log", ""),  # configured in CLI
        ("", "pystack_output_file='./pystack_output.log'"),  # configured in config file
    ],
)
def test_output_file_option(testdir, monkeypatch, pytestarg, pytestconfig):
    monkeypatch.chdir(testdir.tmpdir)
    testdir.makepyfile(SLEEPING_TEST_5S)

    config_file = testdir.makepyprojecttoml(serialize_config(pytestconfig))
    testdir.runpytest("--pystack-threshold=1", pytestarg, "-s", f"-c={config_file}")

    # Outputs to stderr
    with open("./pystack_output.log") as f:
        file_content = f.read()
    assert "PYSTACK  -- test_sleeping_test" in file_content
    assert "time.sleep(5)" in file_content


@pytest.mark.parametrize(
    ["pytestarg", "pytestconfig"],
    [
        ("--pystack-args='--native'", ""),  # configured in CLI
        ("", "pystack_args='--native'"),  # configured in config file
    ],
)
def test_pystack_args(testdir, monkeypatch, pytestarg, pytestconfig, capfd):
    monkeypatch.chdir(testdir.tmpdir)
    testdir.makepyfile(SLEEPING_TEST_5S)

    config_file = testdir.makepyprojecttoml(serialize_config(pytestconfig))
    testdir.runpytest("--pystack-threshold=1", pytestarg, "-s", f"-c={config_file}")

    # Outputs to stderr
    _, stderr = capfd.readouterr()
    assert "PYSTACK  -- test_sleeping_test" in stderr
    assert "(C) File " in stderr
    assert "time.sleep(5)" in stderr


@pytest.mark.parametrize("test_code", [SKIPPED_TEST, ERROR_TEST])
def test_both_setup_and_teardown_called_for_all_tests(testdir, monkeypatch, test_code):
    # GIVEN
    monkeypatch.chdir(testdir.tmpdir)
    testdir.makepyfile(test_code)

    # WHEN
    pytest_process = subprocess.Popen(
        ["pytest", "--pystack-threshold=1", "-s"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    pytest_process.wait()
    stderr = pytest_process.stderr.read()

    # THEN
    assert not stderr


def test_parallel_threads_pytestxdist(testdir, monkeypatch, capfd):
    monkeypatch.chdir(testdir.tmpdir)
    testdir.makepyfile(
        SLEEPING_TEST_5S + TEST_FAILING_AFTER_TIMEOUT + NON_DEBUGGING_TEST
    )

    testdir.runpytest("--pystack-threshold=1", "-s", "-n=3")

    # Outputs to stderr
    _, stderr = capfd.readouterr()

    assert "PYSTACK  -- test_sleeping_test" in stderr
    assert "PYSTACK  -- test_failing_after_timeout" in stderr
    assert "PYSTACK  -- test_non_debugging_test" in stderr
    assert "time.sleep(5)" in stderr


def test_two_slow_tests_in_a_suite_prints_both(testdir, monkeypatch, capfd):
    monkeypatch.chdir(testdir.tmpdir)

    test_case = f"""
{SLEEPING_TEST_5S}

{SLEEPING_TEST_5S.replace('test_sleeping_test', 'test_sleeping_test2')}
"""

    testdir.makepyfile(test_case)

    testdir.runpytest("--pystack-threshold=1", "-s")

    # Outputs to stderr
    _, stderr = capfd.readouterr()
    print(stderr)
    assert "PYSTACK  -- test_sleeping_test" in stderr
    assert "PYSTACK  -- test_sleeping_test2" in stderr
