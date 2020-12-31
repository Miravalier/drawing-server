FROM python:3.9
WORKDIR /drawing-game
COPY ./src/python /drawing-game/python
COPY ./src/js /drawing-game/js
COPY ./setup /drawing-game/setup
RUN pip install -r /drawing-game/setup/Requirements.txt
CMD ["python3.9", "/drawing-game/python/main.py"]
