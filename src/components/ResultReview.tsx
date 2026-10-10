import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, XCircle, AlertCircle, ArrowLeft, RotateCcw, Home, Eye } from 'lucide-react';
import type { TestResult } from '../types';

const ResultReview: React.FC = () => {
  const navigate = useNavigate();
  const [result, setResult] = useState<TestResult | null>(null);
  
  // States for reviewing
  const [reviewMode, setReviewMode] = useState<'all' | 'incorrect' | 'unanswered' | null>(null);
  const [reviewIndex, setReviewIndex] = useState(0);

  useEffect(() => {
    const resStr = sessionStorage.getItem('last_result');
    if (!resStr) {
      navigate('/');
      return;
    }
    setResult(JSON.parse(resStr));
  }, [navigate]);

  if (!result) return <div className="p-10 text-center">Loading Result...</div>;

  const startReview = (mode: 'all' | 'incorrect' | 'unanswered') => {
    setReviewMode(mode);
    setReviewIndex(0);
  };

  const getReviewQuestions = () => {
    if (reviewMode === 'all') return result.questions;
    if (reviewMode === 'incorrect') {
      return result.questions.filter(q => {
        const ans = result.answers[q.id];
        return ans.selectedOptionIndex !== null && ans.originalOptionIndices[ans.selectedOptionIndex] !== q.correctAnswerIndex;
      });
    }
    if (reviewMode === 'unanswered') {
      return result.questions.filter(q => result.answers[q.id].selectedOptionIndex === null);
    }
    return [];
  };

  const reviewQs = getReviewQuestions();

  if (reviewMode && reviewQs.length > 0) {
    const q = reviewQs[reviewIndex];
    const ans = result.answers[q.id];
    
    // In review mode, we need to find the shuffled options if we want to show exactly what they saw,
    // or just show original options. The requirement says:
    // "For every reviewed question, show: Exact question, All four options, Candidate's selected answer, Correct answer, Correct/Incorrect/Unanswered status, Explanation if available"
    // We should show the options in their ORIGINAL order, but indicate what they selected.
    
    let statusText = 'Unanswered';
    let statusColor = 'text-slate-500';
    
    let selectedOriginalIdx = -1;
    if (ans.selectedOptionIndex !== null) {
      selectedOriginalIdx = ans.originalOptionIndices[ans.selectedOptionIndex];
      if (selectedOriginalIdx === q.correctAnswerIndex) {
        statusText = 'Correct';
        statusColor = 'text-emerald-600';
      } else {
        statusText = 'Incorrect';
        statusColor = 'text-red-600';
      }
    }

    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <button 
            onClick={() => setReviewMode(null)}
            className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition font-medium"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Summary
          </button>
          <div className="font-semibold text-slate-700">
            Reviewing {reviewMode === 'all' ? 'All' : reviewMode === 'incorrect' ? 'Incorrect' : 'Unanswered'} ({reviewIndex + 1} of {reviewQs.length})
          </div>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex justify-between items-start mb-6 pb-4 border-b">
            <h2 className="text-xl font-bold text-slate-800">Question {q.originalQuestionNumber}</h2>
            <div className={`px-3 py-1 rounded-full text-sm font-bold bg-opacity-10 border ${statusColor} border-current`}>
              {statusText}
            </div>
          </div>
          
          <div className="text-lg text-slate-800 mb-8 whitespace-pre-wrap font-medium">
            {q.questionText}
          </div>

          {q.hasDiagram && q.diagramPath && (
            <div className="mb-8 rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-white">
              <div className="bg-slate-100 p-2 text-xs font-bold text-slate-500 uppercase flex justify-between">
                <span>Reference Image</span>
                <span>Source: {q.sourcePdf} (Page {q.sourcePage})</span>
              </div>
              <img 
                src={q.diagramPath} 
                alt="Question Reference"
                className="w-full h-auto object-contain"
              />
            </div>
          )}
          
          <div className="space-y-3 mb-8">
            {q.options.map((opt, idx) => {
              const isCorrect = idx === q.correctAnswerIndex;
              const isSelected = idx === selectedOriginalIdx;
              
              let classes = "p-4 border rounded-xl flex justify-between items-center ";
              if (isCorrect) {
                classes += "border-emerald-500 bg-emerald-50";
              } else if (isSelected && !isCorrect) {
                classes += "border-red-500 bg-red-50";
              } else {
                classes += "border-slate-200";
              }
              
              return (
                <div key={idx} className={classes}>
                  <div className="flex items-center gap-3">
                    <span className="font-bold w-6 h-6 rounded-full bg-white border flex justify-center items-center text-sm shadow-sm">
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span className="text-slate-700">{opt}</span>
                  </div>
                  
                  {isCorrect && <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />}
                  {isSelected && !isCorrect && <XCircle className="w-5 h-5 text-red-500 shrink-0" />}
                </div>
              );
            })}
          </div>

          {q.explanation && (
            <div className="p-4 bg-blue-50 rounded-xl border border-blue-100 text-blue-900 mb-8">
              <span className="font-bold block mb-1">Explanation:</span>
              {q.explanation}
            </div>
          )}

          <div className="flex justify-between border-t pt-6">
            <button 
              onClick={() => setReviewIndex(i => Math.max(0, i - 1))}
              disabled={reviewIndex === 0}
              className="px-6 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition disabled:opacity-50 font-medium"
            >
              Previous
            </button>
            <button 
              onClick={() => setReviewIndex(i => Math.min(reviewQs.length - 1, i + 1))}
              disabled={reviewIndex === reviewQs.length - 1}
              className="px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition disabled:opacity-50 font-medium"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Summary View
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-slate-900 mb-8 text-center">Test Result</h1>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden mb-8">
        <div className="bg-slate-900 text-white p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl"></div>
          
          <h2 className="text-2xl font-bold mb-2">{result.settings.subject}</h2>
          <p className="text-slate-400 mb-8">{result.settings.mode} • {new Date(result.date).toLocaleString()}</p>
          
          <div className="flex justify-center items-center gap-12">
            <div>
              <p className="text-slate-400 text-sm font-medium mb-1">Score</p>
              <div className="text-5xl font-black">{result.totalMarks}<span className="text-2xl text-slate-500">/{result.maxMarks}</span></div>
            </div>
            
            <div className="w-px h-16 bg-slate-700"></div>
            
            <div>
              <p className="text-slate-400 text-sm font-medium mb-1">Percentage</p>
              <div className="text-5xl font-black text-blue-400">{result.percentage.toFixed(1)}%</div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-y md:divide-y-0 divide-slate-100 bg-slate-50">
          <div className="p-6 text-center">
            <p className="text-slate-500 text-sm font-medium">Attempted</p>
            <p className="text-2xl font-bold text-slate-800">{result.attempted}/{result.totalQuestions}</p>
          </div>
          <div className="p-6 text-center">
            <p className="text-slate-500 text-sm font-medium">Correct</p>
            <p className="text-2xl font-bold text-emerald-600">{result.correctAnswers}</p>
          </div>
          <div className="p-6 text-center">
            <p className="text-slate-500 text-sm font-medium">Incorrect</p>
            <p className="text-2xl font-bold text-red-600">{result.incorrectAnswers}</p>
          </div>
          <div className="p-6 text-center">
            <p className="text-slate-500 text-sm font-medium">Accuracy</p>
            <p className="text-2xl font-bold text-purple-600">{result.accuracy.toFixed(1)}%</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
        <button 
          onClick={() => startReview('all')}
          className="p-4 bg-white border border-slate-200 rounded-xl hover:border-blue-300 hover:shadow-md transition flex flex-col items-center gap-2 group"
        >
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex justify-center items-center group-hover:bg-blue-100 transition">
            <Eye className="w-6 h-6" />
          </div>
          <span className="font-bold text-slate-800">Review All Questions</span>
          <span className="text-sm text-slate-500">{result.totalQuestions} questions</span>
        </button>
        
        <button 
          onClick={() => startReview('incorrect')}
          disabled={result.incorrectAnswers === 0}
          className="p-4 bg-white border border-slate-200 rounded-xl hover:border-red-300 hover:shadow-md transition flex flex-col items-center gap-2 group disabled:opacity-50 disabled:hover:shadow-none disabled:hover:border-slate-200"
        >
          <div className="w-12 h-12 bg-red-50 text-red-600 rounded-full flex justify-center items-center group-hover:bg-red-100 transition">
            <XCircle className="w-6 h-6" />
          </div>
          <span className="font-bold text-slate-800">Review Incorrect</span>
          <span className="text-sm text-slate-500">{result.incorrectAnswers} questions</span>
        </button>
        
        <button 
          onClick={() => startReview('unanswered')}
          disabled={result.unanswered === 0}
          className="p-4 bg-white border border-slate-200 rounded-xl hover:border-amber-300 hover:shadow-md transition flex flex-col items-center gap-2 group disabled:opacity-50 disabled:hover:shadow-none disabled:hover:border-slate-200"
        >
          <div className="w-12 h-12 bg-amber-50 text-amber-600 rounded-full flex justify-center items-center group-hover:bg-amber-100 transition">
            <AlertCircle className="w-6 h-6" />
          </div>
          <span className="font-bold text-slate-800">Review Unanswered</span>
          <span className="text-sm text-slate-500">{result.unanswered} questions</span>
        </button>
      </div>
      
      <div className="flex justify-center gap-4">
        <button 
          onClick={() => navigate(`/setup/${encodeURIComponent(result.settings.subject)}`)}
          className="px-6 py-3 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition flex items-center gap-2 font-bold text-slate-700"
        >
          <RotateCcw className="w-5 h-5" /> Retake Test
        </button>
        <button 
          onClick={() => navigate('/')}
          className="px-8 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition flex items-center gap-2 font-bold shadow-sm"
        >
          <Home className="w-5 h-5" /> Back to Dashboard
        </button>
      </div>
    </div>
  );
};

export default ResultReview;
