
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import TestConfig from './components/TestConfig';
import Examination from './components/Examination';
import ResultReview from './components/ResultReview';
import History from './components/History';
import AdminValidation from './components/AdminValidation';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/setup/:subject" element={<TestConfig />} />
          <Route path="/exam" element={<Examination />} />
          <Route path="/result" element={<ResultReview />} />
          <Route path="/history" element={<History />} />
          <Route path="/admin" element={<AdminValidation />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
