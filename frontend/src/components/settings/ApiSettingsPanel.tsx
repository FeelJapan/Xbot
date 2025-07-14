import React from 'react';

interface ApiSettings {
  xApiKey: string;
  youtubeApiKey: string;
  openaiApiKey: string;
  geminiApiKey: string;
  geminiModel: string;
  geminiMaxTokens: number;
}

interface ApiSettingsPanelProps {
  settings: ApiSettings;
  onChange: (settings: ApiSettings) => void;
}

export const ApiSettingsPanel: React.FC<ApiSettingsPanelProps> = ({
  settings,
  onChange,
}) => {
  const handleChange = (field: keyof ApiSettings, value: string | number) => {
    onChange({ ...settings, [field]: value });
  };

  return (
    <div className="space-y-6">
      <div>
        <label
          htmlFor="xApiKey"
          className="block text-sm font-medium text-gray-700"
        >
          X API Key
        </label>
        <input
          type="password"
          id="xApiKey"
          value={settings.xApiKey}
          onChange={(e) => handleChange('xApiKey', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <div>
        <label
          htmlFor="youtubeApiKey"
          className="block text-sm font-medium text-gray-700"
        >
          YouTube API Key
        </label>
        <input
          type="password"
          id="youtubeApiKey"
          value={settings.youtubeApiKey}
          onChange={(e) => handleChange('youtubeApiKey', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <div>
        <label
          htmlFor="openaiApiKey"
          className="block text-sm font-medium text-gray-700"
        >
          OpenAI API Key
        </label>
        <input
          type="password"
          id="openaiApiKey"
          value={settings.openaiApiKey}
          onChange={(e) => handleChange('openaiApiKey', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <div>
        <label
          htmlFor="geminiApiKey"
          className="block text-sm font-medium text-gray-700"
        >
          Gemini API Key
        </label>
        <input
          type="password"
          id="geminiApiKey"
          value={settings.geminiApiKey}
          onChange={(e) => handleChange('geminiApiKey', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <div>
        <label
          htmlFor="geminiModel"
          className="block text-sm font-medium text-gray-700"
        >
          Gemini Model
        </label>
        <select
          id="geminiModel"
          value={settings.geminiModel}
          onChange={(e) => handleChange('geminiModel', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="gemini-pro">Gemini Pro</option>
          <option value="gemini-pro-vision">Gemini Pro Vision</option>
        </select>
      </div>

      <div>
        <label
          htmlFor="geminiMaxTokens"
          className="block text-sm font-medium text-gray-700"
        >
          Maximum Tokens
        </label>
        <input
          type="number"
          id="geminiMaxTokens"
          value={settings.geminiMaxTokens}
          onChange={(e) => handleChange('geminiMaxTokens', parseInt(e.target.value))}
          min="1"
          max="32768"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>
    </div>
  );
}; 