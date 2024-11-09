import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def generate_test(testInput):
    """
    사용자 입력과 PDF 내용을 기반으로 OpenAI API를 사용하여 요약을 생성하는 함수
    """
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    # 프롬프트 생성
    system_prompt = f"""
    너는 주어진 언어와 해당 언어에서 공부한 부분에 관해서만 객관식 문제와 답변을 생성해주는 ai assistant야.
    언어와 main 목차와 그에 대한 세부 목차는 다음과 같애.
    
    - language: {testInput.language}
    - main 목차: {testInput.main}
    - 세부 목차: {testInput.sub}
    """



    # 대화형 프롬프트를 생성합니다. 이 프롬프트는 시스템 메시지, 이전 대화 내역, 그리고 사용자 입력을 포함합니다.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    
    request = """
    주어진 언어와 주 목차, 세부 목차에 해당하는 객관식 문제 총 1개와 해당 답변을 만들어줘.
    각 객관식은 4개의 선택지로 구성되어 있어야 해. answer는 options의 번호로 해줘.
    답변 자체를 바로 dictionary 형식으로 변환 가능하도록 해줘. 즉, json 이런 단어는 포함안되도록 해줘.

    {
        "question": "",
        "options": [],
        "answer": 
    }
    """

    chain = prompt | llm | StrOutputParser()


    # OpenAI API 호출
    response = chain.invoke(request)

    return response

def convert_to_dict(testInput, response):
    while True:
        try:
            converted_dict = json.loads(response)
            if isinstance(converted_dict, dict):
                return converted_dict
            else:
                raise Exception
            
        except Exception as e:
            response = generate_test(testInput=testInput) 