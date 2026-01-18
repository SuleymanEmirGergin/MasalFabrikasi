.PHONY: up down restart logs test test-unit test-int shell-backend clean

# Docker operations
up:
	docker-compose up -d --build

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f backend

# Testing
test:
	docker-compose exec backend pytest

test-unit:
	docker-compose exec backend pytest tests/unit

test-int:
	docker-compose exec backend pytest tests/integration

# Development
shell-backend:
	docker-compose exec backend /bin/bash

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
