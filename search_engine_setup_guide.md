# 검색 엔진 API 설정 가이드

## 1. 네이버 검색 API

### API 키 발급 방법
1. [네이버 개발자 센터](https://developers.naver.com/) 접속
2. 로그인 후 "Application" → "애플리케이션 등록" 클릭
3. 애플리케이션 정보 입력:
   - 애플리케이션 이름: 원하는 이름
   - 사용 API: "검색" 선택
   - 환경 추가: "WEB" 선택
   - 서비스 환경: "http://localhost" 입력
4. 등록 완료 후 Client ID와 Client Secret 확인

### 사용 방법
```python
from naver_search import NaverSearcher

# API 키 설정
searcher = NaverSearcher(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)

# 검색 실행
result = searcher.search("검색어")
```

## 2. Google Search API (SerpAPI)

### API 키 발급 방법
1. [SerpAPI](https://serpapi.com/) 접속
2. 회원가입 후 로그인
3. Dashboard에서 API Key 확인
4. 무료 플랜: 월 100회 검색 제한

### 사용 방법
```python
from google_search import GoogleSearcher

# API 키 설정
searcher = GoogleSearcher(api_key="YOUR_API_KEY")

# 검색 실행
result = searcher.search("검색어")
```

## 3. Tavily API (이미 설정됨)

### 현재 설정
- API Key: `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`
- 무료 플랜: 월 1,000회 검색 제한

## 4. DuckDuckGo (API 키 불필요)

### 특징
- API 키 불필요
- 무료 사용 가능
- 한국어 검색 결과 품질이 상대적으로 낮음

## 테스트 실행 방법

### 1. API 키 설정 후 테스트
```bash
# 가상환경 활성화
source venv/bin/activate

# 전체 검색 엔진 테스트 실행
python test_all_search_engines.py
```

### 2. 개별 검색 엔진 테스트
```python
# Tavily 테스트
from web_search_v2 import WebSearcher
searcher = WebSearcher()
result = searcher.search("테스트 쿼리")

# DuckDuckGo 테스트
from duckduckgo_searcher import DuckDuckGoSearcher
searcher = DuckDuckGoSearcher()
result = searcher.search("테스트 쿼리")
```

## 검색 엔진별 특징 비교

| 검색 엔진 | API 키 필요 | 무료 제한 | 한국어 지원 | 결과 품질 |
|:---|:---:|:---:|:---:|:---:|
| Tavily | ✅ | 1,000회/월 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 네이버 | ✅ | 25,000회/일 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| DuckDuckGo | ❌ | 무제한 | ⭐⭐ | ⭐⭐ |
| Google | ✅ | 100회/월 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 권장사항

1. **한국어 검색**: 네이버 API 사용 권장
2. **영어 검색**: Google Search API 또는 Tavily 사용 권장
3. **무료 테스트**: DuckDuckGo 사용 (품질 제한 있음)
4. **상용 서비스**: 네이버 + Google 조합 사용 권장
