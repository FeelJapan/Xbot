/// <reference types="vite/client" />
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// トレンド分析サービスのクライアント
export const trendAnalysisClient = axios.create({
  baseURL: `${API_BASE_URL}/trend-analysis`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 生成AIサービスのクライアント
export const aiGenerationClient = axios.create({
  baseURL: `${API_BASE_URL}/ai-generation`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 設定管理サービスのクライアント
export const settingsClient = axios.create({
  baseURL: `${API_BASE_URL}/settings`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// X投稿サービスのクライアント
export const xPostingClient = axios.create({
  baseURL: `${API_BASE_URL}/x-posting`,
  headers: {
    'Content-Type': 'application/json',
  },
}); 