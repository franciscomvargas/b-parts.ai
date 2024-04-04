### 💀💀💀 REMOVE SECRETS 💀💀💀
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
assTable = "tb_assistants"
userAssThreads = "tb_assistant_threads"

#load_dotenv()

openai.api_key = (ENV_VARS['openai_key'])

app = FastAPI()

client = openai.AsyncOpenAI(api_key=ENV_VARS['openai_key'])
sync_client = openai.OpenAI(api_key=ENV_VARS['openai_key'])



def thread_exists(customer_id):
    sql = "SELECT thread_id FROM tb_assistant_threads WHERE customer_id = %s AND assistant_id = %s"
    
    # Execute the query
    mycursor.execute(sql, (customer_id, "asst_n5SA6rLxPKuVzORBNyfaQyvP"))
    # Fetch one row
    result = mycursor.fetchone()
    # Check if result is not None (thread exists)
    if result is not None:
       return result[0]
    else:
       return False
    
def create_thread(customer_id):
    # Assuming empty_thread is created with your provided method
    empty_thread = sync_client.beta.threads.create()
    #threadjson = empty_thread.model_dump_json()
    
    # Insert the thread information into the database
    sql = "INSERT INTO tb_assistant_threads (assistant_id, thread_id, customer_id, hash) VALUES (%s, %s, %s, %s)"
    val = ("asst_n5SA6rLxPKuVzORBNyfaQyvP", str(empty_thread.id), str(customer_id), "")  # You can modify the values as needed
    
    mycursor.execute(sql, val)
    mydb.commit()  # Commit the changes to the database
    
    #print("Created thread and saved to DB:", threadjson)
    
    return empty_thread.id  # Return the thread ID




async def get_ai_response(thread: str) -> AsyncGenerator[str, None]:
    """
    OpenAI Response
    """

    
    all_content = ""
    async with openai.AsyncClient(api_key=ENV_VARS['openai_key']) as client:
        async with client.beta.threads.runs.create_and_stream(
            thread_id=thread,
            assistant_id="asst_n5SA6rLxPKuVzORBNyfaQyvP",
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

def create_assistant(instructions, name, tools, model):
    assistant = client.beta.assistants.create(
        instructions=instructions,
        name=name,
        tools=tools,
        model=model
    )
    return assistant

@app.get("/create", response_class=HTMLResponse)
async def web_app(request: Request):
    form = """
    <html>
    <head>
    <title>Create assistant</title>
    </head>
    <body>
    
    <h2> <a href='./'> Home </a> | Create assistant: </h2>
    <form method="post" action='./create' >
        <label for="instructions">Instructions:</label><br>
        <input type="text" id="instructions" name="instructions" placeholder="You are a helpful coding instructor..."><br>
        <label for="name">Name:</label><br>
        <input type="text" id="name" name="name" placeholder="Coding assistant"><br>
        <label for="tools">Tools:</label><br>
        <input type="text" id="tools" name="tools" placeholder='[{ "type":"code_interpreter" }]'><br>
        <label for="model">Model:</label><br>
        <input type="text" id="model" name="model" placeholder="gpt-4"><br>
        <input type="submit" value="Create Assistant">
    </form>
    </body>
    </html>
    """
    return HTMLResponse(content=form, status_code=200)


@app.post("/create", response_class=HTMLResponse)
async def submit(instructions: str = Form(...), name: str = Form(...), tools: str = Form(...), model: str = Form(...), files: Optional[List[UploadFile]] = File(None)):

    assistant = sync_client.beta.assistants.create(
        instructions=instructions,
        name=name,
        tools=[{"type":"retrieval"}],
        model=model
    )
    
    sql = "INSERT INTO {assTable} (assistant_id, assistant_active, assistant_meta) VALUES (%s, 1, %s)"
    val = (assistant.id, assistant.model_dump_json())
    mycursor.execute(sql, val)

    mydb.commit()

    html_response = """
    <html>
    <head>
    <title>Assistant created</title>
    </head>
    <body>
    <h2>Assistant Created!</h2>
    <p><strong>Instructions:</strong> {}</p>
    <p><strong>Name:</strong> {}</p>
    <p><strong>Tools:</strong> {}</p>
    <p><strong>Model:</strong> {}</p>
    </body>
    </html>
    """.format(instructions, name, tools, model)

    return HTMLResponse(content=html_response, status_code=200)
    

@app.get("/")
async def web_app() -> HTMLResponse:
#    """
#    Web App
#    """

    mycursor.execute(f"SELECT * FROM {assTable}")

    myresult = mycursor.fetchall()
    assI = 0
    for x in myresult:
        assI+=1 
    if not assI:    
        return HTMLResponse("<html> HI <a href='./create'> Create your assistant </a> </html>")
    else:
        return HTMLResponse(f"<html><head><title>Assistant Admin</title><body><a href='./create'>Add new</a> | List of Assistants: </h2> <p>{assI}</p></body></html>")

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
    """
    Websocket for AI responses
    """
    await websocket.accept()
    while True:
        message = await websocket.receive_text()

        customer = message.split("|")[0].strip()
        if not customer:
           customer = 0 
        thread = thread_exists(customer)
        if thread:
            msg = message.split("|")[1].strip()
        else:
            thread = create_thread(customer)
            msg = message.split("|")[1].strip()
        
        if thread:

            savedmsg = await client.beta.threads.messages.create(
                thread,
                role="user",
                content=msg,
            )

 

        async for text in get_ai_response(thread):
            await websocket.send_text(text)


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