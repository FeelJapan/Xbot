import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CreatePost from './pages/CreatePost';
import Settings from './pages/Settings';
import { ModernUIDemo } from './pages/ModernUIDemo';

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/create" element={<CreatePost />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/modern-ui" element={<ModernUIDemo />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App; 