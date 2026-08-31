from datetime import datetime
import logging

from dotenv import load_dotenv
from pydantic import BaseModel

from app.services.email import send_email
from app.database.repository import Repository
from app.profiles.user_profile import USER_PROFILE
from app.agent.curator_agent import CuratorAgent


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class EmailArticle(BaseModel):
    digest_id: str
    rank: int
    relevance_score: float
    title: str
    summary: str
    url: str
    article_type: str
    reasoning: str


def generate_email_digest(
    hours: int = 24,
    top_n: int = 10
) -> list[EmailArticle]:
    """
    Get recent digests, rank them using CuratorAgent,
    and return the top N articles for the email.
    """

    curator = CuratorAgent(USER_PROFILE)
    repo = Repository()

    digests = repo.get_recent_digests(hours=hours)

    total = len(digests)

    # No recent digests is a valid condition, not an error.
    if total == 0:
        logger.info(
            f"No digests found from the last {hours} hours."
        )
        return []

    logger.info(
        f"Ranking {total} digests for email generation"
    )

    ranked_articles = curator.rank_digests(digests)

    if not ranked_articles:
        logger.error("Failed to rank digests")
        raise ValueError("Failed to rank articles")

    # Fast lookup by digest ID
    digest_lookup = {
        digest["id"]: digest
        for digest in digests
    }

    article_details: list[EmailArticle] = []

    for ranked in ranked_articles:

        digest = digest_lookup.get(
            ranked.digest_id
        )

        if not digest:
            logger.warning(
                f"Digest not found for ID: "
                f"{ranked.digest_id}"
            )
            continue

        article_details.append(
            EmailArticle(
                digest_id=ranked.digest_id,
                rank=ranked.rank,
                relevance_score=ranked.relevance_score,
                title=digest["title"],
                summary=digest["summary"],
                url=digest["url"],
                article_type=digest["article_type"],
                reasoning=ranked.reasoning,
            )
        )

    # Lowest rank number = highest priority
    article_details.sort(
        key=lambda article: article.rank
    )

    # Keep only top N
    article_details = article_details[:top_n]

    logger.info(
        f"Email digest generated with "
        f"{len(article_details)} articles"
    )

    return article_details


def digest_to_html(
    user_name: str,
    articles: list[EmailArticle]
) -> str:
    """
    Convert the ranked articles into HTML email content.
    """

    current_date = datetime.now().strftime(
        "%B %d, %Y"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>PulseAI Daily AI Digest</title>
    </head>

    <body
        style="
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            font-family: Arial, Helvetica, sans-serif;
        "
    >

        <div
            style="
                max-width: 700px;
                margin: 0 auto;
                padding: 30px 20px;
            "
        >

            <div
                style="
                    background: #111827;
                    color: white;
                    padding: 25px;
                    border-radius: 12px;
                "
            >

                <h1
                    style="
                        margin: 0 0 8px 0;
                        font-size: 28px;
                    "
                >
                    PulseAI Daily AI Digest
                </h1>

                <p
                    style="
                        margin: 0;
                        color: #d1d5db;
                    "
                >
                    {current_date}
                </p>

            </div>

            <div
                style="
                    background: white;
                    margin-top: 20px;
                    padding: 25px;
                    border-radius: 12px;
                "
            >

                <p
                    style="
                        font-size: 16px;
                        color: #374151;
                    "
                >
                    Hey {user_name},
                </p>

                <p
                    style="
                        font-size: 16px;
                        color: #374151;
                    "
                >
                    Here are today's top AI stories,
                    ranked according to your interests.
                </p>
    """

    for index, article in enumerate(
        articles,
        start=1
    ):

        html += f"""
                <div
                    style="
                        margin-top: 25px;
                        padding-bottom: 25px;
                        border-bottom: 1px solid #e5e7eb;
                    "
                >

                    <p
                        style="
                            color: #6b7280;
                            font-size: 13px;
                            margin-bottom: 8px;
                        "
                    >
                        #{index}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        {article.article_type.upper()}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        Relevance:
                        {article.relevance_score:.1f}/10
                    </p>

                    <h2
                        style="
                            margin: 5px 0 12px 0;
                            font-size: 21px;
                            color: #111827;
                        "
                    >
                        {article.title}
                    </h2>

                    <p
                        style="
                            color: #4b5563;
                            font-size: 15px;
                            line-height: 1.6;
                        "
                    >
                        {article.summary}
                    </p>

                    <p>
                        <a
                            href="{article.url}"
                            target="_blank"
                            style="
                                color: #2563eb;
                                text-decoration: none;
                                font-weight: bold;
                            "
                        >
                            Read full story →
                        </a>
                    </p>

                </div>
        """

    html += """
            </div>

            <div
                style="
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                    padding: 20px;
                "
            >
                <p>
                    Powered by PulseAI
                </p>
            </div>

        </div>

    </body>
    </html>
    """

    return html


def send_digest_email(
    hours: int = 24,
    top_n: int = 10
) -> dict:
    """
    Generate and send the daily PulseAI digest using Resend.
    """

    try:

        articles = generate_email_digest(
            hours=hours,
            top_n=top_n
        )

        current_date = datetime.now().strftime(
            "%B %d, %Y"
        )

        subject = (
            f"PulseAI Daily AI Digest - "
            f"{current_date}"
        )

        # -------------------------------------------------
        # No-news case
        # -------------------------------------------------

        if not articles:

            logger.info(
                "No new AI articles found. "
                "Sending no-news email."
            )

            body_text = (
                f"Hey {USER_PROFILE['name']},\n\n"
                f"No new AI news was found in the "
                f"last {hours} hours.\n\n"
                "PulseAI will check again tomorrow."
            )

            body_html = f"""
            <!DOCTYPE html>
            <html>
            <body
                style="
                    font-family: Arial, Helvetica, sans-serif;
                    background: #f5f5f5;
                    padding: 30px;
                "
            >

                <div
                    style="
                        max-width: 600px;
                        margin: auto;
                        background: white;
                        padding: 30px;
                        border-radius: 12px;
                    "
                >

                    <h1>
                        PulseAI Daily AI Digest
                    </h1>

                    <p>
                        Hey {USER_PROFILE["name"]},
                    </p>

                    <p>
                        No new AI news was found in the
                        last {hours} hours.
                    </p>

                    <p>
                        PulseAI will check again tomorrow.
                    </p>

                </div>

            </body>
            </html>
            """

            send_email(
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                recipients=[
                    USER_PROFILE["email"]
                ],
            )

            logger.info(
                "No-news email sent successfully."
            )

            return {
                "success": True,
                "subject": subject,
                "articles_count": 0,
            }

        # -------------------------------------------------
        # Normal digest
        # -------------------------------------------------

        body_text = (
            f"Hey {USER_PROFILE['name']},\n\n"
            "Here are today's top AI stories."
        )

        body_html = digest_to_html(
            user_name=USER_PROFILE["name"],
            articles=articles,
        )

        send_email(
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            recipients=[
                USER_PROFILE["email"]
            ],
        )

        logger.info(
            f"Email sent successfully with "
            f"{len(articles)} articles."
        )

        return {
            "success": True,
            "subject": subject,
            "articles_count": len(articles),
        }

    except ValueError as e:

        logger.error(
            f"Error sending email: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }

    except Exception as e:

        logger.error(
            f"Unexpected email error: {e}",
            exc_info=True
        )

        return {
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":

    result = send_digest_email(
        hours=24,
        top_n=10
    )

    if result["success"]:

        print("\n=== Email Digest Sent ===")
        print(
            f"Subject: {result['subject']}"
        )
        print(
            f"Articles: {result['articles_count']}"
        )

    else:

        print(
            f"Error: {result['error']}"
        )
