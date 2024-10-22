from .services.createCard.createCard import generate_summary
from .services.introduceAi.introduceAi import ChatBotManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import JSONResponse
import ast

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
    tool: str = Form(...),  # tools를 리스트로 받기
    reflection: str = Form(...),
    pdfText: str = Form(...)
):
    """
    개발 경험 카드 요약을 생성하는 엔드포인트
    """
    
    try:
        position_list = ast.literal_eval(position)
        tool_list = ast.literal_eval(tool)
    except Exception as e:
        return JSONResponse(content={"error": f"Invalid format for position or tool: {e}"}, status_code=400)

    # 사용자 입력 구성
    user_input = {
        "title": title,
        "position": position_list,
        "tool": tool_list,
        "reflection": reflection,
        "pdfText": pdfText
    }

    # 요약 생성
    summary = generate_summary(user_input)

    return JSONResponse(content={"summary": summary})


# 챗봇 매니저 초기화
chatbot_manager = ChatBotManager()

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    session_id = await chatbot_manager.create_session(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = await chatbot_manager.handle_message(session_id, data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        chatbot_manager.remove_session(session_id)
