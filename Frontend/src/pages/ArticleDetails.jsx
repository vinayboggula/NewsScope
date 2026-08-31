import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getArticle } from "../services/newsService";

export default function ArticleDetails() {
    const { id } = useParams();

    const [article, setArticle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        console.log("Current pathname:", window.location.pathname);
    }, []);
    useEffect(() => {
        async function fetchArticle() {
            try {
                console.log("ID:", id);

                const data = await getArticle(id);

                console.log("Received data:", data);

                setArticle(data);
            } catch (err) {
                console.error(err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        fetchArticle();
    }, [id]);
    if (loading) {
        return <h1>Loading...</h1>;
    }

    if (error) {
        return <h1 className="text-red-500">{error}</h1>;
    }

    if (!article) {
        return <h1>Article not found</h1>;
    }

    return (
        <div className="min-h-screen bg-black text-white p-10">
            <h1 className="text-4xl">{article?.title}</h1>

            <p className="mt-6">{article?.summary}</p>

            <p className="mt-6 text-red-500">
                Source: {article?.source}
            </p>

            <a
                href={article?.url}
                target="_blank"
                rel="noreferrer"
                className="text-blue-400"
            >
                Open article
            </a>
        </div>
    );
}