import axios from 'axios';

// APIクライアントの設定
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// トレンド分析API
export const trendApi = {
  searchVideos: async (query: string) => {
    const response = await apiClient.get('/trend-analysis/search', { params: { query } });
    return response.data;
  },
  getTrends: async () => {
    const response = await apiClient.get('/trend-analysis/trends');
    return response.data;
  },
};

// コンテンツ生成API
export const contentApi = {
  generateText: async (prompt: string) => {
    const response = await apiClient.post('/content-generation/text', { prompt });
    return response.data;
  },
  generateImage: async (prompt: string) => {
    const response = await apiClient.post('/content-generation/image', { prompt });
    return response.data;
  },
};

// 投稿管理API
export const postApi = {
  createPost: async (content: any) => {
    const response = await apiClient.post('/post-management/posts', content);
    return response.data;
  },
  schedulePost: async (postId: string, scheduleTime: string) => {
    const response = await apiClient.post(`/post-management/posts/${postId}/schedule`, { scheduleTime });
    return response.data;
  },
};

export default apiClient; 