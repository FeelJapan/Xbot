import { useState } from 'react';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';

interface Post {
  id: number;
  content: string;
  scheduled_time: string;
  posted: boolean;
}

export default function Dashboard() {
  const [posts, _] = useState<Post[]>([]);

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900">予定された投稿</h3>
        <div className="mt-5">
          {posts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">予定された投稿はありません</p>
            </div>
          ) : (
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">投稿内容</th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">予定時刻</th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">ステータス</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {posts.map((post) => (
                    <tr key={post.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">{post.content}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {format(new Date(post.scheduled_time), 'yyyy年MM月dd日 HH:mm', { locale: ja })}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm">
                        <span
                          className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                            post.posted
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {post.posted ? '投稿済み' : '予定'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 