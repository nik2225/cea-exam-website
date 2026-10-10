import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Timer, ChevronLeft, ChevronRight, Bookmark, Trash2, CheckCircle2 } from 'lucide-react';
import { getQuestionsBySubject, saveTestResult } from '../utils/storage';
import type { Question, TestSettings, AnswerRecord, QuestionStatus, TestResult } from '../types';

// Utility to shuffle an array
const shuffleArray = <T,>(array: T[]): T[] => {
  const newArr = [...array];
  for (let i = newArr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArr[i], newArr[j]] = [newArr[j], newArr[i]];
  }
  return newArr;
};

// Represents a test question prepared for UI
interface ActiveQuestion extends Question {
  shuffledOptions: string[];
  originalIndices: number[]; // maps shuffled index back to original index
}

interface TestState {
  questions: ActiveQuestion[];
  answers: Record<string, AnswerRecord>;
  timeRemainingSeconds: number;
  startTime: string;
}

const Examination: React.FC = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<TestSettings | null>(null);
  const [testState, setTestState] = useState<TestState | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [timeWarning, setTimeWarning] = useState<string | null>(null);
  
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    const initializeTest = async () => {
      // Check if resuming
      const savedStateStr = sessionStorage.getItem('test_state');
      const settingsStr = sessionStorage.getItem('test_settings');
      
      if (!settingsStr) {
        navigate('/'); // No test configured
        return;
      }
      
      const s: TestSettings = JSON.parse(settingsStr);
      setSettings(s);
      
      if (savedStateStr) {
        setTestState(JSON.parse(savedStateStr));
        setLoading(false);
        return;
      }
      
      // Initialize new test
      const allQs = await getQuestionsBySubject(s.subject);
      const verified = allQs.filter(q => q.validationStatus === 'verified');
      const source = verified.length > 0 ? verified : allQs;
      
      // Prepare questions
      let selectedQs = [...source];
      if (s.shuffleQuestions) {
        selectedQs = shuffleArray(selectedQs);
      }
      selectedQs = selectedQs.slice(0, s.numberOfQuestions);
      
      const activeQuestions: ActiveQuestion[] = selectedQs.map(q => {
        let opts = [...q.options];
        let indices = [0, 1, 2, 3];
        
        if (s.shuffleOptions) {
          const zipped = opts.map((opt, i) => ({ opt, i }));
          const shuffled = shuffleArray(zipped);
          opts = shuffled.map(x => x.opt);
          indices = shuffled.map(x => x.i);
        }
        
        return {
          ...q,
          shuffledOptions: opts,
          originalIndices: indices
        };
      });
      
      const initialAnswers: Record<string, AnswerRecord> = {};
      activeQuestions.forEach(q => {
        initialAnswers[q.id] = {
          questionId: q.id,
          selectedOptionIndex: null,
          status: 'not-visited',
          originalOptionIndices: q.originalIndices
        };
      });
      
      // Mark first as not-answered
      if (activeQuestions.length > 0) {
        initialAnswers[activeQuestions[0].id].status = 'not-answered';
      }
      
      setTestState({
        questions: activeQuestions,
        answers: initialAnswers,
        timeRemainingSeconds: s.durationMinutes * 60,
        startTime: new Date().toISOString()
      });
      setLoading(false);
    };
    
    initializeTest();
  }, [navigate]);

  // Persist state when it changes
  useEffect(() => {
    if (testState) {
      sessionStorage.setItem('test_state', JSON.stringify(testState));
    }
  }, [testState]);

  // Timer logic
  useEffect(() => {
    if (!loading && testState && testState.timeRemainingSeconds > 0 && !submitting) {
      timerRef.current = window.setInterval(() => {
        setTestState(prev => {
          if (!prev) return prev;
          
          if (prev.timeRemainingSeconds === 300) {
            setTimeWarning("5 Minutes Remaining!");
            setTimeout(() => setTimeWarning(null), 5000);
          } else if (prev.timeRemainingSeconds === 60) {
            setTimeWarning("1 Minute Remaining! Final Warning.");
            setTimeout(() => setTimeWarning(null), 5000);
          }
          
          if (prev.timeRemainingSeconds <= 1) {
            clearInterval(timerRef.current!);
            handleFinalSubmit(prev); // auto submit
            return { ...prev, timeRemainingSeconds: 0 };
          }
          return { ...prev, timeRemainingSeconds: prev.timeRemainingSeconds - 1 };
        });
      }, 1000);
    }
    
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [loading, submitting]); // removed testState to avoid infinite restarts

  const updateQuestionStatus = (idx: number, state: TestState) => {
    const qId = state.questions[idx].id;
    const ans = state.answers[qId];
    if (ans.status === 'not-visited') {
      return {
        ...state,
        answers: {
          ...state.answers,
          [qId]: { ...ans, status: 'not-answered' as QuestionStatus }
        }
      };
    }
    return state;
  };

  const handleNavigate = (newIdx: number) => {
    if (!testState) return;
    if (newIdx >= 0 && newIdx < testState.questions.length) {
      const newState = updateQuestionStatus(newIdx, testState);
      setTestState(newState);
      setCurrentIndex(newIdx);
    }
  };

  const handleOptionSelect = (optionIdx: number) => {
    if (!testState) return;
    const qId = testState.questions[currentIndex].id;
    const ans = testState.answers[qId];
    
    const newStatus = ans.status === 'marked' || ans.status === 'answered-marked' 
      ? 'answered-marked' 
      : 'answered';
      
    setTestState(prev => prev ? {
      ...prev,
      answers: {
        ...prev.answers,
        [qId]: {
          ...ans,
          selectedOptionIndex: optionIdx,
          status: newStatus as QuestionStatus
        }
      }
    } : null);
  };

  const handleClear = () => {
    if (!testState) return;
    const qId = testState.questions[currentIndex].id;
    const ans = testState.answers[qId];
    
    setTestState(prev => prev ? {
      ...prev,
      answers: {
        ...prev.answers,
        [qId]: {
          ...ans,
          selectedOptionIndex: null,
          status: ans.status === 'answered-marked' ? 'marked' : 'not-answered'
        }
      }
    } : null);
  };

  const handleMarkReview = () => {
    if (!testState) return;
    const qId = testState.questions[currentIndex].id;
    const ans = testState.answers[qId];
    
    let newStatus: QuestionStatus = 'marked';
    if (ans.status === 'answered' || ans.status === 'answered-marked') {
      newStatus = ans.status === 'answered' ? 'answered-marked' : 'answered'; // toggle
    } else if (ans.status === 'not-answered' || ans.status === 'marked') {
      newStatus = ans.status === 'not-answered' ? 'marked' : 'not-answered'; // toggle
    }
    
    setTestState(prev => prev ? {
      ...prev,
      answers: {
        ...prev.answers,
        [qId]: {
          ...ans,
          status: newStatus
        }
      }
    } : null);
    
    // Auto move to next after mark for review
    handleNavigate(currentIndex + 1);
  };

  const handleSaveNext = () => {
    handleNavigate(currentIndex + 1);
  };

  const handleFinalSubmit = (stateToSubmit: TestState = testState!) => {
    if (!settings || !stateToSubmit) return;
    setSubmitting(true);
    
    // Calculate Score
    let correct = 0;
    let incorrect = 0;
    let attempted = 0;
    
    const qIds = stateToSubmit.questions.map(q => q.id);
    qIds.forEach(id => {
      const ans = stateToSubmit.answers[id];
      const q = stateToSubmit.questions.find(x => x.id === id)!;
      
      if (ans.selectedOptionIndex !== null) {
        attempted++;
        // map shuffled index back to original
        const originalIndexChosen = ans.originalOptionIndices[ans.selectedOptionIndex];
        if (originalIndexChosen === q.correctAnswerIndex) {
          correct++;
        } else {
          incorrect++;
        }
      }
    });
    
    const maxMarks = stateToSubmit.questions.length; // 1 mark each
    const negMarks = settings.negativeMarking ? (incorrect * settings.negativeMarksPerWrongAnswer) : 0;
    const totalScore = correct - negMarks;
    
    const result: TestResult = {
      id: Date.now().toString(),
      date: new Date().toISOString(),
      settings,
      questions: stateToSubmit.questions, // store exactly what was shown
      answers: stateToSubmit.answers,
      totalQuestions: stateToSubmit.questions.length,
      attempted,
      correctAnswers: correct,
      incorrectAnswers: incorrect,
      unanswered: stateToSubmit.questions.length - attempted,
      totalMarks: parseFloat(totalScore.toFixed(2)),
      maxMarks,
      percentage: parseFloat(((totalScore / maxMarks) * 100).toFixed(2)),
      accuracy: attempted > 0 ? parseFloat(((correct / attempted) * 100).toFixed(2)) : 0,
      timeTakenSeconds: (settings.durationMinutes * 60) - stateToSubmit.timeRemainingSeconds
    };
    
    saveTestResult(result);
    sessionStorage.setItem('last_result', JSON.stringify(result));
    sessionStorage.removeItem('test_state'); // Clear active test
    
    navigate('/result');
  };

  const formatTime = (secs: number) => {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: QuestionStatus) => {
    switch (status) {
      case 'answered': return 'bg-emerald-500 text-white border-emerald-600';
      case 'not-answered': return 'bg-red-500 text-white border-red-600';
      case 'marked': return 'bg-purple-500 text-white border-purple-600';
      case 'answered-marked': return 'bg-purple-500 text-white border-purple-600 relative after:content-[""] after:w-2 after:h-2 after:bg-emerald-400 after:absolute after:bottom-0 after:right-0 after:rounded-full';
      default: return 'bg-white text-slate-600 border-slate-300';
    }
  };

  if (loading || !testState || !settings) return <div className="min-h-screen flex items-center justify-center">Loading Examination...</div>;

  const currentQ = testState.questions[currentIndex];
  const currentAns = testState.answers[currentQ.id];
  const timeSecs = testState.timeRemainingSeconds;
  
  const counts = {
    answered: Object.values(testState.answers).filter(a => a.status === 'answered' || a.status === 'answered-marked').length,
    notAnswered: Object.values(testState.answers).filter(a => a.status === 'not-answered').length,
    notVisited: Object.values(testState.answers).filter(a => a.status === 'not-visited').length,
    marked: Object.values(testState.answers).filter(a => a.status === 'marked' || a.status === 'answered-marked').length,
  };

  return (
    <div className="flex flex-col h-screen bg-slate-100">
      {/* Header */}
      <header className="bg-slate-900 text-white px-4 py-3 flex justify-between items-center shrink-0">
        <div>
          <h1 className="font-bold text-lg">{settings.subject}</h1>
          <p className="text-slate-400 text-sm">{settings.mode}</p>
        </div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-xl font-bold ${
          timeSecs < 60 ? 'bg-red-500 animate-pulse' : timeSecs < 300 ? 'bg-amber-500' : 'bg-slate-800'
        }`}>
          <Timer className="w-5 h-5" />
          {formatTime(timeSecs)}
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* Left: Question Area */}
        <div className="flex-1 flex flex-col p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex-1 flex flex-col">
            
            {/* Q Header */}
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50 rounded-t-xl">
              <span className="font-bold text-lg">Question {currentIndex + 1} of {testState.questions.length}</span>
              <span className="text-slate-500 text-sm">Marks: +1 {settings.negativeMarking && '| -0.25'}</span>
            </div>
            
            {/* Q Body */}
            <div className="p-6 flex-1 overflow-y-auto">
              <div className="text-xl font-medium text-slate-800 mb-8 whitespace-pre-wrap">
                {currentQ.questionText}
              </div>

              {currentQ.hasDiagram && currentQ.diagramPath && (
                <div className="mb-8 rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-white">
                  <div className="bg-slate-100 p-2 text-xs font-bold text-slate-500 uppercase flex justify-between">
                    <span>Reference Image</span>
                    <span>Source: {currentQ.sourcePdf} (Page {currentQ.sourcePage})</span>
                  </div>
                  <img 
                    src={currentQ.diagramPath} 
                    alt={`Question ${currentIndex + 1} Reference`}
                    className="w-full h-auto object-contain"
                  />
                </div>
              )}
              
              <div className="space-y-3">
                {currentQ.shuffledOptions.map((opt, idx) => (
                  <label 
                    key={idx} 
                    className={`flex items-start gap-4 p-4 border rounded-xl cursor-pointer transition ${
                      currentAns.selectedOptionIndex === idx 
                        ? 'border-blue-500 bg-blue-50 shadow-sm' 
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <input 
                      type="radio" 
                      name={`q-${currentQ.id}`}
                      checked={currentAns.selectedOptionIndex === idx}
                      onChange={() => handleOptionSelect(idx)}
                      className="mt-1 w-5 h-5 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-lg text-slate-700">{opt}</span>
                  </label>
                ))}
              </div>
            </div>
            
            {/* Action Bar */}
            <div className="p-4 border-t border-slate-200 bg-slate-50 flex flex-wrap gap-3 rounded-b-xl">
              <button 
                onClick={handleMarkReview}
                className="px-4 py-2 border border-purple-300 text-purple-700 bg-purple-50 rounded-lg hover:bg-purple-100 font-medium flex items-center gap-2 transition"
              >
                <Bookmark className="w-4 h-4" /> 
                {currentAns.status.includes('marked') ? 'Unmark Review' : 'Mark for Review'}
              </button>
              
              <button 
                onClick={handleClear}
                disabled={currentAns.selectedOptionIndex === null}
                className="px-4 py-2 border border-slate-300 text-slate-600 bg-white rounded-lg hover:bg-slate-100 font-medium flex items-center gap-2 transition disabled:opacity-50"
              >
                <Trash2 className="w-4 h-4" /> Clear Response
              </button>
              
              <div className="flex-1"></div>
              
              <button 
                onClick={() => handleNavigate(currentIndex - 1)}
                disabled={currentIndex === 0}
                className="px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 font-medium flex items-center gap-2 transition disabled:opacity-50"
              >
                <ChevronLeft className="w-4 h-4" /> Previous
              </button>
              
              {currentIndex < testState.questions.length - 1 ? (
                <button 
                  onClick={handleSaveNext}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center gap-2 transition"
                >
                  Save & Next <ChevronRight className="w-4 h-4" />
                </button>
              ) : (
                <button 
                  onClick={() => setShowSubmitModal(true)}
                  className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-bold flex items-center gap-2 transition shadow-sm"
                >
                  <CheckCircle2 className="w-5 h-5" /> Submit Test
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Right: Palette */}
        <div className="w-80 bg-white border-l border-slate-200 flex flex-col shrink-0">
          <div className="p-4 border-b border-slate-200">
            <h3 className="font-bold text-slate-800">Question Palette</h3>
            
            <div className="grid grid-cols-2 gap-2 mt-4 text-xs font-medium text-slate-600">
              <div className="flex items-center gap-2"><div className="w-4 h-4 bg-emerald-500 rounded text-white flex justify-center items-center font-bold"></div> Answered: {counts.answered}</div>
              <div className="flex items-center gap-2"><div className="w-4 h-4 bg-red-500 rounded text-white flex justify-center items-center font-bold"></div> Not Answered: {counts.notAnswered}</div>
              <div className="flex items-center gap-2"><div className="w-4 h-4 bg-white border border-slate-300 rounded text-slate-400 flex justify-center items-center font-bold"></div> Not Visited: {counts.notVisited}</div>
              <div className="flex items-center gap-2"><div className="w-4 h-4 bg-purple-500 rounded text-white flex justify-center items-center font-bold"></div> Marked: {counts.marked}</div>
            </div>
          </div>
          
          <div className="p-4 flex-1 overflow-y-auto">
            <div className="grid grid-cols-5 gap-2">
              {testState.questions.map((q, idx) => {
                const stat = testState.answers[q.id].status;
                const colorClass = getStatusColor(stat);
                return (
                  <button
                    key={q.id}
                    onClick={() => handleNavigate(idx)}
                    className={`w-10 h-10 rounded-md font-bold flex items-center justify-center border transition ${colorClass} ${
                      currentIndex === idx ? 'ring-2 ring-blue-500 ring-offset-2' : ''
                    }`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>
          </div>
          
          <div className="p-4 border-t border-slate-200 bg-slate-50">
            <button 
              onClick={() => setShowSubmitModal(true)}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold shadow-sm transition flex justify-center items-center gap-2"
            >
              <CheckCircle2 className="w-5 h-5" /> Submit Final
            </button>
          </div>
        </div>
      </div>
      {/* Toast Warning */}
      {timeWarning && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-lg shadow-2xl font-bold text-lg animate-bounce z-50 flex items-center gap-2">
          <Timer className="w-6 h-6" /> {timeWarning}
        </div>
      )}

      {/* Submission Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="bg-slate-50 border-b border-slate-100 p-6 text-center">
              <h2 className="text-2xl font-bold text-slate-800">Submit Examination?</h2>
              <p className="text-slate-500 mt-2">Are you sure you want to finish the test? You cannot change your answers after submission.</p>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-emerald-50 text-emerald-800 rounded-lg">
                  <span className="font-medium">Answered Questions</span>
                  <span className="font-bold text-xl">{counts.answered}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-red-50 text-red-800 rounded-lg">
                  <span className="font-medium">Not Answered</span>
                  <span className="font-bold text-xl">{counts.notAnswered + counts.notVisited}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-50 text-purple-800 rounded-lg">
                  <span className="font-medium">Marked for Review</span>
                  <span className="font-bold text-xl">{counts.marked}</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mt-8">
                <button 
                  onClick={() => setShowSubmitModal(false)}
                  className="py-3 px-4 border border-slate-300 rounded-xl font-semibold text-slate-600 hover:bg-slate-50 transition"
                >
                  Return to Test
                </button>
                <button 
                  onClick={() => {
                    setShowSubmitModal(false);
                    handleFinalSubmit();
                  }}
                  className="py-3 px-4 bg-blue-600 rounded-xl font-bold text-white hover:bg-blue-700 transition"
                >
                  Confirm Submit
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Examination;
