build:
	docker build . -f Dockerfile -t vidprep
rebuild:
	docker build --no-cache . -f Dockerfile -t vidprep
