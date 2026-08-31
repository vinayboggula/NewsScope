export default function CategoryTabs({
    selectedCategory,
    setSelectedCategory,
}) {
    const categories = [
        "all",
        "openai",
        "youtube",
        "anthropic",
    ];

    return (
        <div className="flex gap-3">
            {categories.map((category) => (
                <button
                    key={category}
                    onClick={() =>
                        setSelectedCategory(category)
                    }
                    className={`px-4 py-2 rounded-xl ${selectedCategory === category
                        ? "bg-blue-600 text-white"
                        : "bg-gray-800 text-gray-400"
                        }`}
                >
                    {category.toUpperCase()}
                </button>
            ))}
        </div>
    );
}