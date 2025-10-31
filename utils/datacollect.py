import asyncio
from duckduckgo_search import DDGS

async def fetch_sector_news(sector: str):
    """Fetch detailed sector news using DuckDuckGo search."""
    try:
        results = DDGS().news(
            keywords=f"{sector} India",
            region="in-en",
            safesearch="on",
            timelimit="7d",
            max_results=20
        )

        articles = list(results)

        if not articles:
            return [f"No news found for {sector} sector."]

        # Format top 5 articles neatly
        detailed_news = []
        for a in articles[:10]:
            title = a.get("title", "No title")
            description = a.get("body", "No description available.")
            source = a.get("source", "Unknown source")
            pub_date = a.get("date", "No date")
            link = a.get("url", "#")

            news_item = (
                f"📰 **{title}**\n"
                f"📄 {description}\n"
                f"🏢 Source: {source}\n"
                f"📅 Published: {pub_date}\n"
                f"🔗 Link: {link}\n"
                + "—" * 50
            )
            detailed_news.append(news_item)

        return detailed_news

    except Exception as e:
        return [f"Error fetching data: {str(e)}"]


# Run standalone test
if __name__ == "__main__":
    sector = "technology"
    results = asyncio.run(fetch_sector_news(sector))
    print("\n\n".join(results))
