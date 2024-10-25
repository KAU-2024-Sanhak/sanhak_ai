from .services.createCard.createCard import generate_summary
from .services.introduceAi.introduceAi import ChatBotManager
from .services.interviewAi.interviewAi import interview_init_chain
from .services.generalAi.generalAi import general_init_chain
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form, HTTPException
from fastapi.responses import JSONResponse
import ast
from pydantic import BaseModel
from datetime import datetime, timedelta


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

class UserInput(BaseModel):
    title: str  # 프로젝트 제목
    tool: list[str]  # 사용한 도구들
    position: str  # 역할
    reflection: str  # 느낀 점
    pdfText: str # pdf 내용

class UserData(BaseModel):
    userId: str  # 사용자 ID
    userInput: UserInput  # 사용자가 입력한 데이터
    question: str  # 질문

session = {"generalAi" : {}, "interviewAi" : {}, "intorduceAi" : {}}

# 세션 정리 함수
def cleanup_expired_sessions(aiAssistant):
    current_time = datetime.now()
    expired_users = []

    # 인터뷰 AI 세션에서 만료된 사용자 찾기 (5분동안 post요청 X)
    for user_id, data in session[aiAssistant].items():
        if current_time - data["requestTime"] > timedelta(minutes=5):
            expired_users.append(user_id)

    # 만료된 사용자 세션 제거
    for user_id in expired_users:
        del session[aiAssistant][user_id]
        print(f"Session for {user_id} has been removed due to inactivity")

@app.post("/generalAi")
async def general(userData: UserData):

    userId = userData.userId
    userInput = userData.userInput
    question = userData.question

    # post 요청이 들어올 때 마다 각 UserId에 대해 마지막 post요청보다 일정 시간 지날 경우 해당 userId 값 삭제
    cleanup_expired_sessions("generalAi") 

    try:
        # 질문에 대한 응답 생성
        if userId not in session["generalAi"]:
            conversationAi = general_init_chain(userInput=userInput)
            response = conversationAi.invoke(question)
            session["generalAi"][userId] = {
                'conversationAi': conversationAi,
                'requestTime': datetime.now()
            }

            session["generalAi"][userId]['conversationAi'] = conversationAi
            session["generalAi"][userId]['requestTime'] = datetime.now()

        else:
            response = session["generalAi"][userId]['conversationAi'].invoke(question)
            session["generalAi"][userId]['requestTime'] = datetime.now()

        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interviewAi")
async def interview(userData: UserData):

    userId = userData.userId
    userInput = userData.userInput
    question = userData.question

    # post 요청이 들어올 때 마다 각 UserId에 대해 마지막 post요청보다 일정 시간 지날 경우 해당 userId 값 삭제
    cleanup_expired_sessions("interviewAi") 

    try:
        # 질문에 대한 응답 생성
        if userId not in session["interviewAi"]:
            conversationAi = interview_init_chain(userInput=userInput)
            response = conversationAi.invoke(question)
            session["interviewAi"][userId] = {
                'conversationAi': conversationAi,
                'requestTime': datetime.now()
            }

            session["interviewAi"][userId]['conversationAi'] = conversationAi
            session["interviewAi"][userId]['requestTime'] = datetime.now()

        else:
            response = session["interviewAi"][userId]['conversationAi'].invoke(question)
            session["interviewAi"][userId]['requestTime'] = datetime.now()

        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
