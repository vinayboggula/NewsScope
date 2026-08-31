from datetime import datetime, timedelta, timezone
from typing import List, Optional

import feedparser
from pydantic import BaseModel


class GoogleArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class GoogleScraper:

    def __init__(self):

        self.rss_urls = [
            "https://blog.google/technology/ai/rss/",
            "https://deepmind.google/blog/rss.xml",
            "https://research.google/blog/rss/",
        ]

    def get_articles(
        self,
        hours: int = 24,
        max_articles: int = 20
    ) -> List[GoogleArticle]:

        cutoff_time = (
            datetime.now(timezone.utc)
            - timedelta(hours=hours)
        )

        articles = []
        seen_guids = set()

        for rss_url in self.rss_urls:

            print("\n" + "=" * 50)
            print(f"Checking feed: {rss_url}")

            feed = feedparser.parse(rss_url)

            print(
                f"Found {len(feed.entries)} entries"
            )

            if not feed.entries:
                continue

            for entry in feed.entries:

                # -----------------------------------------
                # Get publication date
                # -----------------------------------------

                published_parsed = (
                    getattr(
                        entry,
                        "published_parsed",
                        None
                    )
                    or getattr(
                        entry,
                        "updated_parsed",
                        None
                    )
                )

                if not published_parsed:
                    continue

                published_time = datetime(
                    *published_parsed[:6],
                    tzinfo=timezone.utc
                )

                # -----------------------------------------
                # Time filtering
                # -----------------------------------------

                if published_time < cutoff_time:
                    continue

                # -----------------------------------------
                # Extract GUID
                # -----------------------------------------

                guid = entry.get(
                    "id",
                    entry.get("link", "")
                ).strip()

                if not guid:
                    continue

                # -----------------------------------------
                # Deduplication
                # -----------------------------------------

                if guid in seen_guids:
                    continue

                seen_guids.add(guid)

                # -----------------------------------------
                # Extract data
                # -----------------------------------------

                title = entry.get(
                    "title",
                    ""
                ).strip()

                description = entry.get(
                    "summary",
                    ""
                ).strip()

                url = entry.get(
                    "link",
                    ""
                ).strip()

                # -----------------------------------------
                # Category
                # -----------------------------------------

                category = None

                if entry.get("tags"):

                    category = (
                        entry["tags"][0]
                        .get("term")
                    )

                # -----------------------------------------
                # Create article
                # -----------------------------------------

                article = GoogleArticle(
                    title=title,
                    description=description,
                    url=url,
                    guid=guid,
                    published_at=published_time,
                    category=category
                )

                articles.append(article)

                print(
                    f"Added: {article.title}"
                )

                # -----------------------------------------
                # Global article limit
                # -----------------------------------------

                if len(articles) >= max_articles:
                    print(
                        f"\nReached maximum of "
                        f"{max_articles} Google articles."
                    )

                    return articles

        print("\n" + "=" * 50)
        print(
            f"Total Google articles collected: "
            f"{len(articles)}"
        )

        return articles


if __name__ == "__main__":

    scraper = GoogleScraper()

    articles = scraper.get_articles(
        hours=24,
        max_articles=20
    )

    print("\nCollected articles:\n")

    for article in articles:

        print(
            f"{article.title} | "
            f"{article.published_at}"
        )
