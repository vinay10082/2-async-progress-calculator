# Processing Progress Calculator

## Description
An asynchronous progress calculation engine designed to monitor large batches of non-blocking I/O operations.

## Architecture Overview
State machine tracking resolved versus pending `asyncio.Future` objects within the main event loop.

## Prerequisites
* Python 3.11+
* `pytest-asyncio` for test execution.

## Environment Variables
* `PROGRESS_POLLING_INTERVAL_MS` (default: `100`)

## Quick Start & Usage
Instantiate the tracker and bind it to a collection of active `asyncio.Task` instances for real-time percentage yield.

## Testing & CI
Run `pytest` with `--asyncio-mode=strict` to ensure isolated event loop testing for all coroutines.
