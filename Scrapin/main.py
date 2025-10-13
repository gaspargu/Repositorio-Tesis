from fastapi import FastAPI
import uvicorn
from ollama import chat

app = FastAPI()

@app.get("/")
def read_root():
    response = chat(model="gemma3:4b", messages=[
        {"role": "user", "content": "Hola, ¿cómo estás?"}
    ]) 
    print(response)
    return {"Hello": "World",
            "2":"2"}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)