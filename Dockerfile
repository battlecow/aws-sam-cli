FROM python:2-slim

COPY ./dist /workdir
WORKDIR /workdir

RUN pip install /workdir/* && \
	rm -rf /workdir

ENTRYPOINT ['/usr/local/bin/sam']
