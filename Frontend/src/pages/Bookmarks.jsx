import { useEffect, useState } from "react";
import NewsCard from "../components/feed/NewsCard";
import { getBookmarks } from "../services/bookmarkService";

export default function Bookmarks() {
    const [bookmarks, setBookmarks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchBookmarks() {
            try {
                const data = await getBookmarks();
                setBookmarks(data);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        }

        fetchBookmarks();
    }, []);

    if (loading) {
        return <h1 className="text-white">Loading...</h1>;
    }

    return (
        <div className="min-h-screen bg-[#0d1117] p-6">
            <h1 className="text-3xl text-white font-bold mb-6">
                ⭐ Bookmarks
            </h1>

            <div className="space-y-6">
                {bookmarks.map((bookmark) => (
                    <NewsCard
                        key={bookmark.article_id}
                        article={bookmark}
                    />
                ))}
            </div>
        </div>
    );
}