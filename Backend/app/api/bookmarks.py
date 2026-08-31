from fastapi import APIRouter, HTTPException

from app.database.connection import get_session
from app.database.models import Bookmark

router = APIRouter()


@router.post("/bookmarks/{article_id}")
def save_bookmark(article_id: str):
    session = get_session()

    try:
        existing = (
            session.query(Bookmark)
            .filter(Bookmark.article_id == article_id)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Article already bookmarked"
            )

        bookmark = Bookmark(article_id=article_id)

        session.add(bookmark)
        session.commit()

        return {"message": "Bookmark saved"}

    finally:
        session.close()


@router.get("/bookmarks")
def get_bookmarks():
    session = get_session()

    try:
        bookmarks = (
            session.query(Bookmark)
            .order_by(Bookmark.created_at.desc())
            .all()
        )

        return [
            {
                "id": bookmark.id,
                "article_id": bookmark.article_id,
                "created_at": bookmark.created_at,
            }
            for bookmark in bookmarks
        ]

    finally:
        session.close()


@router.delete("/bookmarks/{article_id}")
def delete_bookmark(article_id: str):
    session = get_session()

    try:
        bookmark = (
            session.query(Bookmark)
            .filter(
                Bookmark.article_id == article_id
            )
            .first()
        )

        if not bookmark:
            raise HTTPException(
                status_code=404,
                detail="Bookmark not found"
            )

        session.delete(bookmark)
        session.commit()

        return {
            "message": "Bookmark deleted"
        }

    finally:
        session.close()
