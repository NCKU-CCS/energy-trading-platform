.PHONY: all clean
all: build_docker
build_docker: 
	pipenv lock --requirements > platform/requirements.txt
	docker login
	docker build --no-cache -t platform_docker:latest platform/
	docker tag platform_docker ttw225/platform_docker
	docker push ttw225/platform_docker
