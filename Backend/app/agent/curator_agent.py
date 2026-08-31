import os
import logging
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger(__name__)


class RankedArticle(BaseModel):
    digest_id: str
    relevance_score: float = Field(
        ge=0.0,
        le=10.0
    )
    rank: int = Field(
        ge=1
    )
    reasoning: str


CURATOR_PROMPT = """
You are an expert AI news curator.

Rank articles based on the user's interests and preferences.

IMPORTANT:
- SCORE MUST be between 0.0 and 10.0.
- Do NOT use scores like 92, 88, or 75.
- Valid examples: 9.2, 8.8, 7.5, 6.0, 4.5.
- RANK must start at 1, where 1 is the most relevant.

Return ONLY this format:

DIGEST_ID: <id>
SCORE: <0.0-10.0>
RANK: <rank>
REASON: <reason>

Separate each article with one blank line.

Do not add headings, explanations, markdown, or any other text.
"""


class CuratorAgent:

    def __init__(self, user_profile: dict):

        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = os.getenv("GROQ_MODEL")

        if not self.model:
            raise ValueError(
                "GROQ_MODEL is not set in the .env file"
            )

        self.user_profile = user_profile
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:

        interests = "\n".join(
            f"- {interest}"
            for interest in self.user_profile["interests"]
        )

        preferences = self.user_profile["preferences"]

        pref_text = "\n".join(
            f"- {k}: {v}"
            for k, v in preferences.items()
        )

        return f"""
{CURATOR_PROMPT}

User Profile:
Name: {self.user_profile["name"]}
Background: {self.user_profile["background"]}
Expertise Level: {self.user_profile["expertise_level"]}

Interests:
{interests}

Preferences:
{pref_text}
"""

    def rank_digests(
        self,
        digests: List[dict]
    ) -> List[RankedArticle]:

        if not digests:
            return []

        # ---------------------------------------------
        # Basic AI filtering before calling the LLM
        # ---------------------------------------------

        ai_keywords = [
            "ai",
            "gpt",
            "llm",
            "openai",
            "anthropic",
            "claude",
            "gemini",
            "machine learning",
            "rag",
            "agent",
        ]

        filtered_digests = []

        for d in digests:

            text = (
                f"{d['title']} "
                f"{d['summary']}"
            ).lower()

            if any(
                keyword in text
                for keyword in ai_keywords
            ):
                filtered_digests.append(d)

        digests = filtered_digests

        if not digests:
            return []

        # ---------------------------------------------
        # Build LLM input
        # ---------------------------------------------

        digest_list = "\n\n".join(
            f"""
ID: {d['id']}
Title: {d['title']}
Summary: {d['summary']}
Type: {d['article_type']}
"""
            for d in digests
        )

        user_prompt = f"""
Rank these {len(digests)} AI news digests according to
the user's profile.

{digest_list}
"""

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            output = response.choices[0].message.content or ""

            print(output)

            ranked_articles = []

            # ---------------------------------------------
            # Parse model output
            # ---------------------------------------------

            blocks = output.strip().split("\n\n")

            for block in blocks:

                lines = block.strip().splitlines()

                article_data = {}

                for line in lines:

                    line = line.strip()

                    if line.startswith("DIGEST_ID:"):

                        article_data["digest_id"] = (
                            line
                            .replace(
                                "DIGEST_ID:",
                                "",
                                1
                            )
                            .strip()
                        )

                    elif line.startswith("SCORE:"):

                        raw_score = (
                            line
                            .replace(
                                "SCORE:",
                                "",
                                1
                            )
                            .strip()
                        )

                        try:

                            score = float(
                                raw_score
                            )

                        except ValueError:

                            logger.warning(
                                f"Invalid score received: "
                                f"{raw_score}"
                            )

                            continue

                        # Handle model returning 92 instead
                        # of 9.2.
                        if score > 10:
                            score = score / 10.0

                        # Clamp safely to 0-10.
                        score = max(
                            0.0,
                            min(score, 10.0)
                        )

                        article_data[
                            "relevance_score"
                        ] = score

                    elif line.startswith("RANK:"):

                        raw_rank = (
                            line
                            .replace(
                                "RANK:",
                                "",
                                1
                            )
                            .strip()
                        )

                        try:

                            article_data["rank"] = int(
                                raw_rank
                            )

                        except ValueError:

                            logger.warning(
                                f"Invalid rank received: "
                                f"{raw_rank}"
                            )

                            continue

                    elif line.startswith("REASON:"):

                        article_data[
                            "reasoning"
                        ] = (
                            line
                            .replace(
                                "REASON:",
                                "",
                                1
                            )
                            .strip()
                        )

                # -----------------------------------------
                # Validate parsed article
                # -----------------------------------------

                required_fields = {
                    "digest_id",
                    "relevance_score",
                    "rank",
                    "reasoning"
                }

                if not required_fields.issubset(
                    article_data.keys()
                ):
                    logger.warning(
                        f"Skipping incomplete ranking block: "
                        f"{article_data}"
                    )
                    continue

                try:

                    ranked_articles.append(
                        RankedArticle(
                            digest_id=article_data[
                                "digest_id"
                            ],
                            relevance_score=article_data[
                                "relevance_score"
                            ],
                            rank=article_data[
                                "rank"
                            ],
                            reasoning=article_data[
                                "reasoning"
                            ]
                        )
                    )

                except Exception as e:

                    logger.warning(
                        f"Invalid ranked article: {e}"
                    )

            # ---------------------------------------------
            # Sort by rank
            # ---------------------------------------------

            ranked_articles.sort(
                key=lambda article: article.rank
            )

            return ranked_articles

        except Exception as e:

            logger.error(
                f"Error ranking digests: {e}"
            )

            return []
