run_server:
	uvicorn food_management.main:app --reload --host 0.0.0.0 --port 8000
