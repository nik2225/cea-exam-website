import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2, Calendar, Clock, Target } from 'lucide-react';
import { getTestHistory, clearTestHistory } from '../utils/storage';
import type { TestResult } from '../types';

const History: React.FC = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<TestResult[]>([]);

  useEffect(() => {
    setHistory(getTestHistory().reverse()); // newest first
  }, []);

  const handleClear = () => {
    if (window.confirm("Are you sure you want to clear all test history? This action cannot be undone.")) {
      clearTestHistory();
      setHistory([]);
    }
  };

  const handleReview = (result: TestResult) => {
    sessionStorage.setItem('last_result', JSON.stringify(result));
    navigate('/result');
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <button 
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition font-medium"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>
        
        {history.length > 0 && (
          <button 
            onClick={handleClear}
            className="flex items-center gap-2 px-4 py-2 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition text-sm font-bold border border-red-100"
          >
            <Trash2 className="w-4 h-4" /> Clear History
          </button>
        )}
      </div>

      <h1 className="text-3xl font-bold text-slate-900 mb-8">Test History</h1>

      {history.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center shadow-sm">
          <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-full flex justify-center items-center mx-auto mb-4">
            <Calendar className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">No tests taken yet</h2>
          <p className="text-slate-500 mb-6 max-w-md mx-auto">Your completed tests will appear here. Start practicing to track your progress over time.</p>
          <button 
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition"
          >
            Go to Dashboard
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((h, i) => (
            <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center gap-6 hover:shadow-md transition">
              <div className="flex-1 w-full">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-lg text-slate-900">{h.settings.subject}</h3>
                  <span className="text-sm font-medium px-2 py-1 bg-slate-100 text-slate-600 rounded">
                    {h.settings.mode}
                  </span>
                </div>
                <div className="flex flex-wrap gap-4 text-sm text-slate-500">
                  <div className="flex items-center gap-1"><Calendar className="w-4 h-4" /> {new Date(h.date).toLocaleString()}</div>
                  <div className="flex items-center gap-1"><Clock className="w-4 h-4" /> {Math.floor(h.timeTakenSeconds / 60)}m {h.timeTakenSeconds % 60}s</div>
                  <div className="flex items-center gap-1"><Target className="w-4 h-4" /> {h.totalQuestions} Qs</div>
                </div>
              </div>
              
              <div className="flex items-center gap-8 w-full md:w-auto border-t md:border-t-0 pt-4 md:pt-0">
                <div className="text-center">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Score</p>
                  <p className="text-xl font-black text-slate-800">{h.totalMarks}<span className="text-sm text-slate-500">/{h.maxMarks}</span></p>
                </div>
                
                <div className="text-center">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Percentage</p>
                  <p className={`text-xl font-black ${h.percentage >= 75 ? 'text-emerald-600' : h.percentage >= 50 ? 'text-amber-500' : 'text-red-500'}`}>
                    {h.percentage.toFixed(1)}%
                  </p>
                </div>
                
                <button 
                  onClick={() => handleReview(h)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 bg-white rounded-lg hover:bg-slate-50 font-bold transition whitespace-nowrap ml-auto"
                >
                  Review
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
