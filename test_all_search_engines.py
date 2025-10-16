#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 검색 엔진 (Tavily, 네이버, DuckDuckGo, Google) 테스트 스크립트
"""

import json
import time
from typing import Dict, List
from web_search_v2 import WebSearcher as TavilySearcher
from naver_search import NaverSearcher
from duckduckgo_searcher import DuckDuckGoSearcher
from google_search import GoogleSearcher


class MultiSearchEngineTester:
    """다중 검색 엔진 테스트 클래스"""
    
    def __init__(self):
        """검색 엔진들 초기화"""
        self.searchers = {
            "Tavily": TavilySearcher(),
            "Naver": NaverSearcher(),  # API 키 필요
            "DuckDuckGo": DuckDuckGoSearcher(),
            "Google": GoogleSearcher()  # API 키 필요
        }
        
        self.test_queries = [
            "대한민국의 현재 대통령은 누구인가요?",
            "A2A가 AI to ALL 이 맞아?"
        ]
    
    def test_single_query(self, query: str) -> Dict:
        """단일 쿼리에 대해 모든 검색 엔진 테스트"""
        results = {
            "query": query,
            "engines": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for engine_name, searcher in self.searchers.items():
            print(f"🔍 {engine_name}에서 '{query}' 검색 중...")
            
            try:
                search_result = searcher.search(query)
                results["engines"][engine_name] = {
                    "success": not search_result.get("error", False),
                    "result_count": len(search_result.get("results", [])),
                    "error_message": search_result.get("message", "") if search_result.get("error", False) else "",
                    "results": search_result.get("results", [])[:3]  # 상위 3개만 저장
                }
                
                if results["engines"][engine_name]["success"]:
                    print(f"✅ {engine_name}: {results['engines'][engine_name]['result_count']}개 결과")
                else:
                    print(f"❌ {engine_name}: {results['engines'][engine_name]['error_message']}")
                    
            except Exception as e:
                results["engines"][engine_name] = {
                    "success": False,
                    "result_count": 0,
                    "error_message": str(e),
                    "results": []
                }
                print(f"❌ {engine_name}: {str(e)}")
            
            # API 호출 간격 조절
            time.sleep(1)
        
        return results
    
    def run_all_tests(self) -> List[Dict]:
        """모든 테스트 쿼리에 대해 테스트 실행"""
        all_results = []
        
        print("=== 다중 검색 엔진 테스트 시작 ===\n")
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"--- 테스트 {i}: '{query}' ---")
            result = self.test_single_query(query)
            all_results.append(result)
            print()
        
        return all_results
    
    def save_results(self, results: List[Dict], filename: str = "multi_search_results.json"):
        """결과를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📁 결과가 {filename}에 저장되었습니다.")
    
    def generate_markdown_report(self, results: List[Dict], filename: str = "multi_search_report.md"):
        """마크다운 형식의 보고서 생성"""
        content = [
            "# 다중 검색 엔진 테스트 결과",
            "",
            "## 테스트 환경",
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
                "| 검색 엔진 | 성공 여부 | 결과 개수 | 오류 메시지 |",
                "|:---|:---:|:---:|:---|"
            ])
            
            for engine_name, engine_result in result["engines"].items():
                success = "✅" if engine_result["success"] else "❌"
                count = engine_result["result_count"]
                error = engine_result["error_message"] if engine_result["error_message"] else "-"
                content.append(f"| {engine_name} | {success} | {count} | {error} |")
            
            content.extend(["", "#### 상세 결과", ""])
            
            for engine_name, engine_result in result["engines"].items():
                if engine_result["success"] and engine_result["results"]:
                    content.extend([
                        f"**{engine_name}**",
                        ""
                    ])
                    
                    for j, item in enumerate(engine_result["results"], 1):
                        content.extend([
                            f"{j}. **{item.get('title', '제목 없음')}**",
                            f"   - URL: {item.get('url', 'URL 없음')}",
                            f"   - 내용: {item.get('content', '내용 없음')[:100]}...",
                            ""
                        ])
                else:
                    content.extend([
                        f"**{engine_name}**: 결과 없음",
                        ""
                    ])
            
            content.append("---")
            content.append("")
        
        # 요약 통계
        content.extend([
            "## 요약 통계",
            "",
            "| 검색 엔진 | 총 테스트 | 성공 | 실패 | 성공률 |",
            "|:---|:---:|:---:|:---:|:---:|"
        ])
        
        engine_stats = {}
        for result in results:
            for engine_name, engine_result in result["engines"].items():
                if engine_name not in engine_stats:
                    engine_stats[engine_name] = {"total": 0, "success": 0, "fail": 0}
                
                engine_stats[engine_name]["total"] += 1
                if engine_result["success"]:
                    engine_stats[engine_name]["success"] += 1
                else:
                    engine_stats[engine_name]["fail"] += 1
        
        for engine_name, stats in engine_stats.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            content.append(f"| {engine_name} | {stats['total']} | {stats['success']} | {stats['fail']} | {success_rate:.1f}% |")
        
        content.extend([
            "",
            "## 결론",
            "",
            "이 테스트를 통해 각 검색 엔진의 성능과 결과 품질을 비교할 수 있습니다.",
            "API 키가 필요한 검색 엔진의 경우 적절한 설정이 필요합니다."
        ])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"📄 마크다운 보고서가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    tester = MultiSearchEngineTester()
    
    # 모든 테스트 실행
    results = tester.run_all_tests()
    
    # 결과 저장
    tester.save_results(results)
    tester.generate_markdown_report(results)
    
    print("\n=== 테스트 완료 ===")
    print("📊 JSON 결과: multi_search_results.json")
    print("📄 마크다운 보고서: multi_search_report.md")


if __name__ == "__main__":
    main()
