FROM python:3.7-alpine

# Main application setup
WORKDIR /application

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "run_server.py" ]