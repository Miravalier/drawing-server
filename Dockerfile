FROM python:3.9
WORKDIR /drawing-game
COPY ./python /drawing-game/src/python
COPY ./js /drawing-game/src/js
COPY ./setup /drawing-game/setup
RUN pip install -r /drawing-game/setup/Requirements.txt
CMD ["python3.9", "/drawing-game/python/main.py"]
