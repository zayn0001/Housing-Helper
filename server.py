from fastapi import FastAPI, Form
import openai
import pandas
import uvicorn
from dotenv import load_dotenv
from typing_extensions import override

load_dotenv()
app = FastAPI()


client = openai.OpenAI()

vectorsestoreid = "vs_TmTo1l9o3hoAhLkWm3EY87T4"
@app.post("/ask_question/")


async def ask_question(question: str = Form(...)):

  assistant = client.beta.assistants.create(
    instructions="You are a helpful housing support assistant and you answer questions based on the files provided to you.",
  model="gpt-4-turbo",
  tools=[{"type": "file_search"}],
  tool_resources={
    "file_search": {
      "vector_store_ids": ["vs_TmTo1l9o3hoAhLkWm3EY87T4"]
    }
  }
  ) 
  thread = client.beta.threads.create()

  run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="You are a helpful housing support assistant and you answer questions based only  on the files provided to you. "+ question,
  )

  if run.status == 'completed': 

      messages = client.beta.threads.messages.list(
          thread_id=thread.id
      )
      
      contents = messages.data[0].content
      print(contents)

      return contents

        

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
