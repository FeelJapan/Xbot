// import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layouts/MainLayout';
import { Home } from './pages/Home';
import { Toaster } from 'react-hot-toast';
import { Settings } from './pages/Settings';
import { HeroUIProvider } from "@heroui/react";

function App() {
  return (
    <HeroUIProvider>
      <Router>
        <Toaster position="top-right" />
        <MainLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/trend-search" element={<div>投稿ネタ検索（実装予定）</div>} />
            <Route path="/post-creation" element={<div>投稿作成（実装予定）</div>} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </MainLayout>
      </Router>
    </HeroUIProvider>
  );
}

export default App; 