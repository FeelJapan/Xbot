import { describe, it, expect, beforeEach, vi } from 'vitest';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Settings } from '../Settings';
import { settingsClient } from '../../api/client';
import { toast } from 'react-hot-toast';

// モックの設定
vi.mock('../../api/client', () => ({
  settingsClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock('react-hot-toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('Settings', () => {
  const mockSettings = {
    api: {
      xApiKey: 'test-x-api-key',
      youtubeApiKey: 'test-youtube-api-key',
      openaiApiKey: 'test-openai-api-key',
      geminiApiKey: 'test-gemini-api-key',
    },
    trend: {
      searchInterval: 3600,
      maxResults: 10,
      minViewCount: 10000,
      targetRegions: ['JP', 'US'],
    },
    theme: {
      categories: ['エンタメ', 'テクノロジー'],
      priority: 1,
      seasonalEvents: true,
    },
    ai: {
      promptTemplate: 'test template',
      temperature: 0.7,
      maxTokens: 1000,
      style: 'casual',
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (settingsClient.get as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockSettings });
  });

  it('初期表示時に設定を読み込む', async () => {
    render(<Settings />);
    
    await waitFor(() => {
      expect(settingsClient.get).toHaveBeenCalledWith('/load');
    });

    // API設定の確認
    expect(screen.getByLabelText('X API Key')).toHaveValue(mockSettings.api.xApiKey);
    expect(screen.getByLabelText('YouTube API Key')).toHaveValue(mockSettings.api.youtubeApiKey);
    expect(screen.getByLabelText('OpenAI API Key')).toHaveValue(mockSettings.api.openaiApiKey);
    expect(screen.getByLabelText('Gemini API Key')).toHaveValue(mockSettings.api.geminiApiKey);

    // トレンド設定の確認
    expect(screen.getByLabelText('検索間隔（秒）')).toHaveValue(mockSettings.trend.searchInterval);
    expect(screen.getByLabelText('最大検索結果数')).toHaveValue(mockSettings.trend.maxResults);
    expect(screen.getByLabelText('最小視聴回数')).toHaveValue(mockSettings.trend.minViewCount);

    // テーマ設定の確認
    mockSettings.theme.categories.forEach(category => {
      expect(screen.getByLabelText(category)).toBeChecked();
    });
    expect(screen.getByLabelText('優先度')).toHaveValue(mockSettings.theme.priority.toString());
    expect(screen.getByLabelText('季節イベントを考慮する')).toBeChecked();

    // AI設定の確認
    expect(screen.getByLabelText('プロンプトテンプレート')).toHaveValue(mockSettings.ai.promptTemplate);
    expect(screen.getByLabelText('温度（創造性）')).toHaveValue(mockSettings.ai.temperature.toString());
    expect(screen.getByLabelText('最大トークン数')).toHaveValue(mockSettings.ai.maxTokens.toString());
    expect(screen.getByLabelText('文体スタイル')).toHaveValue(mockSettings.ai.style);
  });

  it('設定の保存が成功する', async () => {
    (settingsClient.post as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({});
    render(<Settings />);

    await waitFor(() => {
      expect(settingsClient.get).toHaveBeenCalledWith('/load');
    });

    fireEvent.click(screen.getByText('設定を保存'));

    await waitFor(() => {
      expect(settingsClient.post).toHaveBeenCalledWith('/save', mockSettings);
      expect(toast.success).toHaveBeenCalledWith('設定を保存しました');
    });
  });

  it('設定の保存が失敗する', async () => {
    const error = new Error('保存に失敗しました');
    (settingsClient.post as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(error);
    render(<Settings />);

    await waitFor(() => {
      expect(settingsClient.get).toHaveBeenCalledWith('/load');
    });

    fireEvent.click(screen.getByText('設定を保存'));

    await waitFor(() => {
      expect(settingsClient.post).toHaveBeenCalledWith('/save', mockSettings);
      expect(toast.error).toHaveBeenCalledWith('設定の保存に失敗しました');
    });
  });

  it('設定の再読み込みが成功する', async () => {
    render(<Settings />);

    await waitFor(() => {
      expect(settingsClient.get).toHaveBeenCalledWith('/load');
    });

    fireEvent.click(screen.getByText('設定を読み込む'));

    await waitFor(() => {
      expect(settingsClient.get).toHaveBeenCalledTimes(2);
      expect(toast.success).toHaveBeenCalledWith('設定を読み込みました');
    });
  });

  it('設定の再読み込みが失敗する', async () => {
    const error = new Error('読み込みに失敗しました');
    (settingsClient.get as unknown as ReturnType<typeof vi.fn>).mockRejectedValueOnce(error);
    render(<Settings />);

    await waitFor(() => {
      expect(settingsClient.get).toHaveBeenCalledWith('/load');
      expect(toast.error).toHaveBeenCalledWith('設定の読み込みに失敗しました');
    });
  });
}); 