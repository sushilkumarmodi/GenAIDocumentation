FROM python:alpine3.10
FROM rust:1.67-alpine3.16
COPY . /app
WORKDIR /app
RUN apk add --no-cache gcc musl-dev libffi-dev py3-pip python3-dev
RUN apk add --no-cache curl
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install --ignore-installed packaging
RUN pip install -r requirements.txt 
EXPOSE 5001 
ENTRYPOINT [ "python" ] 
CMD [ "app.py" ] 
