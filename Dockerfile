# Stage 1: Build Dependencies
FROM python:slim as builder

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip && \
    pip install --quiet --no-cache-dir --no-warn-script-location --user -r requirements.txt

# Stage 2: Runtime
FROM python:slim
ENV GRADIO_SERVER_NAME=0.0.0.0

RUN rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local/lib/python3.11/site-packages /root/.local/lib/python3.11/site-packages

COPY raccoon_emoji.png raccoon_emoji.png
COPY app.py app.py

CMD [ "python" , "-u", "app.py" ]
EXPOSE 7860
