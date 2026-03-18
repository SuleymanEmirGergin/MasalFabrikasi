from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

class AtmosphereService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

    async def analyze_mood(self, text: str) -> dict:
        """
        Analyzes the text and returns atmospheric lighting data.
        Returns: { "color": "#RRGGBB", "brightness": 0-100, "mood": "calm" }
        """
        system_prompt = """
        Analyze the given story segment and determine the appropriate ambient lighting color and brightness to match the atmosphere.
        Return ONLY a JSON object with:
        - color: Hex code (e.g. #FF0000 for danger/fire, #00FF00 for forest, #0000FF for night/sea, #FFFF00 for day/happy)
        - brightness: Integer 0-100
        - mood: One word description (e.g. Scary, Happy, Mysterious)
        
        Example:
        Text: "The dark cave was filled with glowing red eyes."
        Response: {"color": "#660000", "brightness": 30, "mood": "Scary"}
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=text)
            ])
            
            # Simple cleaning
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"Atmosphere analysis failed: {e}")
            return {"color": "#FFFFFF", "brightness": 100, "mood": "Neutral"}

atmosphere_service = AtmosphereService()
