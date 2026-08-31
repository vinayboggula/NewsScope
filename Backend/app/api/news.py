from fastapi import APIRouter, HTTPException
from sqlalchemy import or_

from app.database.connection import get_session
from app.database.models import Digest
from app.database.models import Bookmark
from datetime import datetime


router = APIRouter()


@router.get("/news")
def get_news():
    session = get_session()

    try:
        digests = (
            session.query(Digest)
            .order_by(Digest.created_at.desc())
            .limit(20)
            .all()
        )

        return [
            {
                "id": digest.id,
                "title": digest.title,
                "summary": digest.summary,
                "url": digest.url,
                "source": digest.article_type,
                "created_at": digest.created_at,
            }
            for digest in digests
        ]

    finally:
        session.close()


@router.get("/news/search")
def search_news(q: str):
    session = get_session()

    try:
        digests = (
            session.query(Digest)
            .filter(
                or_(
                    Digest.title.ilike(f"%{q}%"),
                    Digest.summary.ilike(f"%{q}%"),
                )
            )
            .all()
        )

        return [
            {
                "id": digest.id,
                "title": digest.title,
                "summary": digest.summary,
                "url": digest.url,
                "source": digest.article_type,
            }
            for digest in digests
        ]

    finally:
        session.close()


@router.get("/news/{article_id:path}")
def get_article(article_id: str):
    session = get_session()

    try:
        article = (
            session.query(Digest)
            .filter(Digest.id == article_id)
            .first()
        )

        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found"
            )

        return {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "url": article.url,
            "source": article.article_type,
            "created_at": article.created_at,
        }

    finally:
        session.close()
