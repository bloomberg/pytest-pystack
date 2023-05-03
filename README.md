<p align="center">
<img src="https://user-images.githubusercontent.com/11718525/226942590-de015c9a-4d5b-4960-9c42-8c1eac0845c1.png" width="70%">
</p>

# pytest-pystack

A pytest plug-in for easy integration of PyStack in your test suite.

It can be used to automatically dump the stack trace of a hanging test in your suite.

See [PyStack](https://github.com/bloomberg/pystack) for further information about the tool.

## Installation

To install the PyStack pytest plug-in, just run the following command in your venv:

`python -m pip install pytest-pystack`

## Quick Start

After you have installed the pytest plug-in, you can have PyStack monitor your test suite and output a stack trace if a test takes more than 5
seconds, simply by running pytest with argument `--pystack-threshold=5`.

## Configuration

The PyStack plug-in can be configured via the command line with the following options:

-   `--pystack-threshold`: Enables the plug-in and monitors all tests,
    generating a stack trace if they take longer than the specified
    threshold. Note, this neither stops nor fails the test case after the specified threshold.
-   `--pystack-output-file`: Appends PyStack output to a file.
-   `--pystack-path`: Path to the `pystack` executable.
-   `--pystack-args`: Additional args to pass to `pystack remote <pid>`,
    like `--native` or `--native-all`.

And through any pytest config file, see an example of `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pystack_threshold=60
pystack_path="custom-version-of-pystack"
pystack_output_file="./pystack.log"
pystack_args="--native"
```
