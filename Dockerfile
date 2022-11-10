FROM python:slim
EXPOSE 7860

ENV GRADIO_SERVER_NAME=0.0.0.0
WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    make \
    gcc

ADD requirements.txt /workspace/requirements.txt
RUN pip install --upgrade pip
RUN pip install --quiet --no-cache-dir -r requirements.txt

RUN apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ADD app.py /workspace/
CMD [ "python" , "/workspace/app.py" ]
