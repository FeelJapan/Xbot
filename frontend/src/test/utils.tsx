import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ReactElement } from 'react'

// テスト用のラッパーコンポーネント
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  )
}

// カスタムレンダリング関数
const customRender = (ui: ReactElement, options = {}) =>
  render(ui, { wrapper: AllTheProviders, ...options })

// テスト用のモックデータ
export const mockData = {
  // ここにモックデータを追加
}

// テスト用のヘルパー関数
export const testUtils = {
  // ここにヘルパー関数を追加
}

export * from '@testing-library/react'
export { customRender as render } 