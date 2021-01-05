FROM python:3.9
WORKDIR /server
COPY ./src/python /server/python
COPY ./setup /server/setup
COPY ./secrets /server/secrets
RUN pip install -r /server/setup/Requirements.txt
CMD ["python3.9", "/server/python/server.py"]
