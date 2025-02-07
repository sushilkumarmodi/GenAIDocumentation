FROM python:alpine3.7 
COPY . /app
WORKDIR /app
RUN apk add --no-cache gcc musl-dev
RUN pip install -r requirements.txt 
EXPOSE 5001 
ENTRYPOINT [ "python" ] 
CMD [ "app.py" ] 
