import { useNavigate } from "react-router-dom";
import { saveBookmark } from "../../services/bookmarkService";

export default function NewsCard({ article }) {
    const navigate = useNavigate();

    const sourceColors = {
        openai: "text-green-400",
        youtube: "text-red-400",
        anthropic: "text-orange-400",
    };

    return (
        <div
            className="cursor-pointer bg-[#161b22] p-6 rounded-2xl border border-gray-800 hover:border-blue-500 transition"
            onClick={() =>
                navigate(`/news/${encodeURIComponent(article.id)}`)
            }
        >
            <div className="flex justify-between items-center">
                <span
                    className={`${sourceColors[article.source]} font-semibold`}
                >
                    {article.source.toUpperCase()}
                </span>

                <span className="text-gray-500 text-xs">
                    {new Date(article.created_at).toLocaleDateString()}
                </span>
            </div>

            <h2 className="text-white text-xl font-bold mt-4">
                {article.title}
            </h2>

            <p className="text-gray-400 mt-3 line-clamp-3">
                {article.summary}
            </p>
            <button
                onClick={(e) => {
                    e.stopPropagation();
                    saveBookmark(article.id);
                }}
                className="mt-4 mr-4 px-2 py-1 bg-amber-50 text-black rounded-lg hover:bg-yellow-400"
            >
                ⭐
            </button>

            <a
                href={article.url}
                target="_blank"
                rel="noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-blue-400 mt-4 inline-block"
            >
                Read more →
            </a>
        </div>
    );
}