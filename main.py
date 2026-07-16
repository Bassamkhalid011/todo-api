from fastapi import FastAPI
app=FastAPI()
@app.get("/")
def read_root():
    return {"name": "Bassam",
            "version": "1.0",
            "description": "This is a simple FastAPI application.",
            "endpoints": ["/tasks"]}
@app.get("/health")
def health():
    return {"status": "healthy"}