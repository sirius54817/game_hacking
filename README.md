# game_hacking

A small collection of scripts and utilities used for analyzing and experimenting with game files, transfers, and secure storage. This repository contains helpers for file management, user utilities, network transfer tooling, and simple encryption helpers.

## Project layout

- `main.py` - small entrypoint (example runner).
- `models/` - application models and managers (e.g. `file_manager.py`, `user_manager.py`).
- `network/` - transfer and networking related utilities (e.g. `transfer_manager.py`).
- `secure_storage/` - encrypted blobs (do not commit secrets in plaintext).
- `utils/` - utility modules such as `encryption_utils.py`.

## Requirements

- Python 3.11+ recommended.

## Quick start

1. Create a virtual environment and install dependencies (if any):

	python -m venv .venv
	source .venv/bin/activate

2. Run the example entrypoint:

	python main.py

## Notes

- The `secure_storage` folder contains encrypted files. Treat them as sensitive.
- This repo is intended for learning and experimentation. Respect software licenses and game EULAs when using tools here.

If you'd like a richer README (badges, development workflow, tests), tell me what to include and I will expand it.
