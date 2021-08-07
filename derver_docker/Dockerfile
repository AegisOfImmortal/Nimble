# Base image
FROM python:3

RUN mkdir -p /Server

COPY ../Server.py .
COPY ../requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 9001
EXPOSE 9002
CMD [ "python3", "Server.py" ]