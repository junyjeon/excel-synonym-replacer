from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일 불러오기
load_dotenv()

# OpenAI 클라이언트 생성
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 간단한 테스트
try:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "안녕하세요"}
        ]
    )
    print("응답:", completion.choices[0].message.content)
except Exception as e:
    print("오류 발생:", e)