import api from "./api";

export const getNews = async () => {
    const response = await api.get("/news");
    return response.data;
};

export const searchNews = async (query) => {
    const response = await api.get(`/news/search?q=${query}`);
    return response.data;
};

export const getArticle = async (id) => {
    const response = await api.get(
        `/news/${encodeURIComponent(id)}`
    );
    return response.data;
};