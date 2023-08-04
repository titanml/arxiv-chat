FROM pytorch/pytorch:latest

WORKDIR /code
RUN mkdir /code/data

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

COPY ./app /code/app
RUN pip install -e /code/app/vlite
COPY ./run.sh /code/run.sh

ENTRYPOINT ["bash", "run.sh"]