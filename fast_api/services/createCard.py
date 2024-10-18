import os
import openai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import textwrap
from io import BytesIO

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_file):
    """
    PDF 파일에서 텍스트를 추출하는 함수
    """
    try:
        # 파일을 바이트로 읽어서 BytesIO로 감싼다.
        pdf_bytes = pdf_file.file.read()
        reader = PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        raise e

def generate_summary(user_input):
    """
    사용자 입력과 PDF 내용을 기반으로 OpenAI API를 사용하여 요약을 생성하는 함수
    """
    # PDF에서 추가 데이터 추출
    pdf_content = extract_text_from_pdf(user_input['pdf_file'])
    
    # 프롬프트 생성
    prompt = f"""
    I want you to create a summary of a development experience card. The details are as follows:
    - Title of the experience: {user_input['title']}
    - Development tools involved: {', '.join(user_input['tools'])}
    - Position: {', '.join(user_input['position'])}
    - What I felt about the experience: {user_input['reflection']}
    - Additional experience data from PDF: {pdf_content}
    
    Please Summarize with emphasis on the function and position of the project
        and organize it in one paragraph to help with the self-introduction letter
        and answer in a soft tone so that the context of the sentence is naturally connected
        and answer Korean and Please write about 300 bytes
    """

    # 메시지 컨텍스트 설정
    context = [
        {
            'role': 'system',
            'content': "you create a summary of a development experience card."
        },
        {
            'role': 'user',
            'content': prompt
        }
    ]

    # OpenAI API 호출
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=context,
        temperature=0
    )

    summary = response.choices[0].message["content"]
    
    # 텍스트 래핑
    wrapper = textwrap.TextWrapper(width=70, break_long_words=False, replace_whitespace=False)
    wrapped_text = wrapper.fill(text=summary)

    return wrapped_text
