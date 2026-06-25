.PHONY: dev prod migrate test lint loadtest smoke deploy

# --- Local Development ---
dev:
	@echo "Starting local development environment..."
	docker-compose -f infrastructure/docker-compose.yml up --build

# --- Production Deployment ---
prod:
	@echo "Starting production environment..."
	docker-compose -f infrastructure/docker-compose.prod.yml up -d --build

# --- Database ---
migrate:
	@echo "Running Alembic migrations..."
	docker-compose -f infrastructure/docker-compose.yml exec backend alembic upgrade head

# --- Quality Assurance ---
test:
	@echo "Running tests..."
	cd frontend && npm run test:run
	docker-compose -f infrastructure/docker-compose.yml exec backend pytest

lint:
	@echo "Running linters..."
	cd frontend && npm run check
	cd backend && flake8 . && black --check .

# --- Testing / Validation ---
smoke:
	@echo "Running smoke test..."
	pip install httpx python-socketio rich
	python scripts/smoke_test.py

loadtest:
	@echo "Running staged load test..."
	pip install locust
	locust -f scripts/load_test.py --host=http://localhost:8000

# --- Kubernetes ---
deploy:
	@echo "Applying Kubernetes manifests..."
	kubectl apply -f infrastructure/kubernetes/
