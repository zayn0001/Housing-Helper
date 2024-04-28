from fastapi import FastAPI, Form
import openai
import uvicorn
from dotenv import load_dotenv
from typing_extensions import override

load_dotenv()
app = FastAPI()


client = openai.OpenAI()

vectorsestoreid = "vs_oyCadoQAfTDgr6r1OwLbiZPr"

vectorstorepdfs = {'file-5IED2QKjBtQPncyo29sb3bd2':'Home Maintenance For Dummies',
 'file-DNbDePyPmU1C9ZhLe56QWAdp':'Packet of Home Maintenance Information',
 'file-TYvB0JEnYUSigMhDKeWE6kUy':'Homeowner Maintenance Manual - National Home Warranty',
 'file-VNdRZp7AmPBZm8iBHcdKeREJ':'Homeowner Maintenance Manual - StrucSure Home Warranty',
 'file-MH3jm6gmvedNnx5TwwTdYrza':'Home Maintenance Student Manual - Northwest Territories Housing Corporation'}

@app.post("/ask_question/")


async def ask_question(question: str = Form(...)):

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
      
      return {"answer":value, "files":pdffiles}

        

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
