from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import tempfile
import subprocess
import pandas as pd


app = FastAPI()

@app.get("/")
async def get_main():
    return {"message": "Welcome to Code Process Helper!"}


@app.post("/uploadCodeAndFile")
async def run_code_post(
        code: str = Form(...),
        file: UploadFile = File(...)
):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=415, detail="File type is not csv")

    # with tempfile.NamedTemporaryFile(delete=False, suffix=".py", encoding="utf-8") as temp_py:
    #     # py_content = code
    #     temp_py.write(code)
    #     temp_py_path = temp_py.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
        content = await file.read()
        temp_csv.write(content)
        temp_csv_path = temp_csv.name

    try:
        result = subprocess.run(["python",'-c', code, temp_csv_path],capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
        if result.returncode != 0:
            return {"error": result.stderr}
            # raise Exception("Subprocess failed with return code", result.returncode)
        # 子进程运行后
        output = {"message": "Code executed successfully", "output": result.stdout}
        return JSONResponse(content=jsonable_encoder(output))
        # with open('output.txt', 'r', encoding='utf-8') as file:
        #     print("==================")
        #     print(file.read())
        # return JSONResponse(content=output)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Compilation timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=80)