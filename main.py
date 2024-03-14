from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import uvicorn
from constants import ASSISTANT_ID, API_KEY
import time
import json

client = OpenAI(api_key=API_KEY)

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/measures")
async def main(summary="Knowledge gap in developers", description="the development team lacks people who are expert in the tech stack"):


    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"""
            Risk summary: {summary}
            Risk description: {description}
        """
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        )
    
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1) # Wait for 1 second
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        

    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        last_message = messages.data[0].content[0].text.value
        return json.loads(last_message)
    else:
        print(run.status)

@app.get("/more")
async def get_more(thread_id=""):
    thread = client.beta.threads.retrieve(thread_id=thread_id)

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please provide more mitigations"
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        )
    
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1) # Wait for 1 second
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        

    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        return messages
    else:
        print(run.status)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)