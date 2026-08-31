import { useEffect, useState } from "react";
import { getNews } from "../services/newsService";

export default function useNews() {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchNews() {
            try {
                const data = await getNews();
                setNews(data);
            } catch (error) {
                console.log(error);
            } finally {
                setLoading(false);
            }
        }

        fetchNews();
    }, []);

    return { news, loading };
}