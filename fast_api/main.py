from fastapi import FastAPI
import createCard

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/createCard", response_class=PlainTextResponse)
async def create_summary(
    title: str = Form(...),
    tools: str = Form(...),
    reflection: str = Form(...),
    pdf_file: UploadFile = File(...)
):
    """
    개발 경험 카드 요약을 생성하는 엔드포인트
    """
    # 업로드된 PDF 파일 저장
    pdf_file_path = f"./temp_{pdf_file.filename}"
    with open(pdf_file_path, "wb") as buffer:
        shutil.copyfileobj(pdf_file.file, buffer)

    # 사용자 입력 구성
    user_input = {
        "title": title,
        "tools": tools.split(','),  # 문자열을 리스트로 변환
        "reflection": reflection,
        "pdf_file_path": pdf_file_path
    }

    # 요약 생성
    summary = generate_summary(user_input)

    # 임시 PDF 파일 삭제
    os.remove(pdf_file_path)

    return summary
