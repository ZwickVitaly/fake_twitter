FROM python:3.12-slim


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . ./tests

CMD pytest tests -vv | tee -a ./tests/logs/$(date +%Y%m%d).log
