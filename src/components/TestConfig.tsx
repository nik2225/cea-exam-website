import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Settings, Play } from 'lucide-react';

import type { Question, TestSettings } from '../types';

const TestConfig: React.FC = () => {
  const { subject } = useParams<{ subject: string }>();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [rawTotal, setRawTotal] = useState(0);
  
  const [mode, setMode] = useState<'Full Test' | 'Practice Test' | 'Custom Test'>('Practice Test');
  const [numQuestions, setNumQuestions] = useState(100);
  const [duration, setDuration] = useState(60);
  const [shuffleQuestions, setShuffleQuestions] = useState(true);
  const [shuffleOptions, setShuffleOptions] = useState(true);
  const [negativeMarking, setNegativeMarking] = useState(false);
  const [unansweredZero] = useState(true);

  useEffect(() => {
    if (subject) {
      import('../utils/storage').then(({ getQuestionsBySubject, getAllQuestionsRaw }) => {
        Promise.all([getQuestionsBySubject(subject), getAllQuestionsRaw(subject)]).then(([verifiedQs, allQs]) => {
          setQuestions(verifiedQs);
          setRawTotal(allQs.length);
          setLoading(false);
          
          if (verifiedQs.length < 100) {
            setNumQuestions(verifiedQs.length);
          } else {
            setNumQuestions(100);
          }
        });
      });
    }
  }, [subject]);

  useEffect(() => {
    if (mode === 'Full Test') {
      setNumQuestions(questions.length);
      setDuration(Math.ceil(questions.length * 1.2)); // rough default
    } else if (mode === 'Practice Test') {
      setNumQuestions(Math.min(100, questions.length));
      setDuration(60);
    }
  }, [mode, questions.length]);

  const handleStart = () => {
    if (!subject) return;
    
    const settings: TestSettings = {
      subject,
      mode,
      numberOfQuestions: numQuestions,
      durationMinutes: duration,
      shuffleQuestions,
      shuffleOptions,
      negativeMarking,
      negativeMarksPerWrongAnswer: 0.25,
      unansweredZero
    };
    
    sessionStorage.setItem('test_settings', JSON.stringify(settings));
    sessionStorage.removeItem('test_state'); 
    navigate('/exam');
  };

  if (loading) return <div className="p-10 text-center">Loading questions...</div>;

  const verifiedCount = questions.length;
  const needsReviewCount = rawTotal - verifiedCount;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <button 
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-slate-500 hover:text-slate-800 mb-6 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
        <div className="flex items-center gap-3 mb-6 border-b pb-4">
          <div className="bg-blue-100 p-2 rounded text-blue-600">
            <Settings className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Configure Test</h1>
            <p className="text-slate-500">{subject}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4 mb-8 bg-slate-50 p-4 rounded-xl border border-slate-100">
          <div className="text-center">
            <p className="text-slate-500 text-xs font-bold uppercase mb-1">Total Found</p>
            <p className="text-2xl font-black text-slate-800">{rawTotal}</p>
          </div>
          <div className="text-center border-l border-slate-200">
            <p className="text-emerald-600 text-xs font-bold uppercase mb-1">Verified</p>
            <p className="text-2xl font-black text-emerald-600">{verifiedCount}</p>
          </div>
          <div className="text-center border-l border-slate-200">
            <p className="text-amber-600 text-xs font-bold uppercase mb-1">Needs Review</p>
            <p className="text-2xl font-black text-amber-600">{needsReviewCount}</p>
          </div>
        </div>

        {verifiedCount < 100 && (
           <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-sm">
             <p className="font-bold mb-1">Cannot start default 100-question test.</p>
             <p>This subject only has {verifiedCount} verified questions available. Please use the Admin Validation portal to review and verify more questions.</p>
           </div>
        )}

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Test Mode</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {['Full Test', 'Practice Test', 'Custom Test'].map(m => (
                <button
                  key={m}
                  onClick={() => setMode(m as any)}
                  className={`p-3 rounded-lg border text-sm font-medium transition ${
                    mode === m 
                    ? 'border-blue-500 bg-blue-50 text-blue-700' 
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Number of Questions (Max: {verifiedCount})
              </label>
              <input 
                type="number" 
                value={numQuestions}
                onChange={e => setNumQuestions(Math.min(verifiedCount, Math.max(1, parseInt(e.target.value) || 1)))}
                disabled={mode === 'Full Test'}
                className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-slate-100 disabled:text-slate-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Duration (Minutes)
              </label>
              <input 
                type="number" 
                value={duration}
                onChange={e => setDuration(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t">
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={shuffleQuestions}
                onChange={e => setShuffleQuestions(e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-slate-700">Shuffle Questions</span>
            </label>
            
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={shuffleOptions}
                onChange={e => setShuffleOptions(e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-slate-700">Shuffle Options</span>
            </label>
            
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={negativeMarking}
                onChange={e => setNegativeMarking(e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-slate-700">Enable Negative Marking (-0.25)</span>
            </label>
          </div>
          
          <div className="pt-6 border-t">
            <div className="bg-slate-50 p-4 rounded-lg mb-6 border border-slate-100">
              <h3 className="font-semibold text-slate-800 mb-2">Test Summary</h3>
              <ul className="text-sm text-slate-600 space-y-1">
                <li>• {numQuestions} questions selected from {verifiedCount} available</li>
                <li>• Duration: {duration} minutes</li>
                <li>• Scoring: +1 for correct, {negativeMarking ? '-0.25' : '0'} for incorrect</li>
              </ul>
            </div>
            
            <button 
              onClick={handleStart}
              disabled={verifiedCount === 0 || numQuestions <= 0}
              className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-lg transition flex justify-center items-center gap-2 disabled:bg-slate-300"
            >
              <Play className="w-5 h-5" /> Start Examination
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestConfig;
