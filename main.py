from fastapi import FastAPI, File, HTTPException, UploadFile, Form, Body, Request
from fastapi.responses import JSONResponse
import tempfile
import subprocess
import os
from pydantic import BaseModel

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.get("/")
async def get_main():
    return {"message": "Welcome to Code Process Helper!"}


# @app.post("/execute")
# async def run_code_post(
#         *,
#         code: str = Form(...),
#         # uploadFile: UploadFile = File(...)
#         # uploadFile: str = Form(...)
# ):

@app.post("/execute")
async def execute_code(code_request: CodeRequest):
    code = code_request.code
    if not code:
        raise HTTPException(status_code=400, detail="Bad request. Missing 'code' field.")

    # if uploadFile.content_type!= "text/csv":
    #     raise HTTPException(status_code=415, detail="File type is not csv")

    # content = await uploadFile.read()
    # 1. 临时存储CSV文件linux系统使用
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", encoding="utf-16") as temp_csv:
    #     content = await uploadFile.read()
    #     temp_csv.write(content)
    #     temp_csv_path = temp_csv.name

    # 1. 创建临时文件 Windows系统
    # fd, temp_csv_path = tempfile.mkstemp(suffix=".csv", text=True)
    # os.close(fd)
    # # 使用正确的编码解析文件内容并存储为 CSV
    # with open(temp_csv_path, 'w') as temp_csv:
    #     temp_csv.write(uploadFile)

    # code1 = """temp_csv_path = r'{}'
    # {}
    # """.format(temp_csv_path, uploadCode)


    # with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_py:
    #     temp_py.write(code)
    #     temp_py_path = temp_py.name

    try:
        # result = subprocess.run(["python", temp_py_path], text=True, timeout=30, capture_output=True)
        result = subprocess.run(["python", '-c', code], text=True, timeout=30, capture_output=True)
        if result.returncode != 0:
            return {"error": result.stderr}

        # Return the output
        output = {"message": "Code executed successfully", "result": result.stdout}
        return JSONResponse(content=output)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Compilation timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup: delete the temporary files
        # os.remove(temp_py_path)
        # os.remove(temp_csv_path)
        # print(temp_csv_path)
        pass

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=80)