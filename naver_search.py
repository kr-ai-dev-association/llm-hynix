# To install: pip install requests
import json
import requests
from typing import Dict, List, Optional


class NaverSearcher:
    """네이버 검색 API를 사용한 웹 검색 클래스"""
    
    def __init__(self, client_id: str = "pURdWVQAu4a6a1E_ZE90", client_secret: str = "o04UV4VfZo"):
        """
        네이버 검색 API 클래스 초기화
        
        Args:
            client_id (str): 네이버 API 클라이언트 ID
            client_secret (str): 네이버 API 클라이언트 시크릿
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/webkr.json"
        
    def search(self, qrStr: str, display: int = 10) -> Dict:
        """
        네이버 웹 검색을 수행하고 JSON 객체로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            display (int): 검색 결과 개수 (기본값: 10)
            
        Returns:
            dict: 검색 결과를 담은 JSON 객체
        """
        try:
            if not self.client_id or not self.client_secret:
                return {
                    "error": True,
                    "message": "네이버 API 클라이언트 ID와 시크릿이 필요합니다.",
                    "results": []
                }
            
            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }
            
            params = {
                "query": qrStr,
                "display": display,
                "start": 1,
                "sort": "sim"
            }
            
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        "title": item.get('title', '').replace('<b>', '').replace('</b>', ''),
                        "url": item.get('link', ''),
                        "content": item.get('description', '').replace('<b>', '').replace('</b>', ''),
                        "score": 1.0  # 네이버는 점수를 제공하지 않으므로 기본값
                    })
                
                return {
                    "query": qrStr,
                    "results": results,
                    "total": data.get('total', 0),
                    "error": False
                }
            else:
                return {
                    "error": True,
                    "message": f"네이버 API 요청 실패: {response.status_code}",
                    "results": []
                }
                
        except Exception as e:
            return {
                "error": True,
                "message": f"네이버 검색 오류: {str(e)}",
                "results": []
            }
    
    def search_to_json(self, qrStr: str) -> str:
        """
        네이버 웹 검색을 수행하고 JSON 문자열로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            
        Returns:
            str: 검색 결과를 담은 JSON 문자열
        """
        result = self.search(qrStr)
        return json.dumps(result, ensure_ascii=False, indent=2)
