import os
from dotenv import load_dotenv
load_dotenv()

import time
from pypdf import PdfReader

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'  
    return text



try:
    pdf_path = '/Users/user/Desktop/2024 2학기/산학/chatbot/종합설계 _최종발표자료.pdf'  
    pdf_content = extract_text_from_pdf(pdf_path)
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(pdf_content) 
    
    chroma_db = Chroma.from_texts(texts, embeddings)
    retriever = chroma_db.as_retriever(search_type="mmr", search_kwargs={'k': 3, 'fetch_k': 7})
    
    chat = ChatOpenAI(model="gpt-4o")
 
    contextualize_q_system_prompt = """
    이전 대화 내용과 최신 사용자 질문이 있을 때, 이 질문이 이전 대화 내용과 관련이 있을 수 있습니다. 
    이런 경우 대화 내용을 보고 답변을 하고, 이전 대화 내용과 관련 없을 경우, 새로운 질문으로 판단하고 답변하세요.
    """

    # MessagesPlaceholder: 'chat_history' 입력 키를 사용하여 이전 메세지 기록들을 프롬프트에 포함
    # 프롬프트, 메세지 기록 (문맥 정보), 사용자의 질문으로 프롬프트가 구성
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    # 이를 토대로 메세지 기록을 기억하는 retriever를 생성합니다.
    history_aware_retriever = create_history_aware_retriever(
        chat, retriever, contextualize_q_prompt
    )

    # 방금 전 생성한 체인을 사용하여 문서를 불러올 수 있는 retriever 체인을 생성합니다.

    qa_system_prompt = """ 
        너는 신입 개발자들의 면접을 돕는 AI 면접관이야. 
        Use what you find to answer your questions. 
        If you don't know the answer, say you don't know. 
        The user's information is as follows.

        - Title of the experience: Dog inscription search service from distributed DB using blockchain 
        - Development field: ['backend', 'application'] 
        - Development language: ['kotlin', 'python'] 
        - Development tools involved: ['android studio', 'flask', 'AWS', 'ubuntu'] 
        - project content : {context}
        - What I felt about the experience: I became interested in development, and collaboration with team members was easy.

        - As a interviewer, please answer in the tone you use during the interview.

        ## 답변 예시
        답변 내용: 
"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)

    # 결과값은 input, chat_history, context, answer 
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

except Exception as e:
   print(e)

        
# 프롬프트 비용 문제를 감안해 일단 대화 4번까지 기억하게 해놓음
MAX_MESSAGES_BEFORE_DELETION = 8
messages = []

print()
print("AI 면접관 입니다. 무엇이든 물어보세요.")
print()

while True:
    prompt = input("User : ")

    if prompt == "0":
        break
    

    # 만약 현재 저장된 대화 내용 기록이 4개보다 많으면 자르기
    if len(messages) >= MAX_MESSAGES_BEFORE_DELETION:
        # Remove the first two messages
        del messages[0]
        del messages[0]  
   
    full_response = ""
    messages.append({"role": "user", "content": prompt})
    result = rag_chain.invoke({"input": prompt, "chat_history": messages})

    print()
    print("AI : ")
    for chunk in result["answer"].split(" "):
        full_response += chunk + " "
        time.sleep(0.2)
        print(chunk, end=" ")
    messages.append({"role": "assistant", "content": full_response})
    print()
    print("____________________________________________________")
    print()
    
