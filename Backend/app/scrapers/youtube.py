from datetime import datetime, timedelta, timezone
from typing import List, Optional
import os
import re

import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
)
from youtube_transcript_api.proxies import WebshareProxyConfig


# Strong AI-related terms
STRONG_AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "generative ai",
    "large language model",
    "language model",
    "llm",
    "gpt",
    "chatgpt",
    "openai",
    "anthropic",
    "claude",
    "gemini",
    "deepseek",
    "mistral",
    "llama",
    "rag",
    "retrieval augmented generation",
    "ai agent",
    "ai agents",
    "agentic ai",
    "fine tuning",
    "fine-tuning",
    "neural network",
    "transformer",
]


# General AI terms
AI_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "llm",
    "gpt",
    "chatgpt",
    "openai",
    "anthropic",
    "claude",
    "gemini",
    "deepseek",
    "mistral",
    "llama",
    "rag",
    "agent",
    "agents",
    "langchain",
    "mcp",
    "fine tuning",
    "fine-tuning",
]


class Transcript(BaseModel):
    text: str


class ChannelVideo(BaseModel):
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str
    transcript: Optional[str] = None


class YouTubeScraper:

    def __init__(self):

        proxy_config = None

        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")

        if proxy_username and proxy_password:
            proxy_config = WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )

        self.transcript_api = YouTubeTranscriptApi(
            proxy_config=proxy_config
        )

    # ---------------------------------------------------------
    # RSS
    # ---------------------------------------------------------

    def _get_rss_url(self, channel_id: str) -> str:

        return (
            "https://www.youtube.com/feeds/videos.xml"
            f"?channel_id={channel_id}"
        )

    # ---------------------------------------------------------
    # Video ID
    # ---------------------------------------------------------

    def _extract_video_id(self, video_url: str) -> str:

        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]

        if "youtube.com/shorts/" in video_url:
            return video_url.split("shorts/")[1].split("?")[0]

        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]

        return video_url

    # ---------------------------------------------------------
    # Keyword matching
    # ---------------------------------------------------------

    def _keyword_matches(
        self,
        text: str,
        keywords: List[str]
    ) -> List[str]:

        text = text.lower()

        matches = []

        for keyword in keywords:

            # Convert keyword into a safe regex
            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

            if re.search(pattern, text):
                matches.append(keyword)

        return matches

    # ---------------------------------------------------------
    # AI relevance
    # ---------------------------------------------------------

    def _is_ai_video(
        self,
        title: str,
        description: str
    ) -> bool:

        title_matches = self._keyword_matches(
            title,
            STRONG_AI_KEYWORDS
        )

        description_matches = self._keyword_matches(
            description,
            AI_KEYWORDS
        )

        # Strongest signal:
        # AI topic explicitly mentioned in title
        if title_matches:
            return True

        # Otherwise require multiple AI signals
        if len(description_matches) >= 2:
            return True

        return False

    # ---------------------------------------------------------
    # Transcript
    # ---------------------------------------------------------

    def get_transcript(
        self,
        video_id: str
    ) -> Optional[Transcript]:

        try:

            transcript = self.transcript_api.fetch(
                video_id
            )

            text = " ".join(
                snippet.text
                for snippet in transcript.snippets
            )

            if not text.strip():
                return None

            return Transcript(
                text=text
            )

        except (
            TranscriptsDisabled,
            NoTranscriptFound
        ):

            return None

        except Exception as e:

            print(
                f"Transcript error ({video_id}): {e}"
            )

            return None

    # ---------------------------------------------------------
    # Get latest videos
    # ---------------------------------------------------------

    def get_latest_videos(
        self,
        channel_id: str,
        hours: int = 24,
        max_videos: int = 10
    ) -> List[ChannelVideo]:

        feed = feedparser.parse(
            self._get_rss_url(channel_id)
        )

        if not feed.entries:
            return []

        cutoff_time = (
            datetime.now(timezone.utc)
            - timedelta(hours=hours)
        )

        videos = []

        seen_video_ids = set()

        for entry in feed.entries:

            # -------------------------------------------------
            # Skip Shorts
            # -------------------------------------------------

            if "/shorts/" in entry.link:
                continue

            # -------------------------------------------------
            # Published time
            # -------------------------------------------------

            if not getattr(
                entry,
                "published_parsed",
                None
            ):
                continue

            published_time = datetime(
                *entry.published_parsed[:6],
                tzinfo=timezone.utc
            )

            # -------------------------------------------------
            # Time filter
            # -------------------------------------------------

            if published_time < cutoff_time:
                continue

            # -------------------------------------------------
            # Extract data
            # -------------------------------------------------

            title = entry.title.strip()

            description = entry.get(
                "summary",
                ""
            ).strip()

            video_id = self._extract_video_id(
                entry.link
            )

            # -------------------------------------------------
            # Deduplicate
            # -------------------------------------------------

            if video_id in seen_video_ids:
                continue

            seen_video_ids.add(video_id)

            # -------------------------------------------------
            # AI filter
            # -------------------------------------------------

            if not self._is_ai_video(
                title,
                description
            ):

                print(
                    f"Skipped non-AI: {title}"
                )

                continue

            print(
                f"Accepted AI video: {title}"
            )

            videos.append(
                ChannelVideo(
                    title=title,
                    url=entry.link,
                    video_id=video_id,
                    published_at=published_time,
                    description=description,
                )
            )

            # -------------------------------------------------
            # Limit per channel
            # -------------------------------------------------

            if len(videos) >= max_videos:
                break

        return videos

    # ---------------------------------------------------------
    # Scrape channel
    # ---------------------------------------------------------

    def scrape_channel(
        self,
        channel_id: str,
        hours: int = 24,
        max_videos: int = 5
    ) -> List[ChannelVideo]:

        videos = self.get_latest_videos(
            channel_id=channel_id,
            hours=hours,
            max_videos=max_videos
        )

        result = []

        for video in videos:

            print(
                f"Fetching transcript: {video.title}"
            )

            transcript = self.get_transcript(
                video.video_id
            )

            result.append(
                video.model_copy(
                    update={
                        "transcript": (
                            transcript.text
                            if transcript
                            else None
                        )
                    }
                )
            )

        return result


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    scraper = YouTubeScraper()

    YOUTUBE_CHANNELS = [

        "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman

        "UCbfYPyITQ-7l4upoX8nvctg",  # Two Minute Papers

        "UCsBjURrPoezykLs9EqgamOA",  # Fireship

        "UCbY9xX3_jW5c2fjlZVBI4cg",  # The AI Grid

        "UCNQNu7GURrjlq6edY-qNwow",  # IBM Technology

        "UCHuiy8bXnmK5nisYHUd1J5g",  # NVIDIA
    ]

    all_videos = []

    for channel_id in YOUTUBE_CHANNELS:

        videos = scraper.scrape_channel(
            channel_id=channel_id,
            hours=24,
            max_videos=5
        )

        print(
            f"\nFound {len(videos)} AI videos "
            f"for channel {channel_id}"
        )

        all_videos.extend(videos)

        for video in videos:

            print(
                f"- {video.title}"
            )

    print("\n" + "=" * 60)

    print(
        f"TOTAL AI VIDEOS: {len(all_videos)}"
    )

    print("=" * 60)
