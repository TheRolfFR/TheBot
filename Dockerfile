FROM python:3

ADD ./bot-discord/ /app/

WORKDIR /app
COPY ./bot-discord/requirements.txt ./

RUN pip install --upgrade pip && \
pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]