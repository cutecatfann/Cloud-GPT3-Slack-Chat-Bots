default:
	echo "make check or make deploy"

check:
	python main.py

deploy:
	gcloud functions deploy marvin-handler --runtime python310 --trigger-http --allow-unauthenticated --entry-point hello_world
