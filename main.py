from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import tempfile
import subprocess
import pandas as pd


app = FastAPI()

@app.get("/")
async def get_main():
    return {"message": "Welcome to Code Process Helper!"}


@app.get("/runcode")
async def run_code():
    return {"message": "This is the runcode endpoint, you get it!"}




if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=80)