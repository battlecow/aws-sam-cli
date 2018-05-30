FROM python:2

COPY . /workdir
WORKDIR /workdir

RUN python setup.py sdist

FROM python:2-slim
COPY --from=0 /workdir/dist /workdir/
RUN pip install /workdir/*

ENTRYPOINT ['/usr/local/bin/sam']
