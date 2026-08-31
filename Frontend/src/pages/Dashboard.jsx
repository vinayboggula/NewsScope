import { motion } from "framer-motion";
import { useEffect, useState } from "react";

import Navbar from "../components/Layout/Navbar";
import Sidebar from "../components/Layout/Sidebar";

import CategoryTabs from "../components/feed/CategoryTabs";
import FeaturedCard from "../components/feed/FeaturedCard";
import NewsCard from "../components/feed/NewsCard";
import TrendingPanel from "../components/feed/TrendingPanel";

import { getNews } from "../services/newsService";

export default function Dashboard() {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [selectedCategory, setSelectedCategory] = useState("all");
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        async function fetchNews() {
            try {
                const data = await getNews();

                console.log(data); // Check this

                setArticles(data);
            } catch (err) {
                setError(err.message);
                console.error(err);
            } finally {
                setLoading(false);
            }
        }

        fetchNews();
    }, []);

    const filteredArticles = (articles || []).filter((article) => {
        const matchesCategory =
            selectedCategory === "all" ||
            article.source === selectedCategory;

        const matchesSearch =
            article.title
                .toLowerCase()
                .includes(searchTerm.toLowerCase()) ||
            article.summary
                .toLowerCase()
                .includes(searchTerm.toLowerCase());

        return matchesCategory && matchesSearch;
    });

    return (
        <div className="flex h-screen bg-[#0d1117]">
            <Sidebar />

            <div className="flex-1 flex flex-col overflow-hidden">
                <Navbar
                    searchTerm={searchTerm}
                    setSearchTerm={setSearchTerm}
                />

                <div className="grid grid-cols-12 flex-1 overflow-hidden">
                    {/* Left section */}
                    <div className="col-span-8 overflow-y-auto hide-scrollbar p-6 space-y-6">
                        <FeaturedCard />

                        <CategoryTabs
                            selectedCategory={selectedCategory}
                            setSelectedCategory={setSelectedCategory}
                        />

                        {/* Loading */}
                        {loading && (
                            <h2 className="text-white text-center">
                                Loading...
                            </h2>
                        )}

                        {/* Error */}
                        {error && (
                            <h2 className="text-red-500 text-center">
                                {error}
                            </h2>
                        )}

                        {/* Empty state */}
                        {!loading &&
                            !error &&
                            filteredArticles.length === 0 && (
                                <h2 className="text-gray-400 text-center">
                                    No articles found.
                                </h2>
                            )}

                        {/* Articles */}
                        <div className="space-y-6">
                            {filteredArticles.map((article) => (
                                <motion.div
                                    key={article.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.4 }}
                                >
                                    <NewsCard article={article} />
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    {/* Right section */}
                    <div className="col-span-4 border-l border-gray-800 overflow-y-auto hide-scrollbar p-6">
                        <TrendingPanel />
                    </div>
                </div>
            </div>
        </div>
    );
}