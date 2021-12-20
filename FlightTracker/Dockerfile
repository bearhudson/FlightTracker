FROM python:latest
LABEL Maintainer="Brian Hiudson"
WORKDIR /usr/src
COPY *.* ./
RUN '/usr/bin/curl -sSL https://install.python-poetry.org | python - && /root/.local/bin/./poetry install -n'
CMD [ "python", "./main.py"]