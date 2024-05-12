from fastapi import FastAPI, Form, Response
import openai
import uvicorn
from dotenv import load_dotenv
from typing_extensions import override
from fastapi.middleware.cors import CORSMiddleware
import re
from openai import AssistantEventHandler
from fastapi.responses import JSONResponse
import pusher

pusher_client = pusher.Pusher(
  app_id='1795501',
  key='f1aa2008be7ccd59a34a',
  secret='86333e337bf916f2dd0a',
  cluster='mt1',
  ssl=True
)


class EventHandler(AssistantEventHandler):    
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
    pusher_client.trigger('my-channel', 'my-event', {'message': delta.value})
    

load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to ["*"] to allow requests from any origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
) 


vectorstorepdfs = {'file-5IED2QKjBtQPncyo29sb3bd2':'Home Maintenance for Dummies',
 'file-DNbDePyPmU1C9ZhLe56QWAdp':"Packet of Home Maintenance Information",
 'file-TYvB0JEnYUSigMhDKeWE6kUy':"HOMEOWNER MAINTENANCE MANUAL - National Home Warranty",
 'file-VNdRZp7AmPBZm8iBHcdKeREJ':"HOMEOWNER MAINTENANCE MANUAL - StrucSure Home Warranty",
 'file-MH3jm6gmvedNnx5TwwTdYrza': "HOME MAINTENANCE STUDENT MANUAL - Northwest Territories Housing Corporation"}


client = openai.OpenAI()

vectorsestoreid = "vs_oyCadoQAfTDgr6r1OwLbiZPr"

@app.post("/ask_question/")
def ask_question(question: str = Form(...)):

  

  assistant = client.beta.assistants.create(
    instructions="You are a helpful housing support assistant and you answer questions based on the files provided to you.",
  model="gpt-4-turbo",
  tools=[{"type": "file_search"}],
  tool_resources={
    "file_search": {
      "vector_store_ids": [vectorsestoreid]
    }
  }
  ) 
  thread = client.beta.threads.create()
  """
  run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="You are a helpful housing support assistant. Answer the following question based only on the files provided to you: "+ question,
  )

  if run.status == 'completed': 

      messages = client.beta.threads.messages.list(
          thread_id=thread.id
      )
      
      content = messages.data[0].content[0].text
      print(content)
      annotations = content.annotations
      value = content.value
      filesaccessed = set()
      for annot in annotations:
        file_id = annot.file_citation.file_id
        filename = vectorstorepdfs[file_id]
        filesaccessed.add(filename)
      pdffiles = []
      for file in filesaccessed:
         pdffiles.append({"name":file})


      cleaned_string = re.sub(r'【.*?】', '', value)
      return {"answer":cleaned_string, "files":pdffiles}

      """

  stream = client.beta.threads.runs.create(
    thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="You are a helpful housing support assistant. Do not mention anything about the files. Answer the following question based only on the files provided to you: "+ question,
    stream=True
    )
  
  
  
  buffer = ""
  startbuffer = False
  for event in stream:
    print(event)
    if event.event =="thread.message.delta":
      value = event.data.delta.content[0].text.value

      value = value.replace("\n","<br/>")
      if "**" in value:
        if not startbuffer:
          buffer = value.replace("**","<strong>")
          startbuffer = True
          continue
        else:
          value = value.replace("**","</strong>")
          buffer += value
          startbuffer = False
          print(buffer, end="",flush=True)
          pusher_client.trigger('my-channel', 'my-event', {'message': buffer})
          continue

      if startbuffer:
        buffer+=value
        continue
      
      cleaned_string = re.sub(r'【.*?】', '', value)
      print(cleaned_string, end="",flush=True)
  
      pusher_client.trigger('my-channel', 'my-event', {'message': cleaned_string}) 

  
  messages = client.beta.threads.messages.list(
          thread_id=thread.id
  )
  content = messages.data[0].content[0].text
  annotations = content.annotations
  value = content.value
  filesaccessed = set()
  for annot in annotations:
    file_id = annot.file_citation.file_id
    filename = vectorstorepdfs[file_id]
    filesaccessed.add(filename)
  pdffiles = []
  for file in filesaccessed:
      pdffiles.append({"name":file})

  print(pdffiles)

  
  return pdffiles
  
    

  
  
        

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
