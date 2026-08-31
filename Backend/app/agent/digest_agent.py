import os
from typing import Optional
import time

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str


PROMPT = """
You are an expert AI news analyst specializing in summarizing technical articles,
research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly
understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance

Return the response in the following format:

Title: <title>

Summary: <summary>
"""


class DigestAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = os.getenv("GROQ_MODEL")
        self.system_prompt = PROMPT

    def generate_digest(
        self,
        title: str,
        content: str,
        article_type: str
    ) -> Optional[DigestOutput]:

        try:
            user_prompt = f"""
            Create a digest for this {article_type}.

            Title: {title}

            Content:
            {content[:4000]}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,
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
            time.sleep(2)
            output = response.choices[0].message.content

            parts = output.split("Summary:")

            digest_title = parts[0].replace("Title:", "").strip()

            digest_summary = (
                parts[1].strip()
                if len(parts) > 1
                else output
            )

            return DigestOutput(
                title=digest_title,
                summary=digest_summary
            )

        except Exception as e:
            print(f"Error generating digest: {e}")
            return None
