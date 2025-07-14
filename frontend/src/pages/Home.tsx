import React from 'react';
import { Link } from 'react-router-dom';

export const Home: React.FC = () => {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Xbotへようこそ
        </h1>
        <p className="text-xl text-gray-600">
          AIを活用したX（旧Twitter）自動投稿システム
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/trend-search"
          className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            投稿ネタ検索
          </h2>
          <p className="text-gray-600">
            YouTubeのトレンドを分析し、バズりそうなネタを見つけましょう
          </p>
        </Link>

        <Link
          to="/post-creation"
          className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            投稿作成
          </h2>
          <p className="text-gray-600">
            AIを活用して、面白くて共感できる投稿を作成しましょう
          </p>
        </Link>

        <Link
          to="/settings"
          className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            設定
          </h2>
          <p className="text-gray-600">
            システムの設定をカスタマイズして、より良い投稿を目指しましょう
          </p>
        </Link>
      </div>
    </div>
  );
}; 