import api from "./api";

export const saveBookmark = async (articleId) => {
    try {
        const response = await api.post(
            `/bookmarks/${encodeURIComponent(articleId)}`
        );

        return response.data;
    } catch (error) {
        console.error("Error saving bookmark:", error);
    }
};

export const getBookmarks = async () => {
    try {
        const response = await api.get("/bookmarks");
        return response.data;
    } catch (error) {
        console.error("Error fetching bookmarks:", error);
    }
};