FROM python:3.7-alpine
WORKDIR /server
COPY requirements.txt /server
RUN pip install -r requirements.txt
COPY . /server
ENV FLASK_APP=__init__.py
EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0", "--with-threads"]

