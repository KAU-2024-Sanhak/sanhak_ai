from .services.createCard import extract_text_from_pdf, generate_summary
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/createCard", response_class=JSONResponse)
async def create_summary(
    title: str = Form(...),
    position: str = Form(...),  # position을 리스트로 받기
    tools: str = Form(...),  # tools를 리스트로 받기
    reflection: str = Form(...),
    pdf_file: UploadFile = File(...)
):
    """
    개발 경험 카드 요약을 생성하는 엔드포인트
    """
    
    # position과 tools를 쉼표로 구분된 문자열에서 리스트로 변환
    position_list = position.split(",")  # 'backend, application' => ['backend', 'application']
    tools_list = tools.split(",")  # 'kotlin, python, android studio' => ['kotlin', 'python', 'android studio']

    # 사용자 입력 구성
    user_input = {
        "title": title,
        "position": position_list,
        "tools": tools_list,
        "reflection": reflection,
        "pdf_file": pdf_file
    }

    # 요약 생성
    summary = generate_summary(user_input)

    return JSONResponse(content={"summary": summary})
