from openai import OpenAI
import requests
from datetime import datetime
from supabase import create_client
import os
from typing import List, Dict, Any

class InfoAgent:
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize Supabase client
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Brave Search API key
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        
        # Define tools for OpenAI function calling
        self.tools = [{
            "type": "function",
            "function": {
                "name": "search_financial_news",
                "description": "Search for latest financial news about macroeconomics and Bitcoin",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for financial news"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }]

    def  search_brave(self, query: str) -> List[Dict[str, Any]]:
        """
        Search news using Brave Search API
        """
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.brave_api_key
        }
        params = {
            "q": query,
            "freshness": "pd",  # past day
            "result_filter": "news"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json().get("web", {}).get("results", [])
            return results[:5]  # Return top 5 news results
        return []

    def store_news(self, news_items: List[Dict[str, Any]]) -> None:
        """
        Store news items in Supabase database
        """
        current_time = datetime.utcnow().isoformat()
        
        for item in news_items:
            news_data = {
                'timestamp': current_time,
                'finance_info': f"{item['title']} - {item['description']}"
            }
            
            self.supabase.table('eco_news').insert(news_data).execute()

    def process_news_search(self) -> None:
        """
        Use OpenAI to generate search queries and process news for both crypto and general finance
        """
        # Define separate prompts for crypto and general finance
        search_categories = [
            {
                "role": "system",
                "content": "You are a cryptocurrency news researcher. Generate a search query for important Bitcoin and crypto news. Focus on significant market movements, regulatory updates, and major cryptocurrency developments.",
                "user_prompt": "Generate a specific search query for the latest important cryptocurrency news."
            },
            {
                "role": "system",
                "content": "You are a financial markets researcher. Generate a search query for important macroeconomic news. Focus on significant market events, central bank policies, economic indicators, and global financial developments.",
                "user_prompt": "Generate a specific search query for the latest important financial market news."
            }
        ]

        # Process each category
        for category in search_categories:
            messages = [
                {
                    "role": "system",
                    "content": category["content"]
                },
                {
                    "role": "user",
                    "content": category["user_prompt"]
                }
            ]

            completion = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=self.tools,
                tool_choice="required"
            )

            # Process the search query
            for tool_call in completion.choices[0].message.tool_calls:
                if tool_call.function.name == "search_financial_news":
                    # Extract query and search using Brave
                    query = eval(tool_call.function.arguments)["query"]
                    news_results = self.search_brave(query)
                    
                    if news_results:
                        # Store results in database
                        self.store_news(news_results)

    def run(self) -> None:
        """
        Main method to run the info agent
        """
        try:
            self.process_news_search()
        except Exception as e:
            print(f"Error running InfoAgent: {str(e)}")

if __name__ == "__main__":
    agent = InfoAgent()
    agent.run()

