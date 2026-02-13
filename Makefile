up:
	docker-compose up --build

down:
	docker-compose down

ingest:
	docker-compose exec api python ingestion/run_ingestion.py

train:
	docker-compose exec api python ml/train.py

retrain:
	docker-compose exec api python ml/retrain.py
