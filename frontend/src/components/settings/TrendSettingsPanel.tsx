import React from 'react';

interface TrendSettings {
  searchInterval: number;
  maxResults: number;
  minViewCount: number;
  targetRegions: string[];
  keywords: string[];
  categories: string[];
  language: string;
  timeRange: string;
  buzzScoreWeights: {
    viewCount: number;
    engagement: number;
    commentActivity: number;
    channelInfluence: number;
    sentiment: number;
  };
  engagementThreshold: number;
  commentAnalysisDepth: number;
  sentimentAnalysisPrecision: number;
  cacheEnabled: boolean;
  cacheExpiration: number;
  backupEnabled: boolean;
  backupInterval: number;
  dataRetentionDays: number;
  cleanupEnabled: boolean;
}

interface TrendSettingsPanelProps {
  settings: TrendSettings;
  onChange: (settings: TrendSettings) => void;
}

const REGIONS = [
  { code: 'JP', name: '日本' },
  { code: 'US', name: 'アメリカ' },
  { code: 'GB', name: 'イギリス' },
  { code: 'KR', name: '韓国' },
  { code: 'IN', name: 'インド' },
];

const LANGUAGES = [
  { code: 'ja', name: '日本語' },
  { code: 'en', name: '英語' },
  { code: 'ko', name: '韓国語' },
  { code: 'zh', name: '中国語' },
];

const TIME_RANGES = [
  { value: 'day', name: '24時間' },
  { value: 'week', name: '1週間' },
  { value: 'month', name: '1ヶ月' },
];

export const TrendSettingsPanel: React.FC<TrendSettingsPanelProps> = ({
  settings,
  onChange,
}) => {
  const handleChange = (key: keyof TrendSettings, value: any) => {
    onChange({
      ...settings,
      [key]: value,
    });
  };

  const handleRegionToggle = (regionCode: string) => {
    const newRegions = settings.targetRegions.includes(regionCode)
      ? settings.targetRegions.filter((r) => r !== regionCode)
      : [...settings.targetRegions, regionCode];
    handleChange('targetRegions', newRegions);
  };

  const handleKeywordChange = (index: number, value: string) => {
    const newKeywords = [...settings.keywords];
    newKeywords[index] = value;
    handleChange('keywords', newKeywords);
  };

  const handleAddKeyword = () => {
    handleChange('keywords', [...settings.keywords, '']);
  };

  const handleRemoveKeyword = (index: number) => {
    const newKeywords = settings.keywords.filter((_, i) => i !== index);
    handleChange('keywords', newKeywords);
  };

  return (
    <div className="space-y-6">
      {/* 検索条件の設定 */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">検索条件の設定</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              検索間隔（秒）
            </label>
            <input
              type="number"
              value={settings.searchInterval}
              onChange={(e) => handleChange('searchInterval', parseInt(e.target.value))}
              min="60"
              step="60"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              最大検索結果数
            </label>
            <input
              type="number"
              value={settings.maxResults}
              onChange={(e) => handleChange('maxResults', parseInt(e.target.value))}
              min="1"
              max="50"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              最小視聴回数
            </label>
            <input
              type="number"
              value={settings.minViewCount}
              onChange={(e) => handleChange('minViewCount', parseInt(e.target.value))}
              min="0"
              step="1000"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              対象地域
            </label>
            <div className="grid grid-cols-2 gap-4">
              {REGIONS.map((region) => (
                <label key={region.code} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.targetRegions.includes(region.code)}
                    onChange={() => handleRegionToggle(region.code)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">{region.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              キーワード
            </label>
            <div className="space-y-2">
              {settings.keywords.map((keyword, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => handleKeywordChange(index, e.target.value)}
                    className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                  <button
                    onClick={() => handleRemoveKeyword(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    削除
                  </button>
                </div>
              ))}
              <button
                onClick={handleAddKeyword}
                className="text-blue-600 hover:text-blue-800"
              >
                + キーワードを追加
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              言語
            </label>
            <select
              value={settings.language}
              onChange={(e) => handleChange('language', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              期間
            </label>
            <select
              value={settings.timeRange}
              onChange={(e) => handleChange('timeRange', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              {TIME_RANGES.map((range) => (
                <option key={range.value} value={range.value}>
                  {range.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 分析パラメータの調整 */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">分析パラメータの調整</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              バズり度スコアの重み付け
            </label>
            <div className="space-y-2">
              {Object.entries(settings.buzzScoreWeights).map(([key, value]) => (
                <div key={key} className="flex items-center gap-4">
                  <label className="w-32 text-sm text-gray-700">
                    {key === 'viewCount' && '視聴回数'}
                    {key === 'engagement' && 'エンゲージメント'}
                    {key === 'commentActivity' && 'コメント活性度'}
                    {key === 'channelInfluence' && 'チャンネル影響力'}
                    {key === 'sentiment' && '感情分析'}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={value}
                    onChange={(e) => handleChange('buzzScoreWeights', {
                      ...settings.buzzScoreWeights,
                      [key]: parseFloat(e.target.value)
                    })}
                    className="flex-1"
                  />
                  <span className="w-12 text-sm text-gray-700">{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              エンゲージメント率の閾値
            </label>
            <input
              type="number"
              value={settings.engagementThreshold}
              onChange={(e) => handleChange('engagementThreshold', parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.01"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              コメント分析の深さ
            </label>
            <input
              type="number"
              value={settings.commentAnalysisDepth}
              onChange={(e) => handleChange('commentAnalysisDepth', parseInt(e.target.value))}
              min="10"
              max="1000"
              step="10"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              感情分析の精度
            </label>
            <input
              type="number"
              value={settings.sentimentAnalysisPrecision}
              onChange={(e) => handleChange('sentimentAnalysisPrecision', parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.1"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* データ管理設定 */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">データ管理設定</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              キャッシュを有効にする
            </label>
            <input
              type="checkbox"
              checked={settings.cacheEnabled}
              onChange={(e) => handleChange('cacheEnabled', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              キャッシュの有効期限（秒）
            </label>
            <input
              type="number"
              value={settings.cacheExpiration}
              onChange={(e) => handleChange('cacheExpiration', parseInt(e.target.value))}
              min="60"
              step="60"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              バックアップを有効にする
            </label>
            <input
              type="checkbox"
              checked={settings.backupEnabled}
              onChange={(e) => handleChange('backupEnabled', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              バックアップ間隔（秒）
            </label>
            <input
              type="number"
              value={settings.backupInterval}
              onChange={(e) => handleChange('backupInterval', parseInt(e.target.value))}
              min="3600"
              step="3600"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              データ保持期間（日）
            </label>
            <input
              type="number"
              value={settings.dataRetentionDays}
              onChange={(e) => handleChange('dataRetentionDays', parseInt(e.target.value))}
              min="1"
              max="365"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              自動クリーンアップを有効にする
            </label>
            <input
              type="checkbox"
              checked={settings.cleanupEnabled}
              onChange={(e) => handleChange('cleanupEnabled', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}; 