.. note
   You should *NOT* add new change log entries to this file, this
   file is managed by towncrier. You *may* edit previous change logs to
   fix problems like typo corrections or such.

Changelog
=========

.. towncrier release notes start

pytest-pystack 1.0.2 (2024-11-16)
----------------------------------

Bug Fixes
~~~~~~~~~

- Disable pytest-pystack for tests depending on the ``pytester`` fixture.


pytest-pystack 1.0.1 (2023-08-21)
----------------------------------

Features
~~~~~~~~

- Add Python 3.12 support.

Bug Fixes
~~~~~~~~~

- Use ``pytest_sessionfinish`` instead of ``atexit`` to stop the monitor
  process. With Python 3.12, it is no longer possible to create a new thread
  in an ``atexit`` handler.
