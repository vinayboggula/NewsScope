import { articles } from "../../assets/articles";
import NewsCard from "./NewsCard";

export default function Feed() {
    return (
        <div className="space-y-5">
            {articles.map((article) => (
                <NewsCard key={article.id} article={article} />
            ))}
        </div>
    );
}