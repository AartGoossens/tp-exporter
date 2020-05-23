.PHONY: build run tag_and_publish

build:
	docker build -t aartgoossens/tp-exporter .

run:
	docker run -it -v $(pwd)/downloaddir/:/data/ tp-exporter

tag_and_publish: build
	docker push aartgoossens/tp-exporter:latest
	docker tag aartgoossens/tp-exporter:latest aartgoossens/tp-exporter:${VERSION}
	docker push aartgoossens/tp-exporter:${VERSION}
