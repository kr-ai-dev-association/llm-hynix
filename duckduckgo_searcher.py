# To install: pip install duckduckgo-search
import json
from typing import Dict, List
from duckduckgo_search import DDGS


class DuckDuckGoSearcher:
    """DuckDuckGo 검색 API를 사용한 웹 검색 클래스"""
    
    def __init__(self):
        """
        DuckDuckGo 검색 API 클래스 초기화
        """
        self.ddgs = DDGS()
        
    def search(self, qrStr: str, max_results: int = 10) -> Dict:
        """
        DuckDuckGo 웹 검색을 수행하고 JSON 객체로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            max_results (int): 최대 검색 결과 개수 (기본값: 10)
            
        Returns:
            dict: 검색 결과를 담은 JSON 객체
        """
        try:
            results = []
            
            # DuckDuckGo 검색 실행
            search_results = self.ddgs.text(qrStr, max_results=max_results)
            
            for item in search_results:
                results.append({
                    "title": item.get('title', ''),
                    "url": item.get('href', ''),
                    "content": item.get('body', ''),
                    "score": 1.0  # DuckDuckGo는 점수를 제공하지 않으므로 기본값
                })
            
            return {
                "query": qrStr,
                "results": results,
                "total": len(results),
                "error": False
            }
                
        except Exception as e:
            return {
                "error": True,
                "message": f"DuckDuckGo 검색 오류: {str(e)}",
                "results": []
            }
    
    def search_to_json(self, qrStr: str) -> str:
        """
        DuckDuckGo 웹 검색을 수행하고 JSON 문자열로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            
        Returns:
            str: 검색 결과를 담은 JSON 문자열
        """
        result = self.search(qrStr)
        return json.dumps(result, ensure_ascii=False, indent=2)
