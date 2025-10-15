# To install: pip install tavily-python
import json
from tavily import TavilyClient


class WebSearcher:
    def __init__(self, api_key="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"):
        """
        WebSearcher 클래스 초기화
        
        Args:
            api_key (str): Tavily API 키
        """
        self.client = TavilyClient(api_key)
    
    def search(self, qrStr):
        """
        웹 검색을 수행하고 JSON 객체로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            
        Returns:
            dict: 검색 결과를 담은 JSON 객체
        """
        try:
            response = self.client.search(query=qrStr)
            return response
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "results": []
            }
    
    def search_to_json(self, qrStr):
        """
        웹 검색을 수행하고 JSON 문자열로 결과를 반환
        
        Args:
            qrStr (str): 검색할 쿼리 문자열
            
        Returns:
            str: 검색 결과를 담은 JSON 문자열
        """
        result = self.search(qrStr)
        return json.dumps(result, ensure_ascii=False, indent=2)