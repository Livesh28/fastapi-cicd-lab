from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello CI/CD"}


@app.get("/health")
def health():
    return {"status": "healthy"}