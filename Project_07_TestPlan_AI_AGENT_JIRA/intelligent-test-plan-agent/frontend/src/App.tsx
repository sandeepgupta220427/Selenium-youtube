import { Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import { MainLayout } from '@/components/MainLayout';
import Dashboard from '@/pages/Dashboard';
import Settings from '@/pages/Settings';
import History from '@/pages/History';

function App() {
  return (
    <>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </MainLayout>
      <Toaster />
    </>
  );
}

export default App;
