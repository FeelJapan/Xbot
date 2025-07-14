import React, { useState } from 'react';
import { Tab } from '@headlessui/react';
import { toast } from 'react-hot-toast';
import { settingsClient } from '../api/client';

// タブの定義
const tabs = [
  { id: 'api', name: 'API設定' },
  { id: 'trend', name: 'トレンド分析設定' },
  { id: 'theme', name: '投稿テーマ設定' },
  { id: 'ai', name: '生成AI設定' },
];

// API設定の型定義
interface ApiSettings {
  xApiKey: string;
  youtubeApiKey: string;
  openaiApiKey: string;
  geminiApiKey: string;
}

// トレンド分析設定の型定義
interface TrendSettings {
  searchInterval: number;
  maxResults: number;
  minViewCount: number;
  targetRegions: string[];
}

// 投稿テーマ設定の型定義
interface ThemeSettings {
  categories: string[];
  priority: number;
  seasonalEvents: boolean;
}

// 生成AI設定の型定義
interface AiSettings {
  promptTemplate: string;
  temperature: number;
  maxTokens: number;
  style: string;
}

export const Settings: React.FC = () => {
  // 各設定の状態管理
  const [apiSettings, setApiSettings] = useState<ApiSettings>({
    xApiKey: '',
    youtubeApiKey: '',
    openaiApiKey: '',
    geminiApiKey: '',
  });

  const [trendSettings, setTrendSettings] = useState<TrendSettings>({
    searchInterval: 3600,
    maxResults: 10,
    minViewCount: 10000,
    targetRegions: ['JP', 'US'],
  });

  const [themeSettings, setThemeSettings] = useState<ThemeSettings>({
    categories: ['エンタメ', 'テクノロジー', 'ライフスタイル'],
    priority: 1,
    seasonalEvents: true,
  });

  const [aiSettings, setAiSettings] = useState<AiSettings>({
    promptTemplate: '',
    temperature: 0.7,
    maxTokens: 1000,
    style: 'casual',
  });

  // 設定の保存
  const saveSettings = async () => {
    try {
      await settingsClient.post('/save', {
        api: apiSettings,
        trend: trendSettings,
        theme: themeSettings,
        ai: aiSettings,
      });
      toast.success('設定を保存しました');
    } catch (error) {
      toast.error('設定の保存に失敗しました');
      console.error('設定の保存エラー:', error);
    }
  };

  // 設定の読み込み
  const loadSettings = async () => {
    try {
      const response = await settingsClient.get('/load');
      const { api, trend, theme, ai } = response.data;
      setApiSettings(api);
      setTrendSettings(trend);
      setThemeSettings(theme);
      setAiSettings(ai);
      toast.success('設定を読み込みました');
    } catch (error) {
      toast.error('設定の読み込みに失敗しました');
      console.error('設定の読み込みエラー:', error);
    }
  };

  // コンポーネントのマウント時に設定を読み込む
  React.useEffect(() => {
    loadSettings();
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow rounded-lg">
        <Tab.Group>
          <Tab.List className="flex space-x-1 rounded-t-lg bg-gray-100 p-1">
            {tabs.map((tab) => (
              <Tab
                key={tab.id}
                className={({ selected }) =>
                  `w-full rounded-lg py-2.5 text-sm font-medium leading-5
                  ${
                    selected
                      ? 'bg-white text-blue-700 shadow'
                      : 'text-gray-600 hover:bg-white/[0.12] hover:text-gray-800'
                  }`
                }
              >
                {tab.name}
              </Tab>
            ))}
          </Tab.List>
          <Tab.Panels className="p-4">
            <Tab.Panel>
              <ApiSettingsPanel
                settings={apiSettings}
                onChange={setApiSettings}
              />
            </Tab.Panel>
            <Tab.Panel>
              <TrendSettingsPanel
                settings={trendSettings}
                onChange={setTrendSettings}
              />
            </Tab.Panel>
            <Tab.Panel>
              <ThemeSettingsPanel
                settings={themeSettings}
                onChange={setThemeSettings}
              />
            </Tab.Panel>
            <Tab.Panel>
              <AiSettingsPanel
                settings={aiSettings}
                onChange={setAiSettings}
              />
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>
      </div>

      <div className="mt-6 flex justify-end space-x-4">
        <button
          onClick={loadSettings}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          設定を読み込む
        </button>
        <button
          onClick={saveSettings}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          設定を保存
        </button>
      </div>
    </div>
  );
};

// API設定パネル
const ApiSettingsPanel: React.FC<{
  settings: ApiSettings;
  onChange: (settings: ApiSettings) => void;
}> = ({ settings, onChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">X API Key</label>
        <input
          type="password"
          value={settings.xApiKey}
          onChange={(e) => onChange({ ...settings, xApiKey: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">YouTube API Key</label>
        <input
          type="password"
          value={settings.youtubeApiKey}
          onChange={(e) => onChange({ ...settings, youtubeApiKey: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">OpenAI API Key</label>
        <input
          type="password"
          value={settings.openaiApiKey}
          onChange={(e) => onChange({ ...settings, openaiApiKey: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Gemini API Key</label>
        <input
          type="password"
          value={settings.geminiApiKey}
          onChange={(e) => onChange({ ...settings, geminiApiKey: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
    </div>
  );
};

// トレンド分析設定パネル
const TrendSettingsPanel: React.FC<{
  settings: TrendSettings;
  onChange: (settings: TrendSettings) => void;
}> = ({ settings, onChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">検索間隔（秒）</label>
        <input
          type="number"
          value={settings.searchInterval}
          onChange={(e) => onChange({ ...settings, searchInterval: Number(e.target.value) })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">最大結果数</label>
        <input
          type="number"
          value={settings.maxResults}
          onChange={(e) => onChange({ ...settings, maxResults: Number(e.target.value) })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">最小視聴回数</label>
        <input
          type="number"
          value={settings.minViewCount}
          onChange={(e) => onChange({ ...settings, minViewCount: Number(e.target.value) })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
    </div>
  );
};

// 投稿テーマ設定パネル
const ThemeSettingsPanel: React.FC<{
  settings: ThemeSettings;
  onChange: (settings: ThemeSettings) => void;
}> = ({ settings, onChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">カテゴリー</label>
        <input
          type="text"
          value={settings.categories.join(', ')}
          onChange={(e) => onChange({ ...settings, categories: e.target.value.split(',').map(c => c.trim()) })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">優先度</label>
        <input
          type="number"
          value={settings.priority}
          onChange={(e) => onChange({ ...settings, priority: Number(e.target.value) })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.seasonalEvents}
            onChange={(e) => onChange({ ...settings, seasonalEvents: e.target.checked })}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">季節イベントを考慮する</span>
        </label>
      </div>
    </div>
  );
};

// 生成AI設定パネル
const AiSettingsPanel: React.FC<{
  settings: AiSettings;
  onChange: (settings: AiSettings) => void;
}> = ({ settings, onChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">プロンプトテンプレート</label>
        <textarea
          value={settings.promptTemplate}
          onChange={(e) => onChange({ ...settings, promptTemplate: e.target.value })}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Temperature</label>
        <input
          type="number"
          step="0.1"
          min="0"
          max="1"
          value={settings.temperature}
          onChange={(e) => onChange({ ...settings, temperature: Number(e.target.value) })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">最大トークン数</label>
        <input
          type="number"
          value={settings.maxTokens}
          onChange={(e) => onChange({ ...settings, maxTokens: Number(e.target.value) })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">スタイル</label>
        <select
          value={settings.style}
          onChange={(e) => onChange({ ...settings, style: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="casual">カジュアル</option>
          <option value="formal">フォーマル</option>
          <option value="creative">クリエイティブ</option>
        </select>
      </div>
    </div>
  );
}; 