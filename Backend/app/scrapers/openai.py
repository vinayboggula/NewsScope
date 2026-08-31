from datetime import datetime, timedelta, timezone
from typing import List, Optional

import feedparser
from pydantic import BaseModel


class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class OpenAIScraper:

    def __init__(self):
        self.rss_url = "https://openai.com/news/rss.xml"

    def get_articles(
        self,
        hours: int = 24,
        max_articles: int = 20
    ) -> List[OpenAIArticle]:

        feed = feedparser.parse(self.rss_url)

        if not feed.entries:
            return []

        cutoff_time = (
            datetime.now(timezone.utc)
            - timedelta(hours=hours)
        )

        articles = []
        seen_guids = set()

        for entry in feed.entries:

            # -------------------------------------------------
            # Published date
            # -------------------------------------------------

            published_parsed = getattr(
                entry,
                "published_parsed",
                None
            )

            if not published_parsed:
                continue

            published_time = datetime(
                *published_parsed[:6],
                tzinfo=timezone.utc
            )

            # -------------------------------------------------
            # Time filter
            # -------------------------------------------------

            if published_time < cutoff_time:
                continue

            # -------------------------------------------------
            # Extract fields
            # -------------------------------------------------

            title = entry.get(
                "title",
                ""
            ).strip()

            description = entry.get(
                "description",
                ""
            ).strip()

            url = entry.get(
                "link",
                ""
            ).strip()

            guid = entry.get(
                "id",
                url
            ).strip()

            # -------------------------------------------------
            # Deduplicate
            # -------------------------------------------------

            if guid in seen_guids:
                continue

            seen_guids.add(guid)

            # -------------------------------------------------
            # Category
            # -------------------------------------------------

            category = None

            tags = entry.get(
                "tags",
                []
            )

            if tags:
                category = tags[0].get(
                    "term"
                )

            # -------------------------------------------------
            # Create article
            # -------------------------------------------------

            article = OpenAIArticle(
                title=title,
                description=description,
                url=url,
                guid=guid,
                published_at=published_time,
                category=category
            )

            articles.append(article)

            # -------------------------------------------------
            # Limit results
            # -------------------------------------------------

            if len(articles) >= max_articles:
                break

        return articles


if __name__ == "__main__":

    scraper = OpenAIScraper()

    articles = scraper.get_articles(
        hours=24,
        max_articles=20
    )

    print(
        f"Found {len(articles)} OpenAI articles"
    )

    for article in articles:

        print(
            f"\n{article.title}"
        )

        print(
            article.published_at
        )

        print(
            article.url
        )
