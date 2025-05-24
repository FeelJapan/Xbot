import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { DarkModeToggle } from '../components/ui/DarkModeToggle';

export const ModernUIDemo: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div className="
      min-h-screen
      bg-gray-50
      dark:bg-gray-900
      py-12
      px-4
      sm:px-6
      lg:px-8
    ">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="
            text-4xl
            font-bold
            text-gray-900
            dark:text-white
          ">
            モダンなUIデモ
          </h1>
          <DarkModeToggle />
        </div>
        
        <div className="
          grid
          grid-cols-1
          md:grid-cols-2
          lg:grid-cols-3
          gap-6
          mb-12
        ">
          <Card
            title="モダンなカード"
            image="https://picsum.photos/400/300"
          >
            <p className="mb-4">これはモダンなカードコンポーネントのデモです。</p>
            <Button variant="primary">
              詳細を見る
            </Button>
          </Card>
          
          <Card
            title="セカンダリーカード"
            className="bg-gray-50 dark:bg-gray-700"
          >
            <p className="mb-4">異なるスタイルのカードも作成できます。</p>
            <Button variant="secondary">
              アクション
            </Button>
          </Card>
          
          <Card
            title="アウトラインボタン"
          >
            <p className="mb-4">アウトラインスタイルのボタンも使用できます。</p>
            <Button variant="outline">
              クリック
            </Button>
          </Card>
        </div>
        
        <div className="
          max-w-md
          mx-auto
          p-8
          bg-white
          dark:bg-gray-800
          rounded-xl
          shadow-lg
        ">
          <h2 className="
            text-2xl
            font-bold
            text-gray-900
            dark:text-white
            mb-6
          ">
            フォームデモ
          </h2>
          
          <div className="space-y-4">
            <Input
              label="メールアドレス"
              type="email"
              value={email}
              onChange={setEmail}
              placeholder="example@example.com"
              required
            />
            
            <Input
              label="パスワード"
              type="password"
              value={password}
              onChange={setPassword}
              placeholder="パスワードを入力"
              required
            />
            
            <Button
              variant="primary"
              size="lg"
              className="w-full mt-6"
            >
              送信
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}; 