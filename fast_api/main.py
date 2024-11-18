from .services.createCard.createCard import generate_summary
from .services.interviewAi.interviewAi import interview_init_chain
from .services.generalAi.generalAi import general_init_chain
from .services.introduceAi.introduceAi import introduce_init_chain
from .services.languageTest.languageTest import generate_test, convert_to_dict
from .services.recommend.recommend import recommend_companies_w2v
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta


app = FastAPI()

class UserInput(BaseModel):
    title: str  # 프로젝트 제목
    tool: list[str]  # 사용한 도구들
    position: list[str]  # 역할
    reflection: str  # 느낀 점
    pdfText: str # pdf 내용

'''
채팅 입력 데이터 형태
{
    "userId" : ,
    "question" : ,
}
'''

class ChatData(BaseModel):
    userId: str  # 사용자 ID
    question: str  # 질문

'''
서버로 부터 받는 채팅 init 데이터 형태
{
    "userId" : ,
    "userInput" : {
                    "title" : ,
                    "tool" : ,
                    "position" : ,
                    "reflection" : ,
                    "pdfText" : ,
    }
    "chatModel" : "0(generalAi) or 1(interviewAi) or 2(introduceAi)" -> 0,1,2 중에 하나 받음
}
'''

class ChatInitData(BaseModel):
    userId: str 
    UserInput: UserInput
    chatModel: str


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


class CardUserInput(BaseModel):
    title: str  # 프로젝트 제목
    tool: list[str]  # 사용한 도구들
    position: list[str]  # 역할
    reflection: str  # 느낀 점
    pdfUrl: str # pdf 내용

@app.post("/createCard")
async def create_summary(cardUserInput: CardUserInput):
    """
    개발 경험 카드 요약을 생성하는 엔드포인트
    """
    
    try:
        # 요약 생성
        summary, pdfText = generate_summary(cardUserInput)

        return {"summary": summary, "pdfText" : pdfText}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
session
{
    generalAi : {
                    userId :{
                              conversationAi :,
                              requestTime : ,  
                            }
                  },
    interviewAi : {
                    userId :{
                              conversationAi :,
                              requestTime : ,  
                            }
                  },
    introduceAi : {
                    userId:{
                              conversationAi :,
                              requestTime : ,  
                            }
                  },

}
"""

session = {"generalAi" : {}, "interviewAi" : {}, "introduceAi" : {}}

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

@app.post("/initialize")
async def initialize(chatInitData: ChatInitData):
    userId = chatInitData.userId
    UserInput = chatInitData.UserInput
    chatModel = chatInitData.chatModel

    if chatModel == "0":
        generalAi = general_init_chain(userInput=UserInput)
        session["generalAi"][userId] = {
            'conversationAi' : generalAi,
            'requestTime' : datetime.now()
        }

    elif chatModel == "1":
        interviewAi = interview_init_chain(userInput=UserInput)
        session['interviewAi'][userId] = {
            'conversationAi' : interviewAi,
            'requestTime' : datetime.now()
        }
    elif chatModel == "2":
        introduceAi = introduce_init_chain(userInput=UserInput)
        session['introduceAi'][userId] = {
            "conversationAi" : introduceAi,
            "requestTime" : datetime.now()
        }

@app.post("/generalAi")
async def general(chatData: ChatData):

    userId = chatData.userId
    question = chatData.question

    # post 요청이 들어올 때 마다 각 UserId에 대해 마지막 post요청보다 일정 시간 지날 경우 해당 userId 값 삭제
    cleanup_expired_sessions("generalAi") 

    try:
        # 질문에 대한 응답 생성
        response = session["generalAi"][userId]['conversationAi'].invoke(question)
        session["generalAi"][userId]['requestTime'] = datetime.now()
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interviewAi")
async def interview(chatData: ChatData):

    userId = chatData.userId
    question = chatData.question

    # post 요청이 들어올 때 마다 각 UserId에 대해 마지막 post요청보다 일정 시간 지날 경우 해당 userId 값 삭제
    cleanup_expired_sessions("interviewAi") 

    try:
        # 질문에 대한 응답 생성
        response = session["interviewAi"][userId]['conversationAi'].invoke(question)
        session["interviewAi"][userId]['requestTime'] = datetime.now()  

        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/introduceAi")
async def introduce(chatData: ChatData):

    userId = chatData.userId
    question = chatData.question

    # post 요청이 들어올 때 마다 각 UserId에 대해 마지막 post요청보다 일정 시간 지날 경우 해당 userId 값 삭제
    cleanup_expired_sessions("introduceAi") 

    try:
        # 질문에 대한 응답 생성
        response = session["introduceAi"][userId]['conversationAi'].invoke(question)
        session["introduceAi"][userId]['requestTime'] = datetime.now()  

        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# 언어에 대한 진행도 판단의 테스트를 위한 데이터
class TestInput(BaseModel):
    language: str 
    main: str 
    sub: list 

@app.post("/createTest")
async def create_summary(testInput: TestInput):
    try:
        # 요약 생성
        questions = generate_test(testInput)
        questions = convert_to_dict(testInput=testInput, response=questions)

        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SkillInput(BaseModel):
    skills: list[str]

@app.post("/recommendCompanies")
async def recommend_companies(skill_input: SkillInput):
    try:
        recommendations = recommend_companies_w2v(skill_input.skills)
        return recommendations.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
