FROM python

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${HOME}/.poetry/bin:${PATH}"
RUN mkdir -p /opt/code
VOLUME [ "/opt/code" ]
WORKDIR /opt/code
ENTRYPOINT [ "./test.sh" ]
