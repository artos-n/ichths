.PHONY: run dev clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

run: ## Run Perf Tool (desktop)
	python main.py

dev: ## Run with verbose output
	python main.py --refresh 500

compact: ## Run in compact mode
	python main.py --compact

lint: ## Check syntax
	python -m py_compile main.py
	python -m py_compile monitor.py
	python -m py_compile overlay.py
	python -m py_compile widgets.py
	python -m py_compile config.py
	@echo "✅ All files compile cleanly"

clean: ## Remove build artifacts
	rm -rf __pycache__ */__pycache__
	rm -rf .buildozer android/.buildozer android/bin
	rm -rf dist build *.egg-info

android: ## Build Android APK (requires buildozer)
	cd android && buildozer android debug

install: ## Install dependencies
	pip install -r requirements.txt
