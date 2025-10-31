from google import genai
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

async def analyze_with_gemini(news: str, sector: str):
    prompt = f"""
    You are a financial market analyst specializing in India's {sector} sector.
    Analyze the following recent news and synthesize key insights:

    --- NEWS START ---
    {news}
    --- NEWS END ---

    **Your task:**
    Create a concise, well-structured **Markdown report** covering:

    1. **Sector Overview** — Brief context of the {sector} sector in India.
    2. **Key Trends** — Identify emerging patterns or changes supported by the news.
    3. **Risks & Opportunities** — Highlight potential challenges and growth drivers.
    4. **Market Outlook** — Provide a short-term (3–6 months) and medium-term (1–2 years) outlook.
    5. **Investor Insight (optional)** — If relevant, note implications for investors or businesses.

    **Formatting Guidelines:**
    - Use Markdown headers and bullet points for clarity.
    - Keep the analysis concise, factual, and neutral in tone.
    - Avoid repeating information verbatim from the news; instead, synthesize insights.
    """


    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text.strip()

    except Exception as e:
        return f" Gemini API Error: {str(e)}"

# Example test
if __name__ == "__main__":
    sample_news = """
    India's renewable energy sector is attracting major foreign investments.
    Solar and wind energy projects are growing rapidly, supported by government initiatives.
    """
    result = asyncio.run(analyze_with_gemini(sample_news, "renewable energy"))
    print(result)
