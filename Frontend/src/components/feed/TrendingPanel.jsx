export default function TrendingPanel() {
    const trends = [
        "GPT-5 Agents",
        "Claude Code",
        "Gemini 3",
        "OpenAI Browser",
        "AI Robotics",
    ];

    return (
        <div className="bg-[#161b22] rounded-2xl mt-4 p-6">

            <h2 className="text-white text-xl font-bold">
                Trending
            </h2>

            <div className="mt-5 space-y-4">

                {trends.map((trend) => (
                    <div
                        key={trend}
                        className="bg-[#0d1117] text-white p-4 rounded-xl"
                    >
                        🔥 {trend}
                    </div>
                ))}
            </div>

        </div>
    );
}