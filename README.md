<p align="center">
<img src="https://user-images.githubusercontent.com/11718525/226942590-de015c9a-4d5b-4960-9c42-8c1eac0845c1.png" width="70%">
</p>

# pytest-pystack

[![CI](https://github.com/bloomberg/pytest-pystack/actions/workflows/validate.yaml/badge.svg)](https://github.com/bloomberg/pytest-pystack/actions/workflows/validate.yaml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest-pystack)
![PyPI](https://img.shields.io/pypi/v/pytest-pystack)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-pystack)
![Code Style](https://img.shields.io/badge/code%20style-black,%20isort-000000.svg)

A pytest plug-in for easy integration of PyStack in your test suite.

It can be used to automatically dump the stack trace of a hanging test in your suite (with exception to test using `pytester` fixture).

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

# License

This project is Apache-2.0 licensed, as found in the [LICENSE](LICENSE.txt) file.

# Code of Conduct

- [Code of Conduct](https://github.com/bloomberg/.github/blob/main/CODE_OF_CONDUCT.md)

This project has adopted a Code of Conduct. If you have any concerns about the Code, or behavior
that you have experienced in the project, please contact us at opensource@bloomberg.net.

# Contributing

We welcome your contributions to help us improve and extend this project!

Below you will find some basic steps required to be able to contribute to the project. If you have
any questions about this process or any other aspect of contributing to a Bloomberg open source
project, feel free to send an email to opensource@bloomberg.net and we'll get your questions
answered as quickly as we can.

## Contribution Licensing

Since this project is distributed under the terms of an [open source license](LICENSE.txt),
contributions that you make are licensed under the same terms. For us to be able to accept your
contributions, we will need explicit confirmation from you that you are able and willing to provide
them under these terms, and the mechanism we use to do this is called a Developer's Certificate of
Origin [(DCO)](https://github.com/bloomberg/.github/blob/main/DCO.md). This is similar to the
process used by the Linux kernel, Samba, and many other major open source projects.

To participate under these terms, all that you must do is include a line like the following as the
last line of the commit message for each commit in your contribution:

```
Signed-Off-By: Random J. Developer <random@developer.example.org>
```

The simplest way to accomplish this is to add `-s` or `--signoff` to your `git commit` command.

You must use your real name (sorry, no pseudonyms, and no anonymous contributions).

## Steps

- Create an Issue, select 'Feature Request', and explain the proposed change.
- Follow the guidelines in the issue template presented to you.
- Submit the Issue.
- Submit a Pull Request and link it to the Issue by including "#<issue number>" in the Pull Request
  summary.
