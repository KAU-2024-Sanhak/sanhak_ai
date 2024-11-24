import fitz  # PyMuPDF
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


def download_pdf(url):
    """
    URL에서 PDF 파일 다운로드
    """
    response = requests.get(url)
    pdf_path = "downloaded_file.pdf"
    if response.status_code == 200:
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print("PDF 다운로드 완료!")
    else:
        raise Exception(f"PDF 다운로드 실패: {response.status_code}")
    return pdf_path


def extract_text_from_pdf(pdf_path):
    """
    PDF에서 텍스트 추출 (PyMuPDF 사용)
    """
    doc = fitz.open(pdf_path)
    total_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        total_text += f"\n{text}"
    return total_text


def extract_images_from_pdf(pdf_path):
    """
    PDF에서 이미지를 추출 (PyMuPDF 사용)
    """
    doc = fitz.open(pdf_path)
    image_counter = 1
    extracted_images = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page{page_number+1}_img{img_index+1}.{image_ext}"

            with open(image_filename, "wb") as f:
                f.write(image_bytes)
            print(f"이미지 저장 완료: {image_filename}")
            extracted_images.append(image_filename)
    
    return extracted_images


def ocr_google_api(image_path):
    """
    Google Vision API를 사용하여 이미지에서 텍스트 추출
    """
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "requests": [
            {
                "image": {"content": base64_image},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        if "textAnnotations" in response_data["responses"][0]:
            return response_data["responses"][0]["textAnnotations"][0]["description"]
        else:
            return "No text found in image."
    else:
        raise Exception(f"API Error: {response.status_code}, {response.text}")


def extract_all_text_from_pdf(url, use_ocr=True):
    """
    PDF URL에서 텍스트 및 이미지 기반 OCR 수행
    """
    try:
        pdf_path = download_pdf(url)
        text = extract_text_from_pdf(pdf_path)
        image_text = ""

        if use_ocr:
            extracted_images = extract_images_from_pdf(pdf_path)
            for image in extracted_images:
                try:
                    image_text += f"\n{ocr_google_api(image)}"
                    os.remove(image)  # 처리 후 임시 이미지 파일 삭제
                except Exception as e:
                    print(f"이미지 처리 실패: {e}")
                    continue

        # PDF 파일 삭제
        os.remove(pdf_path)

        total_text = f"Text:\n{text}\nImage text:\n{image_text}"
        return total_text

    except Exception as e:
        return f"오류 발생: {e}"