from fastapi import FastAPI

app = FastAPI(title="RecoverAI")


@app.get("/")
def root():
    return {
        "message": "RecoverAI API is running"
    }