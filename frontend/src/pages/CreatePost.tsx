import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface PostFormData {
  content: string;
  scheduled_time: string;
}

export default function CreatePost() {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors }, setValue } = useForm<PostFormData>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('検索キーワードを入力してください');
      return;
    }

    try {
      setIsSearching(true);
      // TODO: ChatGPT APIを呼び出して検索
      const response = await fetch('http://localhost:8000/api/v1/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        throw new Error('検索に失敗しました');
      }

      const data = await response.json();
      setValue('content', data.content);
      toast.success('投稿内容を生成しました');
    } catch (error) {
      toast.error('検索に失敗しました');
    } finally {
      setIsSearching(false);
    }
  };

  const onSubmit = async (data: PostFormData) => {
    try {
      setIsSubmitting(true);
      // TODO: APIを呼び出して投稿を作成
      toast.success('投稿を予約しました');
      navigate('/');
    } catch (error) {
      toast.error('投稿の予約に失敗しました');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900">新規投稿の作成</h3>
        
        {/* 検索フォーム */}
        <div className="mt-5">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700">
            ChatGPTで投稿内容を検索
          </label>
          <div className="mt-1 flex rounded-md shadow-sm">
            <input
              type="text"
              id="search"
              className="block w-full rounded-l-md border-gray-300 focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              placeholder="検索キーワードを入力..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button
              type="button"
              onClick={handleSearch}
              disabled={isSearching}
              className="inline-flex items-center rounded-r-md border border-l-0 border-gray-300 bg-gray-50 px-3 text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              <MagnifyingGlassIcon className="h-5 w-5" />
              {isSearching ? '検索中...' : '検索'}
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-5 space-y-6">
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700">
              投稿内容
            </label>
            <div className="mt-1">
              <textarea
                id="content"
                rows={4}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                {...register('content', { required: '投稿内容を入力してください' })}
              />
              {errors.content && (
                <p className="mt-2 text-sm text-red-600">{errors.content.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="scheduled_time" className="block text-sm font-medium text-gray-700">
              投稿予定時刻
            </label>
            <div className="mt-1">
              <input
                type="datetime-local"
                id="scheduled_time"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                {...register('scheduled_time', { required: '投稿予定時刻を選択してください' })}
              />
              {errors.scheduled_time && (
                <p className="mt-2 text-sm text-red-600">{errors.scheduled_time.message}</p>
              )}
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isSubmitting ? '送信中...' : '投稿を予約'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 