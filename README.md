**Approach:**

The implementation has been done with FastAPI. There are two main endpoints The root endpoint ("/") that is the entry point of the application and renders a basic HTML page. The other is a websocket endpoint ("/chat"), that sets up a websocket connection when the root endpoint is hit.

Websocket has been used to facilitate real time chat experience. Redis has been used as a message queue which allows a number of benifits as bellow:

    1. When a web client sends a message instead of directly processing it and sending a response, the messages are being piushed to the redis list. This helps by separting the concerns of message receiving and message processing, in the scenarios when latency or heavy processing is involved.

    2. By offloading the message handling to redis the application can handle a large number of websocket connection without overloadind the FastAPI server which is benificial in real time applications.

    3. The "process_messages" coroutine continuously checks for new messages in the redis list. The asynchronous processing ensures that the websocket endpoint can quickly handle incoming messages without having to wait for the generation time of the response.

**Process Flow:**

When the FastAPI server is started, upon application startup an event handler is used to call the function startup() that initializes the connection set (which stores web socket connections) and also runs a coroutine function "process_messages()"

The "process_messages()" function coninuously and asynchronously checks if any message is available in the redis list. If it is available then it generates a random response from corpus and calls another async function "send_response_to_clients()"

The "send_response_to_clients()" function iterates over all the websocket connections stored in connections set and sends the response through websocket to each connected client.

The ("/") end point renders a html file ("index.html) which allows the user to enter messages. When a websocket connection is established through the ("/chat") endpoint, the websocket connection is added to the connections set and it continuosly recieves the input message from the client and stores it in a redis list.

The connections set is emptied when an error occurs while receiving messages or pushing to redis

**How to Set Up:**

    1. Clone the repo
    2. pip3 install -r requirements.txt
    3. sudo apt install redis-server
    4. sudo systemctl start redis (if not started by default after installation)
    5. Run the python script main.py in the app directory. This would automatically start the FastAPI application.
    6. Visit http://localhost:8000, which would display a simple html page to interact with the backend.
    7. Type in the messages and the response should be displayed

**Tests:**

Two tests have been implemented in the "test_chatbot.py" file, using the pytest library and the fast API Test Client. One of which is to test the websocket connection ( test_websocket ) and the other is to test the randomness of the responses (test_randomness). Both the tests are passed if the websocket connection is successful and the responses are random.

**To test:**

navigate to the /app directory and run "pytest"
