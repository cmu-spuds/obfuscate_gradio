FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
EXPOSE 7860

ENV GRADIO_SERVER_NAME=0.0.0.0
WORKDIR /workspace

ADD requirements.txt /workspace/requirements.txt
RUN pip install -r requirements.txt

ADD app.py /workspace/
CMD [ "python" , "/workspace/app.py" ]
