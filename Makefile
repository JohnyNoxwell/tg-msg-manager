PYTHON ?= python3
RUFF ?= ruff

.PHONY: lint format format-check test verify

lint:
	$(PYTHON) -m compileall tg_msg_manager tests
	$(RUFF) check tg_msg_manager tests

format:
	$(RUFF) format tg_msg_manager tests

format-check:
	$(RUFF) format --check tg_msg_manager tests

test:
	$(PYTHON) -m unittest discover -s tests -q

verify:
	$(MAKE) lint
	$(MAKE) format-check
	$(MAKE) test
