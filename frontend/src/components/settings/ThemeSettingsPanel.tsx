import React from 'react';

interface ThemeSettings {
  categories: string[];
  priority: number;
  seasonalEvents: boolean;
}

interface ThemeSettingsPanelProps {
  settings: ThemeSettings;
  onChange: (settings: ThemeSettings) => void;
}

const CATEGORIES = [
  'エンタメ',
  'テクノロジー',
  'ライフスタイル',
  'スポーツ',
  'ニュース',
  'グルメ',
  'ファッション',
  '旅行',
  '音楽',
  'アニメ',
  'ゲーム',
  '教育',
];

export const ThemeSettingsPanel: React.FC<ThemeSettingsPanelProps> = ({
  settings,
  onChange,
}) => {
  const handleChange = (key: keyof ThemeSettings, value: any) => {
    onChange({
      ...settings,
      [key]: value,
    });
  };

  const handleCategoryToggle = (category: string) => {
    const newCategories = settings.categories.includes(category)
      ? settings.categories.filter((c) => c !== category)
      : [...settings.categories, category];
    handleChange('categories', newCategories);
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          カテゴリ
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {CATEGORIES.map((category) => (
            <label
              key={category}
              className="inline-flex items-center"
            >
              <input
                type="checkbox"
                checked={settings.categories.includes(category)}
                onChange={() => handleCategoryToggle(category)}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">{category}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label
          htmlFor="priority"
          className="block text-sm font-medium text-gray-700"
        >
          優先度
        </label>
        <select
          id="priority"
          value={settings.priority}
          onChange={(e) => handleChange('priority', parseInt(e.target.value))}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value={1}>低</option>
          <option value={2}>中</option>
          <option value={3}>高</option>
        </select>
      </div>

      <div>
        <label className="inline-flex items-center">
          <input
            type="checkbox"
            checked={settings.seasonalEvents}
            onChange={(e) => handleChange('seasonalEvents', e.target.checked)}
            className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">
            季節イベントを考慮する
          </span>
        </label>
      </div>
    </div>
  );
}; 