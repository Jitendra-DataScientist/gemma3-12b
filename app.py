from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import asyncio
import uvicorn
import re
import json


app = FastAPI()

# Allowing all origins for now
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Regular expression to match the code block delimiters
pattern = r'```[a-z]*\n([\s\S]*?)\n```'

# Function to remove the delimiters
def remove_code_block_delimiters(text):
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


class QueryRequest(BaseModel):
    text: str
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/gemma3-12b/ask-question/", response_model=QueryResponse)
async def ask_question_from_text(request: QueryRequest):
    try:
        # Prepare the prompt for the model
        prompt = f"Based on the following text, answer the question:\n\nText: {request.text}\n\nQuestion: {request.question}"

        # Generate the response using the model
        response = ollama.chat(
            model='gemma3:12b',
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )

        # Extract the model's reply
        answer = response['message']['content'].strip()

        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class ExtarctionRequest(BaseModel):
    prompt: str

class ExtarctionResponse(BaseModel):
    answer: str

@app.post("/gemma3-12b/ner/", response_model=ExtarctionResponse)
async def ask_question_from_text(request: ExtarctionRequest):
    try:
        print ("/gemma3-12b/ner/ endpoint hit")
        # # Prepare the prompt for the model
        # prompt = f"Based on the following text, answer the question:\n\nText: {request.text}\n\nQuestion: {request.question}"

        # Generate the response using the model
        response = ollama.chat(
            model='gemma3:12b',
            messages=[{
                'role': 'user',
                'content': request.prompt
            }]
        )

        # Extract the model's reply
        answer = remove_code_block_delimiters(response['message']['content'].strip())
        try:
            print (json.dumps(answer, indent=4))
        except:
            print ("invalid json")

        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






if __name__ == "__main__":
    # Initialize the ollama client if necessary
    # ollama_client = ollama.Client(...)

    # Sample input data
    # sample_request = QueryRequest(
    #     text="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+.",
    #     question="What is FastAPI?"
    # )

    # # Function to call the API endpoint
    # async def test_ask_question():
    #     try:
    #         # Call the endpoint function directly
    #         response = await ask_question_from_text(sample_request)
    #         print(f"Answer: {response.answer}")
    #     except HTTPException as http_exc:
    #         print(f"HTTP Exception: {http_exc.detail}")
    #     except Exception as exc:
    #         print(f"An error occurred: {exc}")

    # # Run the test function in the event loop
    # asyncio.run(test_ask_question())

    # Start the FastAPI application
    # uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8005)
