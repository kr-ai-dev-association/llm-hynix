#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSearcher 클래스와 Ollama LLM을 연동한 웹 검색 및 답변 생성 시스템
"""

from web_search_v2 import WebSearcher
import json
import requests
import time


def test_web_searcher():
    """WebSearcher 클래스의 기능을 테스트하는 함수"""
    
    print("=== WebSearcher 클래스 테스트 시작 ===\n")
    
    # WebSearcher 인스턴스 생성
    searcher = WebSearcher()
    
    # 테스트 쿼리들
    test_queries = [
        "대한민국의 현재 대통령은 누구지?",
        "A2A가 AI to ALL 이 맞아?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"--- 테스트 {i}: '{query}' 검색 ---")
        
        # JSON 객체로 결과 받기
        print("1. JSON 객체로 결과 받기:")
        result_dict = searcher.search(query)
        print(f"   결과 타입: {type(result_dict)}")
        print(f"   에러 여부: {result_dict.get('error', False)}")
        
        if not result_dict.get('error', False):
            print(f"   검색 결과 개수: {len(result_dict.get('results', []))}")
            if result_dict.get('results'):
                first_result = result_dict['results'][0]
                print(f"   첫 번째 결과 제목: {first_result.get('title', 'N/A')}")
                print(f"   첫 번째 결과 URL: {first_result.get('url', 'N/A')}")
        else:
            print(f"   에러 메시지: {result_dict.get('message', 'N/A')}")
        
        print()
        
        # JSON 문자열로 결과 받기
        print("2. JSON 문자열로 결과 받기:")
        result_json = searcher.search_to_json(query)
        print(f"   결과 타입: {type(result_json)}")
        print(f"   JSON 길이: {len(result_json)} 문자")
        print(f"   JSON 미리보기 (처음 200자): {result_json[:200]}...")
        
        print("\n" + "="*50 + "\n")


def test_error_handling():
    """에러 처리 테스트"""
    print("=== 에러 처리 테스트 ===\n")
    
    # 잘못된 API 키로 테스트
    print("1. 잘못된 API 키로 테스트:")
    bad_searcher = WebSearcher("invalid-api-key")
    result = bad_searcher.search("test query")
    print(f"   에러 여부: {result.get('error', False)}")
    print(f"   에러 메시지: {result.get('message', 'N/A')}")
    
    print("\n2. 빈 쿼리로 테스트:")
    searcher = WebSearcher()
    result = searcher.search("")
    print(f"   에러 여부: {result.get('error', False)}")
    print(f"   결과: {result}")
    
    print("\n" + "="*50 + "\n")


def interactive_test():
    """사용자 입력을 받아서 대화형 테스트"""
    print("=== 대화형 테스트 ===\n")
    print("검색할 키워드를 입력하세요 (종료하려면 'quit' 입력):")
    
    searcher = WebSearcher()
    
    while True:
        query = input("\n검색어: ").strip()
        
        if query.lower() in ['quit', 'exit', '종료']:
            print("테스트를 종료합니다.")
            break
        
        if not query:
            print("검색어를 입력해주세요.")
            continue
        
        print(f"\n'{query}' 검색 중...")
        result = searcher.search(query)
        
        if result.get('error', False):
            print(f"에러 발생: {result.get('message', 'N/A')}")
        else:
            results = result.get('results', [])
            print(f"검색 결과 {len(results)}개:")
            
            for i, item in enumerate(results[:3], 1):  # 상위 3개만 표시
                print(f"  {i}. {item.get('title', 'N/A')}")
                print(f"     URL: {item.get('url', 'N/A')}")
                print(f"     내용: {item.get('content', 'N/A')[:100]}...")
                print()


class OllamaWebSearchAssistant:
    """Ollama LLM과 웹 검색을 연동한 AI 어시스턴트"""
    
    def __init__(self, model_name="gpt-oss:120b-cloud", ollama_url="http://localhost:11434"):
        """
        초기화
        
        Args:
            model_name (str): 사용할 Ollama 모델명
            ollama_url (str): Ollama 서버 URL
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.web_searcher = WebSearcher()
        
    def check_ollama_connection(self):
        """Ollama 서버 연결 확인"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if self.model_name in model_names:
                    print(f"✅ Ollama 연결 성공: {self.model_name} 모델 사용 가능")
                    return True
                else:
                    print(f"❌ 모델 {self.model_name}을 찾을 수 없습니다.")
                    print(f"사용 가능한 모델: {model_names}")
                    return False
            else:
                print(f"❌ Ollama 서버 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ollama 서버 연결 오류: {e}")
            return False
    
    def search_and_analyze(self, query):
        """
        웹 검색을 수행하고 LLM으로 결과를 분석하여 답변 생성
        
        Args:
            query (str): 사용자 질의
            
        Returns:
            dict: 검색 결과와 LLM 분석 결과
        """
        print(f"\n🔍 '{query}' 검색 중...")
        
        # 1. 웹 검색 수행
        search_result = self.web_searcher.search(query)
        
        if search_result.get('error', False):
            return {
                "query": query,
                "search_error": True,
                "error_message": search_result.get('message', 'Unknown error'),
                "llm_response": None
            }
        
        # 2. 검색 결과를 LLM 프롬프트로 구성
        search_data = search_result.get('results', [])
        if not search_data:
            return {
                "query": query,
                "search_error": False,
                "search_results": [],
                "llm_response": "검색 결과를 찾을 수 없습니다."
            }
        
        # 3. LLM에게 전달할 프롬프트 구성
        prompt = self._create_prompt(query, search_data)
        
        # 4. LLM으로 분석 요청
        print("🤖 LLM 분석 중...")
        llm_response = self._query_ollama(prompt)
        
        return {
            "query": query,
            "search_error": False,
            "search_results": search_data,
            "llm_response": llm_response,
            "raw_search_data": search_result
        }
    
    def _create_prompt(self, query, search_results):
        """검색 결과를 바탕으로 LLM 프롬프트 생성"""
        
        # 검색 결과를 텍스트로 정리
        search_text = f"사용자 질문: {query}\n\n"
        search_text += "웹 검색 결과:\n"
        
        for i, result in enumerate(search_results[:5], 1):  # 상위 5개만 사용
            title = result.get('title', '제목 없음')
            content = result.get('content', '내용 없음')
            url = result.get('url', 'URL 없음')
            
            search_text += f"\n{i}. 제목: {title}\n"
            search_text += f"   내용: {content[:500]}...\n"  # 내용은 500자로 제한
            search_text += f"   출처: {url}\n"
        
        prompt = f"""당신은 웹 검색 결과를 바탕으로 사용자의 질문에 정확하고 유용한 답변을 제공하는 AI 어시스턴트입니다.

{search_text}

위의 웹 검색 결과를 바탕으로 사용자의 질문에 대해 다음 형식으로 답변해주세요:

1. **핵심 답변**: 질문에 대한 직접적이고 명확한 답변
2. **상세 설명**: 답변의 근거와 추가 정보
3. **참고 자료**: 답변에 사용된 검색 결과의 출처

답변은 한국어로 작성하고, 검색 결과에 기반한 사실적이고 정확한 정보를 제공해주세요. 만약 검색 결과로 질문에 답할 수 없다면 솔직하게 그렇게 말해주세요."""

        return prompt
    
    def _query_ollama(self, prompt):
        """Ollama API를 통해 LLM에 질의"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 2000
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '응답을 생성할 수 없습니다.')
            else:
                return f"LLM 요청 실패: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"LLM 요청 오류: {str(e)}"
    
    def single_query(self, query):
        """단일 질의 처리"""
        print("=== Ollama 웹 검색 AI 어시스턴트 ===\n")
        
        if not self.check_ollama_connection():
            print("Ollama 연결에 실패했습니다. 프로그램을 종료합니다.")
            return
        
        if not query or not query.strip():
            print("질문을 입력해주세요.")
            return
        
        # 검색 및 분석 수행
        result = self.search_and_analyze(query.strip())
        
        # 결과 출력
        self._display_result(result)
    
    def _display_result(self, result):
        """검색 및 분석 결과를 사용자에게 표시"""
        print("\n" + "="*60)
        print(f"📝 질문: {result['query']}")
        print("="*60)
        
        if result.get('search_error', False):
            print(f"❌ 검색 오류: {result.get('error_message', 'Unknown error')}")
            return
        
        # 검색 결과 요약
        search_results = result.get('search_results', [])
        print(f"🔍 검색 결과: {len(search_results)}개 발견")
        
        # LLM 응답
        llm_response = result.get('llm_response', '응답을 생성할 수 없습니다.')
        print(f"\n🤖 AI 답변:\n{llm_response}")
        
        # 참고 자료
        if search_results:
            print(f"\n📚 참고 자료:")
            for i, item in enumerate(search_results[:3], 1):
                title = item.get('title', '제목 없음')
                url = item.get('url', 'URL 없음')
                print(f"  {i}. {title}")
                print(f"     {url}")
        
        print("\n" + "="*60 + "\n")


def test_ollama_integration():
    """Ollama 연동 테스트"""
    print("=== Ollama 연동 테스트 ===\n")
    
    assistant = OllamaWebSearchAssistant()
    
    # 연결 테스트
    if not assistant.check_ollama_connection():
        return
    
    # 테스트 쿼리들
    test_queries = [
        "대한민국의 현재 대통령은 누구인가요?",
        "A2A 프로토콜이 무엇인가요?",
        "2024년 AI 기술 동향은 어떤가요?"
    ]
    
    for query in test_queries:
        print(f"\n--- 테스트: '{query}' ---")
        result = assistant.search_and_analyze(query)
        assistant._display_result(result)
        time.sleep(2)  # API 호출 간격 조절


if __name__ == "__main__":
    import sys
    
    try:
        # 명령행 인수로 질의를 받음
        if len(sys.argv) > 1:
            # 명령행에서 질의를 받은 경우
            query = " ".join(sys.argv[1:])
            assistant = OllamaWebSearchAssistant()
            assistant.single_query(query)
        else:
            # 사용자 선택 모드
            print("Ollama 웹 검색 AI 어시스턴트를 시작합니다...\n")
            print("실행할 모드를 선택하세요:")
            print("1. 기본 테스트 (기존 WebSearcher 테스트)")
            print("2. Ollama 연동 테스트")
            print("3. 단일 질의 (Ollama + 웹 검색)")
            print("4. 기존 대화형 테스트")
            
            choice = input("\n선택 (1-4): ").strip()
            
            if choice == "1":
                test_web_searcher()
                test_error_handling()
            elif choice == "2":
                test_ollama_integration()
            elif choice == "3":
                query = input("질문을 입력하세요: ").strip()
                assistant = OllamaWebSearchAssistant()
                assistant.single_query(query)
            elif choice == "4":
                interactive_test()
            else:
                print("잘못된 선택입니다. 단일 질의 모드를 시작합니다.")
                query = input("질문을 입력하세요: ").strip()
                assistant = OllamaWebSearchAssistant()
                assistant.single_query(query)
        
        print("\n프로그램이 종료되었습니다.")
        
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
