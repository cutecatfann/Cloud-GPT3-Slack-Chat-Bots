default:
	echo "make check or make deploy"

check:
	python main.py

deploy:
	gcloud functions deploy joojoo-hf --runtime python310 --trigger-http --allow-unauthenticated --entry-point hello_world
