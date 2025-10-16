# To install: pip install google-search-results
import json
from typing import Dict, List
from serpapi import GoogleSearch


class GoogleSearcher:
    """Google Search API를 사용한 웹 검색 클래스"""
    
    def __init__(self, api_key: str = ""):
        """
        Google Search API 클래스 초기화
        
        Args:
            api_key (str): SerpAPI API 키
        """
        self.api_key = api_key
        
    def search(self, qrStr: str, num_results: int = 10) -> Dict:
        """
        Google 웹 검색을 수행하고 JSON 객체로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            num_results (int): 검색 결과 개수 (기본값: 10)
            
        Returns:
            dict: 검색 결과를 담은 JSON 객체
        """
        try:
            if not self.api_key:
                return {
                    "error": True,
                    "message": "Google Search API 키가 필요합니다.",
                    "results": []
                }
            
            params = {
                "q": qrStr,
                "api_key": self.api_key,
                "num": num_results,
                "gl": "kr",  # 한국 검색 결과
                "hl": "ko"   # 한국어 인터페이스
            }
            
            search = GoogleSearch(params)
            results_data = search.get_dict()
            
            results = []
            
            if "organic_results" in results_data:
                for item in results_data["organic_results"]:
                    results.append({
                        "title": item.get('title', ''),
                        "url": item.get('link', ''),
                        "content": item.get('snippet', ''),
                        "score": 1.0  # Google은 점수를 제공하지 않으므로 기본값
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
                "message": f"Google 검색 오류: {str(e)}",
                "results": []
            }
    
    def search_to_json(self, qrStr: str) -> str:
        """
        Google 웹 검색을 수행하고 JSON 문자열로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            
        Returns:
            str: 검색 결과를 담은 JSON 문자열
        """
        result = self.search(qrStr)
        return json.dumps(result, ensure_ascii=False, indent=2)
