# System imports
import os, json

# 😍 YAML 🤤
import yaml
from yaml.loader import SafeLoader

# typing imports @spacewalkingninja stuff
from typing import AsyncGenerator, NoReturn
from typing import List, Optional
from typing_extensions import override

# openai imports
import openai
from openai.types.beta import AssistantStreamEvent

# db imports
import mysql.connector

# server imports
import uvicorn
from fastapi import FastAPI, WebSocket, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from a2wsgi import ASGIMiddleware

# Script Secrets
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
ENV_VARS_PATH = os.path.join(ROOT_PATH, "config.yaml")
with open( ENV_VARS_PATH ) as ev:
    ENV_VARS = yaml.load(ev, Loader=SafeLoader)
assert ENV_VARS

# how we want to handle the events in the response stream.
class EventHandler(openai.AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)
class AIEventHandler(EventHandler):
    async def __aiter__(self):
        """
        Makes the class an asynchronous iterator
        """
        return self

    async def __anext__(self):
        """
        Returns the next message from the event stream
        """
        response = await self.recv()
        if response["type"] == "message":
            return response["data"]["text"]
        elif response["type"] == "run:complete":
            raise StopAsyncIteration
        else:
            return None



mydb = mysql.connector.connect(
  host="localhost",
  user=ENV_VARS['db_user'],
  password=ENV_VARS['db_pass'],
  database=ENV_VARS['db_name']
)


mycursor = mydb.cursor()
ASS_THREADS = ENV_VARS['chat_tab']

DEV_THREAD = ENV_VARS['dev_thread_id']

#load_dotenv()
OPENAI_KEY = ENV_VARS['openai_key']
openai.api_key = (OPENAI_KEY)

app = FastAPI()

client = openai.AsyncOpenAI(api_key=OPENAI_KEY)
sync_client = openai.OpenAI(api_key=OPENAI_KEY)



def thread_exists(customer_id):
    sql = f"SELECT thread_id FROM {ASS_THREADS} WHERE customer_id = %s"
    # Execute the query
    mycursor.execute(sql, (customer_id, ))
    # Fetch one row
    result = mycursor.fetchone()
    # Check if result is not None (thread exists)
    if result is not None:
       return result[0]
    else:
       return False
    
def create_thread(customer_id):
    # Assuming empty_thread is created with your provided method
    empty_thread_id = sync_client.beta.threads.create().id
    #threadjson = empty_thread.model_dump_json()
    
    # Insert the thread information into the database
    sql = f"INSERT INTO {ASS_THREADS} (chat_id, customer_id, thread_id) VALUES (NULL, %s, %s);"
    val = (str(customer_id), str(empty_thread_id))  # You can modify the values as needed
    
    mycursor.execute(sql, val)
    mydb.commit()  # Commit the changes to the database
    
    #print("Created thread and saved to DB:", threadjson)
    
    return empty_thread_id  # Return the thread ID


async def get_ai_response(thread: str) -> AsyncGenerator[str, None]:
    """
    OpenAI Response
    """
    all_content = ""
    async with openai.AsyncClient(api_key=OPENAI_KEY) as client:
        async with client.beta.threads.runs.create_and_stream(
            thread_id=thread,
            assistant_id=DEV_THREAD,
        ) as stream:
            async for message in stream:
                #if ['message.created', 'step.in_progress', 'thread.run.created', 'thread.run.queued', 'thread.run.in_progress', ''] in message.event:
                #   yield ''
                if str(message.event).endswith('message.delta'):
                    print(message.data.delta.content[0].text.value)
                    try:
                        all_content += str(message.data.delta.content[0].text.value)
                        yield all_content
                    except:
                       yield all_content
                if str(message.event).endswith('message.completed'):
                    print(message.data)
                    try:
                        all_content = str(message.data.content[0].text.value)
                        yield all_content
                    except:
                       yield all_content
                #print(message)
                #yield str(message.event)

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
    """
    Websocket for AI responses
    """
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()


            customer, msg = message.split("|", 1)
            customer = customer.strip()
            thread = thread_exists(customer)
            if not thread:
                thread = create_thread(customer)

            if thread:
                saved_msg = await client.beta.threads.messages.create(
                    thread,
                    role="user",
                    content=msg.strip(),
                )

            async for text in get_ai_response(thread):
                await websocket.send_text(text)
    except WebSocketDisconnect:
        pass  # Handle disconnection gracefully


@app.get("/chatapi")
async def root():
    return {"message": "Hello API World 🐟"}

# mod_wsgi expects the name 'application' by default
application = ASGIMiddleware(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9000,
        log_level="debug",
        reload=True,
    )
