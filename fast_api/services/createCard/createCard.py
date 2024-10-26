import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(userInput):
    """
    사용자 입력과 PDF 내용을 기반으로 OpenAI API를 사용하여 요약을 생성하는 함수
    """
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    # 프롬프트 생성
    system_prompt = f"""
    you create a summary of a development experience card.
    I want you to create a summary of a development experience card. The details are as follows:
    - Title of the experience: {userInput.title}
    - Development tool involved: {userInput.tool}
    - Position: {userInput.position}
    - What I felt about the experience: {userInput.reflection}
    - Additional experience data from PDF: {userInput.pdfText}
    """



    # 대화형 프롬프트를 생성합니다. 이 프롬프트는 시스템 메시지, 이전 대화 내역, 그리고 사용자 입력을 포함합니다.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    request = """
    Please Summarize with emphasis on the function and position of the project
        and organize it in one paragraph to help with the self-introduction letter
        and answer in a soft tone so that the context of the sentence is naturally connected
        and answer Korean and Please write about 300 bytes
    """

    chain = prompt | llm | StrOutputParser()


    # OpenAI API 호출
    response = chain.invoke(request)


    return response
