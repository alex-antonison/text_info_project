FROM python:3.7.5

ADD data/ data/

ADD reference/ reference/

ADD text_processing.py /

ADD requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "./text_processing.py" ]