export default function Navbar({ searchTerm, setSearchTerm }) {
    return (
        <nav className="bg-[#0d1117] p-4 border-b border-gray-800">
            <input
                type="text"
                placeholder="Search GPT, Gemini, Claude..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-[#161b22] text-white px-4 py-2 rounded-xl outline-none"
            />
        </nav>
    );
}