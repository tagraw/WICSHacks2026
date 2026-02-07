import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SerpService:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"

    def get_live_alerts(self, query="Austin City Limits Festival weather news"):
        """
        Fetches live alerts related to the query using SerpAPI.
        """
        if not self.api_key:
            return [{"title": "API Key Missing", "link": "#", "snippet": "Please configure SERPAPI_KEY in .env"}]

        params = {
            "q": query,
            "api_key": self.api_key,
            "tbm": "nws" # News search
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            results = response.json().get("news_results", [])

            alerts = []
            for item in results[:5]: # Return top 5
                alerts.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "date": item.get("date")
                })
            return alerts
        except Exception as e:
            print(f"Error fetching SerpAPI data: {e}")
            return [{"title": "Error fetching alerts", "link": "#", "snippet": str(e)}]
