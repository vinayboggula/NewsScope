from datetime import datetime


def create_digest_email(
    user_name: str,
    articles: list
) -> str:

    current_date = datetime.now().strftime("%B %d, %Y")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 20px;
            }}

            .container {{
                max-width: 700px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            .date {{
                color: #666;
                margin-bottom: 30px;
            }}

            .article {{
                padding: 20px 0;
                border-bottom: 1px solid #ddd;
            }}

            .article h2 {{
                margin-bottom: 10px;
            }}

            .summary {{
                color: #444;
                line-height: 1.6;
            }}

            .read-more {{
                display: inline-block;
                margin-top: 10px;
            }}
        </style>
    </head>

    <body>

        <div class="container">

            <h1>PulseAI Daily Digest</h1>

            <div class="date">
                {current_date}
            </div>

            <p>
                Hey {user_name},
            </p>

            <p>
                Here are the AI updates most relevant to you today.
            </p>
    """

    for index, article in enumerate(articles, start=1):

        html += f"""
            <div class="article">

                <h2>
                    {index}. {article.title}
                </h2>

                <p class="summary">
                    {article.summary}
                </p>

                <a
                    class="read-more"
                    href="{article.url}"
                >
                    Read more →
                </a>

            </div>
        """

    html += """
        </div>

    </body>
    </html>
    """

    return html
