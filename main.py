from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
import tempfile
import subprocess
import os
from pydantic import BaseModel
from typing import Optional, List
import csv
import re
import importlib
import uuid
import pandas as pd
from io import StringIO



app = FastAPI()


class CodeRequest(BaseModel):
    code: str
    file_string: Optional[str] = None


class Packages(BaseModel):
    p: List[str] = []


@app.get("/")
async def get_main():
    return {"message": "Welcome to Code Process Helper!"}


# @app.post("/package")
async def package(package: Packages):
    if install_packages(package.p):
        return JSONResponse(content='success')

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_unique_filename(filename):
    unique_filename = str(uuid.uuid4())
    _, file_extension = os.path.splitext(filename)
    return f"{unique_filename}{file_extension}"

# @app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    filename = get_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return JSONResponse(content={"filename": filename}, status_code=200)


@app.post("/execute")
async def execute_code(code_request: CodeRequest):
    code = code_request.code
    received_string = code_request.file_string
    if not code:
        raise HTTPException(status_code=400, detail="Bad request. Missing 'code' field.")
    lines = code.split("\n")
    for line in lines:
        if line.startswith("import") or line.startswith("from"):
            try:
                exec(line, globals())
            except ModuleNotFoundError as e:
                module_name = e.name
                print(f"\033[41mError: Required module not found ({e.name}).\033[0m")
                print(f"\033[43mpip install {e.name}\033[0m")
                try:
                    subprocess.run(["pip", "install", module_name])
                except Exception as e:
                    print(f"\033[41mError: {e}\033[0m")

    # 有文件情况
    if received_string is not None:
        # file_path = os.path.join(UPLOAD_FOLDER, filename)
        df_received = pd.read_csv(StringIO(received_string))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
            df_received.to_csv(temp_csv.name, index=False)
            temp_csv_path = temp_csv.name

        print(f"Temp CSV file created at: {temp_csv_path}")

        pattern = re.compile(r"'(path_to[^']*)'")
        if os.path.exists(temp_csv_path):
            code_with_file = pattern.sub(f"'{temp_csv_path}'", code)
        else:
            raise HTTPException(status_code=400, detail="Bad request. File not found, please upload the file first.")

        try:
            # 创建一个空字典，用于存储执行结果
            exec_result = {}
            # 使用exec()执行代码，并将执行结果存储到exec_result字典中
            print(code_with_file)
            exec(code_with_file, {}, exec_result)
            # 如果代码执行成功，返回消息和结果
            return {"message": "Code executed successfully", "result": exec_result.get("results")}
        except Exception as e:
            # 如果执行过程中出现异常，返回错误消息
            return {"error": str(e)}
        finally:
            # Cleanup: delete the temporary files
            # os.remove(temp_csv_path)
            # print(temp_csv_path)
            pass
    # 没有文件情况，直接执行代码
    else:
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_py:
        #     temp_py.write(code)
        #     temp_py_path = temp_py.name
        try:
            # install_packages(required_packages)
            # result = subprocess.run(["python", temp_py_path], text=True, timeout=30, capture_output=True)
            # result = subprocess.run(["/home/user/.virtualenvs/0111/bin/python", '-c', code], text=True, timeout=30, capture_output=True)
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
            pass


def install_packages(packages):
    missing_packages = [package for package in packages if importlib.util.find_spec(package) is None]
    if missing_packages:
        print(f"Installing missing packages: {missing_packages}")
        subprocess.run(['pip', 'install'] + missing_packages)
    else:
        print("All required packages are already installed.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8008)
