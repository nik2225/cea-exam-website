import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, History as HistoryIcon, Award, BarChart3 } from 'lucide-react';
import { getTestHistory } from '../utils/storage';
import type { SubjectStats } from '../types';

const SUBJECTS = [
  "Mathematics & Applied Mechanics",
  "Drawing",
  "Construction, Construction Materials, Stores Account",
  "Surveying",
  "General Civil Engineering"
];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<SubjectStats[]>([]);
  const [overall, setOverall] = useState({
    testsAttempted: 0,
    averageScore: 0,
    bestScore: 0,
    accuracy: 0
  });

  useEffect(() => {
    const history = getTestHistory();
    let totalQuestionsAttempted = 0;
    let totalCorrectAnswers = 0;
    let totalScoreSum = 0;
    let overallBestScore = 0;
    const subjectStats: SubjectStats[] = SUBJECTS.map(subj => {

      
      const subjHistory = history.filter(h => h.settings.subject === subj);
      const tests = subjHistory.length;
      
      let maxScore = 0;
      let lastScore = 0;
      let sCorrect = 0;
      let sAttempted = 0;
      
      if (tests > 0) {
        maxScore = Math.max(...subjHistory.map(h => h.percentage));
        lastScore = subjHistory[subjHistory.length - 1].percentage;
        sCorrect = subjHistory.reduce((sum, h) => sum + h.correctAnswers, 0);
        sAttempted = subjHistory.reduce((sum, h) => sum + h.attempted, 0);
        
        overallBestScore = Math.max(overallBestScore, maxScore);
        totalScoreSum += subjHistory.reduce((sum, h) => sum + h.percentage, 0);
        totalQuestionsAttempted += sAttempted;
        totalCorrectAnswers += sCorrect;
      }
      
      return {
        subject: subj,
        totalVerifiedQuestions: 0,
        completedTests: tests,
        bestScore: maxScore,
        lastTestScore: lastScore,
        averageScore: tests > 0 ? subjHistory.reduce((sum, h) => sum + h.percentage, 0) / tests : 0,
        totalAccuracy: sAttempted > 0 ? (sCorrect / sAttempted) * 100 : 0
      };
    });
    
    // Asynchronously load real question counts
    Promise.all(SUBJECTS.map(async (subj) => {
      const { getAllQuestionsRaw } = await import('../utils/storage');
      const allRaw = await getAllQuestionsRaw(subj);
      return { 
        subj, 
        verified: allRaw.filter(q => q.validationStatus === 'verified').length,
        total: allRaw.length
      };
    })).then(counts => {
      setStats(prev => prev.map(s => {
        const c = counts.find(x => x.subj === s.subject);
        return { ...s, totalVerifiedQuestions: c?.verified || 0, totalQuestions: c?.total || 0 };
      }));
    });
    
    setStats(subjectStats);
    setOverall({
      testsAttempted: history.length,
      averageScore: history.length > 0 ? totalScoreSum / history.length : 0,
      bestScore: overallBestScore,
      accuracy: totalQuestionsAttempted > 0 ? (totalCorrectAnswers / totalQuestionsAttempted) * 100 : 0
    });
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="flex justify-between items-center mb-8 border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">CEA Departmental Exam Practice</h1>
          <p className="text-slate-500 mt-1">Maharashtra PWD Civil Engineering Assistant</p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => navigate('/history')}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition"
          >
            <HistoryIcon className="w-4 h-4" />
            Test History
          </button>
          <button 
            onClick={() => navigate('/admin')}
            className="flex items-center gap-2 px-4 py-2 bg-amber-100 hover:bg-amber-200 text-amber-800 font-bold border border-amber-200 rounded-lg shadow-sm transition"
          >
            <BookOpen className="w-4 h-4" />
            Admin Validation
          </button>
        </div>
      </header>

      {/* Overall Progress */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="bg-blue-100 p-3 rounded-lg text-blue-600">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Tests Attempted</p>
            <p className="text-2xl font-bold">{overall.testsAttempted}</p>
          </div>
        </div>
        
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="bg-emerald-100 p-3 rounded-lg text-emerald-600">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Average Score</p>
            <p className="text-2xl font-bold">{overall.averageScore.toFixed(1)}%</p>
          </div>
        </div>
        
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="bg-amber-100 p-3 rounded-lg text-amber-600">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Best Score</p>
            <p className="text-2xl font-bold">{overall.bestScore.toFixed(1)}%</p>
          </div>
        </div>
        
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="bg-purple-100 p-3 rounded-lg text-purple-600">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Accuracy</p>
            <p className="text-2xl font-bold">{overall.accuracy.toFixed(1)}%</p>
          </div>
        </div>
      </section>

      {/* Subjects */}
      <h2 className="text-xl font-bold mb-4 text-slate-800">Select a Subject</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((s, i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition">
            <div className="p-6">
              <h3 className="font-bold text-lg mb-2 leading-tight text-slate-900">{s.subject}</h3>
              
              <div className="grid grid-cols-2 gap-y-2 mt-4 text-sm">
                <div className="text-slate-500">Verified Questions</div>
                <div className="font-medium text-right text-emerald-600">
                  {s.totalVerifiedQuestions} <span className="text-slate-400 text-xs">/ {s.totalQuestions || 0}</span>
                </div>
                
                <div className="text-slate-500">Completed Tests</div>
                <div className="font-medium text-right">{s.completedTests}</div>
                
                <div className="text-slate-500">Best Score</div>
                <div className="font-medium text-right text-blue-600">{s.bestScore.toFixed(1)}%</div>
              </div>
            </div>
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-col gap-2">
              <button 
                onClick={() => navigate(`/setup/${encodeURIComponent(s.subject)}`)}
                className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
              >
                Configure Test
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
