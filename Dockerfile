FROM python:alpine3.7 
COPY . /app
WORKDIR /app
RUN apt-get -y install gcc
RUN pip install -r requirements.txt 
EXPOSE 5001 
ENTRYPOINT [ "python" ] 
CMD [ "app.py" ] 
