import pytest
from fastapi.testclient import TestClient
from app.main import app, CORPUS, process_messages, startup
import asyncio
import websockets
import random
import aioredis
import randtest as rt

client = TestClient(app)

CORPUS_DICT = {
    "What a lovely day, today.": 0,
    "Feels great to connect with you.:": 1,
    "What do you think is the easiest way to solve a rubix cube?": 2,
    "strange that Strange never used time stome to beat Thanos.": 3,
    "Soon I will be intelligent enough to answer that.": 4,
    "What's your opinion on multiverse?": 5,
    "With great power comes great responsibilities.": 6,
    "Would you rather be Iron man or Batman?": 7,
    "Let's talk MARVEL.": 8,
    "What's your favourite sport? Mine is soccer.": 9
}

# Fixture to configure the initializations and start the process_messages co routine
@pytest.fixture(scope="module", autouse=True)
async def setup():
    startup()
    asyncio.create_task(process_messages())

    
# A test to check whether websocket connection is successful
@pytest.mark.asyncio
async def test_websocket():
    async with websockets.connect("ws://localhost:8000/chat") as websocket:
        await websocket.send("Hello")
        response = await websocket.recv()
        assert response in CORPUS, "Websocket connection is successful"

#A test to check the randomness of the responses using randint. 
#The response order is found from the CORPUS_DICT and stored in a list. This is then evaluated with random_score method.
@pytest.mark.asyncio
async def test_randomness():
    async with websockets.connect("ws://localhost:8000/chat") as websocket:
        received_responses = []
        for _ in range(10):
            await websocket.send("Hello")
            response = await websocket.recv()
            key = CORPUS_DICT.get(response)
            received_responses.append(key)
        assert rt.random_score(received_responses) == True, "Responses are random"
        


