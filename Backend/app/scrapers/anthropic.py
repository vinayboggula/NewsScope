from datetime import datetime, timedelta, timezone
from typing import List, Optional

import feedparser
from docling.document_converter import DocumentConverter
from pydantic import BaseModel


class AnthropicArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class AnthropicScraper:

    def __init__(self):

        self.rss_urls = [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        ]

        # Used only when converting an article URL
        # into full markdown content.
        self.converter = DocumentConverter()

    def get_articles(
        self,
        hours: int = 24,
        max_articles: int = 15
    ) -> List[AnthropicArticle]:

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
                # Time filter
                # -----------------------------------------

                if published_time < cutoff_time:
                    continue

                # -----------------------------------------
                # Extract URL / GUID
                # -----------------------------------------

                url = entry.get(
                    "link",
                    ""
                ).strip()

                guid = entry.get(
                    "id",
                    url
                ).strip()

                if not guid:
                    continue

                # -----------------------------------------
                # Deduplicate
                # -----------------------------------------

                if guid in seen_guids:
                    continue

                seen_guids.add(guid)

                # -----------------------------------------
                # Extract category
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

                article = AnthropicArticle(
                    title=entry.get(
                        "title",
                        ""
                    ).strip(),

                    description=entry.get(
                        "description",
                        ""
                    ).strip(),

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
                # Global limit
                # -----------------------------------------

                if len(articles) >= max_articles:

                    print(
                        f"\nReached maximum of "
                        f"{max_articles} Anthropic articles."
                    )

                    return articles

        print("\n" + "=" * 50)

        print(
            f"Total Anthropic articles collected: "
            f"{len(articles)}"
        )

        return articles

    def url_to_markdown(
        self,
        url: str
    ) -> Optional[str]:

        try:

            result = self.converter.convert(url)

            return result.document.export_to_markdown()

        except Exception as e:

            print(
                f"Markdown conversion failed: {e}"
            )

            return None


if __name__ == "__main__":

    scraper = AnthropicScraper()

    articles = scraper.get_articles(
        hours=24,
        max_articles=15
    )

    print("\nCollected articles:\n")

    for article in articles:

        print(
            f"{article.title} | "
            f"{article.published_at}"
        )

    # Test Docling separately
    if articles:

        markdown = scraper.url_to_markdown(
            articles[0].url
        )

        if markdown:

            print("\nMarkdown Preview:\n")
            print(markdown[:2000])
