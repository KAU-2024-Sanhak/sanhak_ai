import pandas as pd
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# CSV 파일 로드
data = pd.read_csv("/home/boseung/24-2/cooperative/sanhak_ai/fast_api/services/recommend/company_data.csv")
data['skills_text'] = data['extracted_skills'].fillna("").apply(lambda x: x.split(", "))

# Word2Vec 모델 학습
w2v_model = Word2Vec(sentences=data['skills_text'], vector_size=100, window=5, min_count=1, sg=1)

# 각 기업 스킬 임베딩 벡터 계산
def get_company_vector(skills):
    skill_vectors = [w2v_model.wv[skill] for skill in skills if skill in w2v_model.wv]
    if skill_vectors:
        return np.mean(skill_vectors, axis=0)
    else:
        return np.zeros(w2v_model.vector_size)

data['company_vector'] = data['skills_text'].apply(get_company_vector)

# 추천 함수 정의
def recommend_companies_w2v(user_skills):
    user_vector = get_company_vector(user_skills)
    
    # 코사인 유사도 계산
    data['similarity'] = data['company_vector'].apply(lambda x: cosine_similarity([user_vector], [x]).item())
    
    # 유사도가 높은 기업 추천
    recommendations = data.sort_values(by='similarity', ascending=False)[['company_names', 'result', 'extracted_skills', 'similarity']]
    return recommendations.head(5)

# 예시: 사용자의 스킬을 입력
user_skills = ['tensorflow']
recommended_companies = recommend_companies_w2v(user_skills)
print(recommended_companies)
