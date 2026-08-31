import { Sparkles } from "lucide-react";

export default function FeaturedCard() {
    return (
        <div className="bg-gradient-to-r from-blue-600 to-purple-700 rounded-3xl p-8 mb-8">
            <div className="flex items-center gap-2 text-white">
                <Sparkles size={18} />
                Featured Story
            </div>

            <h1 className="text-4xl font-bold text-white mt-4">
                GPT-5 agents can now complete multi-step tasks
            </h1>

            <p className="text-gray-200 mt-4">
                OpenAI introduces autonomous agents capable of
                reasoning and tool use.
            </p>

            <button className="mt-6 bg-white text-black px-5 py-3 rounded-xl">
                Read article
            </button>
        </div>
    );
}