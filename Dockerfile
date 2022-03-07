FROM python:3.9-slim

WORKDIR /code

RUN apt-get update && apt install -y libgl1-mesa-glx libglib2.0-0

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8080

COPY . .

CMD ["python3", "main.py"]