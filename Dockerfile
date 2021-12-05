FROM python:3.9

WORKDIR /code

ENV NOTHING=0.0.0.0

RUN apt-get update
RUN apt install -y libgl1-mesa-glx

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8080

COPY . .

COPY start-container /usr/local/bin/start-container
RUN chmod +x /usr/local/bin/start-container
ENTRYPOINT ["start-container"]