import { BrowserRouter, Route, Routes } from "react-router-dom";

import Dashboard from "../src/pages/Dashboard";
import Explore from "../src/pages/Explore";
import Saved from "../src/pages/Saved";
import Settings from "../src/pages/Settings";
import ArticleDetails from "./pages/ArticleDetails";
import Bookmarks from "./pages/Bookmarks";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/news/:id" element={<ArticleDetails />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/saved" element={<Saved />} />
        <Route path="/settings" element={<Settings />} />
        <Route
          path="/bookmarks"
          element={<Bookmarks />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;