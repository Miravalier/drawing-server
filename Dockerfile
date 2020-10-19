FROM python:3.9
WORKDIR /drawing-game
COPY ./src /drawing-game/src
COPY ./setup /drawing-game/setup
# RUN pip install -r /drawing-game/setup/requirements.txt
CMD ["python3.9", "/drawing-game/src/main.py"]
