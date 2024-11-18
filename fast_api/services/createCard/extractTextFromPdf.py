import aspose.pdf as ap
import aspose.pydrawing as drawing
import fitz  # PyMuPDF

import os
import requests

def download_pdf(url):
    # PDF 다운로드
    response = requests.get(url)
    pdf_path = "downloaded_file.pdf"
    if response.status_code == 200:
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print("PDF 다운로드 완료!")
    else:
        print("PDF 다운로드 실패:", response.status_code)
    
    return pdf_path 

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    total_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        total_text += f"\n {text}"
    
    return total_text

def ocr_space_file(filename, language='kor'):
    """
    This function performs OCR on an image file using OCR.space API.
    
    :param filename: Path to the image file
    :param api_key: Your OCR.space API key (You can get it from https://ocr.space/ocrapi)
    :param language: The language code (default is 'kor' for Korean)
    :return: The extracted text from the image
    """

    api_key='7231cb8c6388957'

    with open(filename, 'rb') as f:
        img_data = f.read()

    # Set up the API request
    url = 'https://api.ocr.space/parse/image'
    headers = {'apikey': api_key}
    payload = {
        'language': language,
        'filetype': 'PNG'  # Manually specify the file type if needed (e.g., PNG, JPG)
    }
    files = {
        'file': img_data
    }

    try:
        response = requests.post(url, headers=headers, data=payload, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

    # Parse the JSON response
    result = response.json()

    if result['OCRExitCode'] == 1:
        # If OCR is successful, extract the parsed text
        return result['ParsedResults'][0]['ParsedText']
    else:
        # In case of an error
        return f"Error: {result['ErrorMessage']}"

def extract_image_from_pdf(pdf_path):

    # PDF 로드
    document = ap.Document(pdf_path)

    image_counter = 1
    image_name = "image_{counter}.png"

    total_string = ""

    # 모든 페이지 반복
    for page in document.pages:
        # 페이지의 이미지 반복
        for image in page.resources.images: 
                # 이미지를 저장할 메모리 스트림 객체 생성
                with open(image_name.format(counter=image_counter), "wb") as stream:
                    # 이미지 저장
                    image.save(stream, drawing.imaging.ImageFormat.png)
                
                img_name = f"image_{image_counter}.png"
                extracted_text = ocr_space_file(img_name)
                total_string = total_string + ' \n ' + extracted_text
                os.remove(img_name)

                image_counter = image_counter + 1
        
    return total_string


def extract_all_text_from_pdf(url):
    pdf_path = download_pdf(url)

    text = extract_text(pdf_path)
    image_text = extract_image_from_pdf(pdf_path)

    total_text = f"Text:\n{text}\n Image text:\n{image_text}"

    os.remove(pdf_path)

    return total_text