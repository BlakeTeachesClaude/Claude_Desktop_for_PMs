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
.PHONY: test smoke
test:
	$(PYTHON) -m pytest -q
smoke:
	$(PYTHON) scripts/smoke.py

# Your own targets live in my.mk (git-ignored); see guided-build.md
-include my.mk
