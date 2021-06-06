FROM python:3.9
COPY ./setup /server/setup
RUN pip install -r /server/setup/Requirements.txt
COPY ./src/python /server/python
COPY ./secrets /server/secrets
WORKDIR /server
CMD ["python3.9", "/server/python/server.py"]
