# Makefile — dev tasks. Works with GNU make.
# On Windows without make, the equivalent command is shown in each comment.

.PHONY: install dev test lint format api front deploy clean

install:  ## install backend + frontend deps
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:  ## run backend API (reload). Win: same command works
	cd backend && uvicorn app.main:app --reload --port 8000

front:  ## run the React dev server. Win: same
	cd frontend && npm run dev

test:  ## run the test suite (the Stop hook runs this too). Win: same
	cd backend && pytest -q

lint:  ## ruff check + format. Win: same
	cd backend && ruff format . && ruff check --fix .

deploy:  ## push to Render/Railway (backend) + Vercel (frontend)
	@echo "Backend deploys on git push to main (Render/Railway git integration)."
	@echo "Frontend:" && cd frontend && npx vercel --prod

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist
