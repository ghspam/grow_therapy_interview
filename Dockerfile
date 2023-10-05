FROM python:3.11

WORKDIR /opt/grow_therapy_interview

RUN python -m venv .venv
ENV PATH=/opt/grow_therapy_interview/.venv:$PATH

RUN . .venv/bin/activate
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .

EXPOSE 8000

CMD ["uwsgi", "--uid", "100", "--lazy", "--http", "0.0.0.0:8000", "--master", "-p", "4", "-w", "app:app"]
