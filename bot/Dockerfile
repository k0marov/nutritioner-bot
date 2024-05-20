FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./ ./
COPY ./lib ./lib
COPY ./main.py ./

RUN chmod -R 777 ./

CMD ["python", "main.py"]