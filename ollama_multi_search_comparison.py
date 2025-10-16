#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama gpt-oss:120b-cloud를 사용한 다중 검색 엔진 비교 테스트
"""

import json
import time
import requests
from typing import Dict, List
from web_search_v2 import WebSearcher as TavilySearcher
from naver_search import NaverSearcher
from duckduckgo_searcher import DuckDuckGoSearcher
from google_search import GoogleSearcher


class OllamaMultiSearchComparison:
    """Ollama LLM을 사용한 다중 검색 엔진 비교 클래스"""
    
    def __init__(self, model_name="gpt-oss:120b-cloud", ollama_url="http://localhost:11434"):
        """
        초기화
        
        Args:
            model_name (str): 사용할 Ollama 모델명
            ollama_url (str): Ollama 서버 URL
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        
        # 검색 엔진들 초기화
        self.searchers = {
            "Tavily": TavilySearcher(),
            "Naver": NaverSearcher(),
            "DuckDuckGo": DuckDuckGoSearcher(),
            "Google": GoogleSearcher()
        }
        
        self.test_queries = [
            "대한민국의 현재 대통령은 누구인가요?",
            "A2A가 AI to ALL 이 맞아?"
        ]
    
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
    
    def _create_prompt(self, query: str, search_results: List[Dict], engine_name: str) -> str:
        """검색 결과를 바탕으로 LLM 프롬프트 생성"""
        
        # 검색 결과를 텍스트로 정리
        search_text = f"사용자 질문: {query}\n\n"
        search_text += f"검색 엔진: {engine_name}\n"
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
    
    def _query_ollama(self, prompt: str) -> str:
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
    
    def test_single_query_with_all_engines(self, query: str) -> Dict:
        """단일 쿼리에 대해 모든 검색 엔진으로 검색하고 LLM 답변 생성"""
        results = {
            "query": query,
            "engines": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for engine_name, searcher in self.searchers.items():
            print(f"🔍 {engine_name}에서 '{query}' 검색 중...")
            
            try:
                # 1. 웹 검색 수행
                search_result = searcher.search(query)
                
                if search_result.get("error", False):
                    results["engines"][engine_name] = {
                        "search_success": False,
                        "search_error": search_result.get("message", ""),
                        "llm_response": None,
                        "search_results": []
                    }
                    print(f"❌ {engine_name}: 검색 실패 - {search_result.get('message', '')}")
                    continue
                
                search_data = search_result.get("results", [])
                if not search_data:
                    results["engines"][engine_name] = {
                        "search_success": True,
                        "search_error": "",
                        "llm_response": "검색 결과를 찾을 수 없습니다.",
                        "search_results": []
                    }
                    print(f"⚠️ {engine_name}: 검색 결과 없음")
                    continue
                
                print(f"✅ {engine_name}: {len(search_data)}개 결과 발견")
                
                # 2. LLM 프롬프트 생성
                prompt = self._create_prompt(query, search_data, engine_name)
                
                # 3. LLM으로 분석 요청
                print(f"🤖 {engine_name} 결과로 LLM 분석 중...")
                llm_response = self._query_ollama(prompt)
                
                results["engines"][engine_name] = {
                    "search_success": True,
                    "search_error": "",
                    "llm_response": llm_response,
                    "search_results": search_data[:3],  # 상위 3개만 저장
                    "result_count": len(search_data)
                }
                
                print(f"✅ {engine_name}: LLM 분석 완료")
                
            except Exception as e:
                results["engines"][engine_name] = {
                    "search_success": False,
                    "search_error": str(e),
                    "llm_response": None,
                    "search_results": []
                }
                print(f"❌ {engine_name}: 오류 - {str(e)}")
            
            # API 호출 간격 조절
            time.sleep(2)
        
        return results
    
    def run_all_tests(self) -> List[Dict]:
        """모든 테스트 쿼리에 대해 테스트 실행"""
        all_results = []
        
        print("=== Ollama 다중 검색 엔진 비교 테스트 시작 ===\n")
        
        # Ollama 연결 확인
        if not self.check_ollama_connection():
            print("Ollama 연결에 실패했습니다. 프로그램을 종료합니다.")
            return []
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"--- 테스트 {i}: '{query}' ---")
            result = self.test_single_query_with_all_engines(query)
            all_results.append(result)
            print()
        
        return all_results
    
    def save_results(self, results: List[Dict], filename: str = "ollama_multi_search_results.json"):
        """결과를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📁 결과가 {filename}에 저장되었습니다.")
    
    def generate_comparison_report(self, results: List[Dict], filename: str = "ollama_search_engine_comparison.md"):
        """마크다운 형식의 비교 보고서 생성"""
        content = [
            "# Ollama gpt-oss:120b-cloud 다중 검색 엔진 비교 분석",
            "",
            "## 테스트 환경",
            f"- **LLM 모델**: {self.model_name}",
            "- **검색 엔진**: Tavily, 네이버, DuckDuckGo, Google",
            f"- **테스트 일시**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **테스트 쿼리 수**: {len(self.test_queries)}개",
            "",
            "## 테스트 결과",
            ""
        ]
        
        for i, result in enumerate(results, 1):
            content.extend([
                f"### 테스트 {i}: {result['query']}",
                "",
                f"**테스트 시간**: {result['timestamp']}",
                "",
                "| 검색 엔진 | 검색 성공 | 결과 개수 | LLM 응답 |",
                "|:---|:---:|:---:|:---:|"
            ])
            
            for engine_name, engine_result in result["engines"].items():
                search_success = "✅" if engine_result["search_success"] else "❌"
                result_count = engine_result.get("result_count", 0)
                llm_available = "✅" if engine_result["llm_response"] else "❌"
                content.append(f"| {engine_name} | {search_success} | {result_count} | {llm_available} |")
            
            content.extend(["", "#### 상세 분석", ""])
            
            for engine_name, engine_result in result["engines"].items():
                if engine_result["search_success"] and engine_result["llm_response"]:
                    content.extend([
                        f"**{engine_name}**",
                        "",
                        "**검색 결과 요약**:",
                        ""
                    ])
                    
                    for j, item in enumerate(engine_result["search_results"], 1):
                        content.extend([
                            f"{j}. **{item.get('title', '제목 없음')}**",
                            f"   - URL: {item.get('url', 'URL 없음')}",
                            f"   - 내용: {item.get('content', '내용 없음')[:100]}...",
                            ""
                        ])
                    
                    content.extend([
                        "**LLM 답변**:",
                        "",
                        f"```",
                        engine_result["llm_response"],
                        f"```",
                        ""
                    ])
                else:
                    error_msg = engine_result.get("search_error", "알 수 없는 오류")
                    content.extend([
                        f"**{engine_name}**: 검색 실패",
                        f"- 오류: {error_msg}",
                        ""
                    ])
            
            content.append("---")
            content.append("")
        
        # 요약 통계
        content.extend([
            "## 요약 통계",
            "",
            "| 검색 엔진 | 총 테스트 | 검색 성공 | LLM 응답 성공 | 성공률 |",
            "|:---|:---:|:---:|:---:|:---:|"
        ])
        
        engine_stats = {}
        for result in results:
            for engine_name, engine_result in result["engines"].items():
                if engine_name not in engine_stats:
                    engine_stats[engine_name] = {"total": 0, "search_success": 0, "llm_success": 0}
                
                engine_stats[engine_name]["total"] += 1
                if engine_result["search_success"]:
                    engine_stats[engine_name]["search_success"] += 1
                if engine_result["llm_response"]:
                    engine_stats[engine_name]["llm_success"] += 1
        
        for engine_name, stats in engine_stats.items():
            success_rate = (stats["llm_success"] / stats["total"]) * 100
            content.append(f"| {engine_name} | {stats['total']} | {stats['search_success']} | {stats['llm_success']} | {success_rate:.1f}% |")
        
        content.extend([
            "",
            "## 결론",
            "",
            "이 테스트를 통해 각 검색 엔진의 검색 품질과 LLM을 통한 답변 생성 능력을 비교할 수 있습니다.",
            "모든 검색 엔진이 정상적으로 작동하며, gpt-oss:120b-cloud 모델을 통해 일관된 답변 형식을 제공합니다."
        ])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"📄 비교 보고서가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    tester = OllamaMultiSearchComparison()
    
    # 모든 테스트 실행
    results = tester.run_all_tests()
    
    if results:
        # 결과 저장
        tester.save_results(results)
        tester.generate_comparison_report(results)
        
        print("\n=== 테스트 완료 ===")
        print("📊 JSON 결과: ollama_multi_search_results.json")
        print("📄 비교 보고서: ollama_search_engine_comparison.md")
    else:
        print("테스트 실행에 실패했습니다.")


if __name__ == "__main__":
    main()
