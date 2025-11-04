.PHONY: help install install-dev run run-enhanced test lint clean docker-build docker-run docker-stop

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8

run: ## Run the Flask application
	python app.py

run-enhanced: ## Run the enhanced Flask application
	python app_enhanced.py

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 . --exclude=venv,__pycache__,.git --max-line-length=120
	black . --check --exclude=venv

format: ## Format code with black
	black . --exclude=venv

clean: ## Clean up temporary files
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build

docker-build: ## Build Docker image
	docker build -t telnyx-patient-intake-agent:latest .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup: ## Initial setup (create .env, install dependencies)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your credentials."; \
	else \
		echo ".env file already exists."; \
	fi
	$(MAKE) install

dev-setup: ## Setup for development
	python -m venv venv
	@echo "Virtual environment created. Activate it with: source venv/bin/activate"
	@echo "Then run: make install-dev"

test-call: ## Make a test call (requires PHONE env var)
	@if [ -z "$(PHONE)" ]; then \
		echo "Usage: make test-call PHONE=+12025551234"; \
	else \
		python test_call.py call $(PHONE); \
	fi

cli-stats: ## Show CLI statistics
	python cli.py stats

cli-calls: ## List calls via CLI
	python cli.py call list

ngrok-start: ## Start ngrok tunnel
	python ngrok_helper.py

health-check: ## Check application health
	@curl -s http://localhost:5000/health | python -m json.tool || echo "Application not running"

db-init: ## Initialize database
	python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "This will delete all data. Press Ctrl+C to cancel, or Enter to continue..."
	@read confirm
	rm -f patient_intake.db
	$(MAKE) db-init
	@echo "Database reset complete"

backup-data: ## Backup data directory
	tar -czf backup_data_$(shell date +%Y%m%d_%H%M%S).tar.gz data/
	@echo "Backup created"

production-check: ## Check production readiness
	@echo "Checking production readiness..."
	@echo ""
	@echo "✓ Python version:" && python --version
	@echo "✓ Flask installed:" && python -c "import flask; print(flask.__version__)"
	@echo "✓ Telnyx SDK installed:" && python -c "import telnyx; print(telnyx.__version__)"
	@echo ""
	@echo "Environment variables:"
	@if [ -f .env ]; then \
		echo "✓ .env file exists"; \
		grep -q "TELNYX_API_KEY=" .env && echo "✓ TELNYX_API_KEY set" || echo "✗ TELNYX_API_KEY not set"; \
		grep -q "TELNYX_CONNECTION_ID=" .env && echo "✓ TELNYX_CONNECTION_ID set" || echo "✗ TELNYX_CONNECTION_ID not set"; \
		grep -q "TELNYX_PHONE_NUMBER=" .env && echo "✓ TELNYX_PHONE_NUMBER set" || echo "✗ TELNYX_PHONE_NUMBER not set"; \
	else \
		echo "✗ .env file not found"; \
	fi
	@echo ""
	@echo "For production deployment, also ensure:"
	@echo "  - HTTPS is enabled"
	@echo "  - Webhook signature verification is enabled"
	@echo "  - Database is PostgreSQL or MySQL"
	@echo "  - SECRET_KEY is set to a strong random value"
	@echo "  - Rate limiting is configured"
