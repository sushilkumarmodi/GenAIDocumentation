FROM python:alpine3.10
COPY . /app
WORKDIR /app
RUN apk add --no-cache gcc musl-dev libffi-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 
EXPOSE 5001 
ENTRYPOINT [ "python" ] 
CMD [ "app.py" ] 
