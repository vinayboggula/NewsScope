import {
    Bookmark,
    Compass,
    LayoutDashboard,
    Settings,
} from "lucide-react";

import { NavLink } from "react-router-dom";
const items = [
    {
        icon: LayoutDashboard,
        label: "Dashboard",
        path: "/",
    },
    {
        icon: Compass,
        label: "Explore",
        path: "/explore",
    },
    {
        icon: Bookmark,
        label: "Saved",
        path: "/bookmarks",
    },
    {
        icon: Settings,
        label: "Settings",
        path: "/settings",
    },
];

export default function Sidebar() {
    return (
        <aside className="w-20 lg:w-64 bg-[#0d1117] border-r border-gray-800 h-screen p-5">
            <h1 className="text-white text-2xl font-bold hidden lg:block">
                PulseAI
            </h1>

            <div className="mt-12 space-y-4">
                {items.map((item) => {
                    const Icon = item.icon;

                    return (
                        <NavLink
                            key={item.label}
                            to={item.path}
                            className={({ isActive }) =>
                                `w-full flex items-center gap-4 p-4 rounded-xl transition ${isActive
                                    ? "bg-blue-600 text-white"
                                    : "text-gray-400 hover:bg-[#161b22] hover:text-white"
                                }`
                            }
                        >
                            <Icon size={20} />

                            <span className="hidden lg:block">
                                {item.label}
                            </span>
                        </NavLink>
                    );
                })}
            </div>
        </aside>
    );
}