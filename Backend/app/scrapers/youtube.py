from datetime import datetime, timedelta, timezone
from typing import List, Optional
import os
import re
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import requests
import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
)
from youtube_transcript_api.proxies import WebshareProxyConfig


logger = logging.getLogger(__name__)

# Keep external scraping from blocking the entire daily pipeline.
RSS_TIMEOUT_SECONDS = int(os.getenv("SCRAPER_RSS_TIMEOUT", "15"))
TRANSCRIPT_TIMEOUT_SECONDS = int(os.getenv("SCRAPER_TRANSCRIPT_TIMEOUT", "30"))

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

    def _fetch_transcript(self, video_id: str):
        """Run the YouTube transcript request in a worker so a stuck request
        cannot block the daily pipeline indefinitely."""
        return self.transcript_api.fetch(video_id)

    def get_transcript(
        self,
        video_id: str
    ) -> Optional[Transcript]:

        logger.info(
            "Starting transcript fetch for %s (timeout=%ss)",
            video_id,
            TRANSCRIPT_TIMEOUT_SECONDS,
        )

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self._fetch_transcript, video_id)

        try:
            transcript = future.result(timeout=TRANSCRIPT_TIMEOUT_SECONDS)

            text = " ".join(
                snippet.text
                for snippet in transcript.snippets
            )

            if not text.strip():
                logger.warning("Empty transcript for %s", video_id)
                return None

            logger.info("Transcript fetched successfully for %s", video_id)

            return Transcript(
                text=text
            )

        except FuturesTimeoutError:
            logger.warning(
                "Transcript timed out after %ss for %s; continuing without it",
                TRANSCRIPT_TIMEOUT_SECONDS,
                video_id,
            )
            return None

        except (
            TranscriptsDisabled,
            NoTranscriptFound
        ):
            logger.info("No transcript available for %s", video_id)
            return None

        except Exception as e:
            logger.warning(
                "Transcript error (%s): %s",
                video_id,
                e,
            )
            return None

        finally:
            # Do not wait for a stuck worker during executor shutdown.
            executor.shutdown(wait=False, cancel_futures=True)

    # ---------------------------------------------------------
    # Get latest videos
    # ---------------------------------------------------------

    def get_latest_videos(
        self,
        channel_id: str,
        hours: int = 24,
        max_videos: int = 10
    ) -> List[ChannelVideo]:

        rss_url = self._get_rss_url(channel_id)

        logger.info(
            "Fetching YouTube RSS for channel %s (timeout=%ss)",
            channel_id,
            RSS_TIMEOUT_SECONDS,
        )

        try:
            response = requests.get(
                rss_url,
                timeout=RSS_TIMEOUT_SECONDS,
                headers={
                    "User-Agent": "PulseAI/1.0 (+https://www.youtube.com/)"
                },
            )
            response.raise_for_status()
            feed = feedparser.parse(response.content)

        except requests.Timeout:
            logger.warning(
                "YouTube RSS timed out after %ss for channel %s",
                RSS_TIMEOUT_SECONDS,
                channel_id,
            )
            return []

        except requests.RequestException as e:
            logger.warning(
                "YouTube RSS request failed for channel %s: %s",
                channel_id,
                e,
            )
            return []

        except Exception as e:
            logger.warning(
                "YouTube RSS parsing failed for channel %s: %s",
                channel_id,
                e,
            )
            return []

        if not feed.entries:
            logger.info("No YouTube RSS entries for channel %s", channel_id)
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

        logger.info(
            "Starting YouTube channel scrape: %s (window=%sh, max_videos=%s)",
            channel_id,
            hours,
            max_videos,
        )

        videos = self.get_latest_videos(
            channel_id=channel_id,
            hours=hours,
            max_videos=max_videos
        )

        logger.info(
            "YouTube channel %s: found %d AI videos in the last %s hours",
            channel_id,
            len(videos),
            hours,
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

        logger.info(
            "Finished YouTube channel scrape: %s (%d videos)",
            channel_id,
            len(result),
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

    logger.info("Running YouTube scraper test with a 24-hour window")
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
