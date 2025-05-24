import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

interface SettingsFormData {
  x_api_key: string;
  x_api_secret: string;
  x_access_token: string;
  x_access_token_secret: string;
}

export default function Settings() {
  const { register, handleSubmit, formState: { errors } } = useForm<SettingsFormData>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (data: SettingsFormData) => {
    try {
      setIsSubmitting(true);
      // TODO: APIを呼び出して設定を保存
      toast.success('設定を保存しました');
    } catch (error) {
      toast.error('設定の保存に失敗しました');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900">X API設定</h3>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-5 space-y-6">
          <div>
            <label htmlFor="x_api_key" className="block text-sm font-medium text-gray-700">
              API Key
            </label>
            <div className="mt-1">
              <input
                type="password"
                id="x_api_key"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                {...register('x_api_key', { required: 'API Keyを入力してください' })}
              />
              {errors.x_api_key && (
                <p className="mt-2 text-sm text-red-600">{errors.x_api_key.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="x_api_secret" className="block text-sm font-medium text-gray-700">
              API Secret
            </label>
            <div className="mt-1">
              <input
                type="password"
                id="x_api_secret"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                {...register('x_api_secret', { required: 'API Secretを入力してください' })}
              />
              {errors.x_api_secret && (
                <p className="mt-2 text-sm text-red-600">{errors.x_api_secret.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="x_access_token" className="block text-sm font-medium text-gray-700">
              Access Token
            </label>
            <div className="mt-1">
              <input
                type="password"
                id="x_access_token"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                {...register('x_access_token', { required: 'Access Tokenを入力してください' })}
              />
              {errors.x_access_token && (
                <p className="mt-2 text-sm text-red-600">{errors.x_access_token.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="x_access_token_secret" className="block text-sm font-medium text-gray-700">
              Access Token Secret
            </label>
            <div className="mt-1">
              <input
                type="password"
                id="x_access_token_secret"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                {...register('x_access_token_secret', { required: 'Access Token Secretを入力してください' })}
              />
              {errors.x_access_token_secret && (
                <p className="mt-2 text-sm text-red-600">{errors.x_access_token_secret.message}</p>
              )}
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isSubmitting ? '保存中...' : '設定を保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 