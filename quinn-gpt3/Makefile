default:
	echo "make check or make deploy"

check:
	python main.py

deploy:
	gcloud functions deploy marvin-gpt3 --runtime python310 --trigger-http --allow-unauthenticated --entry-point marvin_bot
