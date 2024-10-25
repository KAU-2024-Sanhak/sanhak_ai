import os
from dotenv import load_dotenv
load_dotenv()

import time

from langchain_openai import ChatOpenAI


from operator import itemgetter
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, Runnable
from langchain_core.output_parsers import StrOutputParser


api_key = os.getenv("OPENAI_API_KEY")

def init_chain(userInput):
    
    # ChatOpenAI 모델을 초기화합니다.
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)

    # 대화 버퍼 메모리를 생성하고, 메시지 반환 기능을 활성화합니다.
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

    class MyConversationChain(Runnable):

        def __init__(self, llm, prompt, memory,input_key="input"):

            self.prompt = prompt
            self.memory = memory
            self.input_key = input_key

            self.chain = (
                RunnablePassthrough.assign(
                    chat_history=RunnableLambda(self.memory.load_memory_variables)
                    | itemgetter(memory.memory_key)  # memory_key 와 동일하게 입력합니다.
                )
                | prompt
                | llm
                | StrOutputParser()
            )

        def invoke(self, query, configs=None, **kwargs):
            answer = self.chain.invoke({self.input_key: query})
            self.memory.save_context(inputs={"human": query}, outputs={"ai": answer})
            return answer
        
        # ChatOpenAI 모델을 초기화합니다.
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)



    # 요약 메모리
    memory = ConversationSummaryMemory(
        llm=llm, return_messages=True, memory_key="chat_history"
    )

    qa_system_prompt = f""" 
            너는 질문에 답을 해줄 ai assistant야
            user의 정보와 관련있는 질문이면, user의 정보에 기반하여 답을 해줄 수도 있고,
            user의 정보와 관련없는 질문이면, user의 정보를 무시하고 답변해줘.

            - Title of the experience: {userInput.title}
            - Development tool involved: {userInput.tool} 
            - position: {userInput.position} 
            - project content : {userInput.pdfText}
            - What I felt about the experience: {userInput.reflection}

    """


    # 대화형 프롬프트를 생성합니다. 이 프롬프트는 시스템 메시지, 이전 대화 내역, 그리고 사용자 입력을 포함합니다.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    conversationAi = MyConversationChain(llm, prompt, memory)

    return conversationAi


