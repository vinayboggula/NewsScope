import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function MainLayout({ children }) {
    return (
        <div className="flex bg-[#0d1117] min-h-screen">
            <Sidebar />

            <div className="flex-1">
                <Navbar />

                <main className="p-8">{children}</main>
            </div>
        </div>
    );
}