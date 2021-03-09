# FROM python:3
FROM therolf/python-ffmpeg:latest

ADD ./ /app/

WORKDIR /app
COPY ./requirements.txt ./

# RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --upgrade pip && \
pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]