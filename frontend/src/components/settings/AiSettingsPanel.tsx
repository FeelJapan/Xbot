import React from 'react';

interface AiSettings {
  promptTemplate: string;
  temperature: number;
  maxTokens: number;
  style: string;
}

interface AiSettingsPanelProps {
  settings: AiSettings;
  onChange: (settings: AiSettings) => void;
}

const STYLES = [
  { value: 'casual', label: 'カジュアル' },
  { value: 'professional', label: 'プロフェッショナル' },
  { value: 'humorous', label: 'ユーモア' },
  { value: 'informative', label: '情報提供' },
  { value: 'emotional', label: '感情表現' },
];

export const AiSettingsPanel: React.FC<AiSettingsPanelProps> = ({
  settings,
  onChange,
}) => {
  const handleChange = (key: keyof AiSettings, value: any) => {
    onChange({
      ...settings,
      [key]: value,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <label
          htmlFor="promptTemplate"
          className="block text-sm font-medium text-gray-700"
        >
          プロンプトテンプレート
        </label>
        <textarea
          id="promptTemplate"
          value={settings.promptTemplate}
          onChange={(e) => handleChange('promptTemplate', e.target.value)}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="例: 以下のトピックについて、{style}な文体で、{maxLength}文字以内の投稿を作成してください。"
        />
      </div>

      <div>
        <label
          htmlFor="temperature"
          className="block text-sm font-medium text-gray-700"
        >
          温度（創造性）
        </label>
        <input
          type="range"
          id="temperature"
          min="0"
          max="1"
          step="0.1"
          value={settings.temperature}
          onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          className="mt-1 block w-full"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>より確実</span>
          <span>より創造的</span>
        </div>
      </div>

      <div>
        <label
          htmlFor="maxTokens"
          className="block text-sm font-medium text-gray-700"
        >
          最大トークン数
        </label>
        <input
          type="number"
          id="maxTokens"
          value={settings.maxTokens}
          onChange={(e) => handleChange('maxTokens', parseInt(e.target.value))}
          min="100"
          max="4000"
          step="100"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <div>
        <label
          htmlFor="style"
          className="block text-sm font-medium text-gray-700"
        >
          文体スタイル
        </label>
        <select
          id="style"
          value={settings.style}
          onChange={(e) => handleChange('style', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          {STYLES.map((style) => (
            <option key={style.value} value={style.value}>
              {style.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}; 