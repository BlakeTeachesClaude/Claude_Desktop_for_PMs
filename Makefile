ifeq ($(OS),Windows_NT)
PYTHON ?= python
else
PYTHON ?= python3
endif
.PHONY: sync sample
sync:
	$(PYTHON) scripts/sync.py
sample:
	$(PYTHON) scripts/sync.py --sample
