import random
import uvicorn
import aioredis
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from asyncio import sleep, create_task
from fastapi.templating import Jinja2Templates
import logging

app = FastAPI()


CORPUS = [
    "What a lovely day, today.",
    "Feels great to connect with you.",
    "What do you think is the easiest way to solve a rubix cube?",
    "strange that Strange never used time stome to beat Thanos.",
    "Soon I will be intelligent enough to answer that.",
    "What's your opinion on multiverse?",
    "With great power comes great responsibilities.",
    "Would you rather be Iron man or Batman?",
    "Let's talk MARVEL.",
    "What's your favourite sport? Mine is soccer."
]


redis = aioredis.from_url("redis://localhost")

templates = Jinja2Templates(directory="templates/") 

#to log the errors in errors.log file
logging.basicConfig(filename='errors.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s') 

#function to generate random request from corpus
async def get_random_response():
    return random.choice(CORPUS)


#an asynchronous function that is called on startup and there after continuously checks if there is in message in redis list. 
#If there is then random response is sent to all clients.
async def process_messages():

    while True:
        message = await redis.rpop("messages")

        if message:
            response = await get_random_response()
            await send_response_to_clients(response)
        else:
            await sleep(1)


#function that iterates over all the active websocket connections and sends the response passed in from previous function to all connected clients
async def send_response_to_clients(response):
    try:
        for connection in app.state.connections:
            await connection.send_text(response)
    except Exception as e:
        logging.error(str(e))


#Endpoint to render the simple HTML page
@app.get("/")
async def index_endpoint(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})


#Websockent end point that is connected from the front end whenever someone visits the root endpoint. 
#It continuously and asynchronously recieves text from the user (through websocket) and stores it in the redis list
@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
   
    app.state.connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await redis.lpush("messages", data)
    except Exception as e:
        logging.error(str(e))
    finally:
        app.state.connections.remove(websocket)


#This method is called when the fastapi application starts up. 
#Here the connection set is initilized to store websocket connections and the coroutine function "process_manager" is made to run concurrently.
def startup():
    app.state.connections = set()
    create_task(process_messages())


#call startup() function when startup event occurs
app.add_event_handler("startup", startup)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)