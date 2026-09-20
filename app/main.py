from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello CI/CD v2"}


@app.get("/health")
def health():
    return {"status": "healthy"}
