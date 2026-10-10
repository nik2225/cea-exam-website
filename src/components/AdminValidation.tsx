import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, ChevronLeft, ChevronRight, CheckCircle2, AlertCircle, Image as ImageIcon } from 'lucide-react';
import type { Question } from '../types';

const SUBJECTS = [
  "Mathematics & Applied Mechanics",
  "Drawing",
  "Construction, Construction Materials, Stores Account",
  "Surveying",
  "General Civil Engineering"
];

const AdminValidation: React.FC = () => {
  const navigate = useNavigate();
  const [subject, setSubject] = useState(SUBJECTS[0]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string>('');

  useEffect(() => {
    loadQuestions(subject);
  }, [subject]);

  const loadQuestions = async (sub: string) => {
    try {
      const safeName = sub.replace(/ /g, '_').replace(/&/g, 'and').replace(/,/g, '');
      const response = await fetch(`/src/data/${safeName}.json?t=${Date.now()}`); // Cache busting
      if (response.ok) {
        const data = await response.json();
        setQuestions(data);
        setCurrentIndex(0);
      } else {
        setQuestions([]);
      }
    } catch (e) {
      console.error(e);
      setQuestions([]);
    }
  };

  const currentQ = questions[currentIndex];

  const handleUpdate = (field: keyof Question, value: any) => {
    const updated = [...questions];
    updated[currentIndex] = { ...updated[currentIndex], [field]: value };
    setQuestions(updated);
  };

  const handleOptionUpdate = (index: number, value: string) => {
    const updated = [...questions];
    const newOptions = [...updated[currentIndex].options];
    newOptions[index] = value;
    updated[currentIndex] = { ...updated[currentIndex], options: newOptions };
    setQuestions(updated);
  };

  const saveToServer = async () => {
    setLoading(true);
    setSaveStatus('Saving...');
    try {
      const response = await fetch('/api/save-questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, questions })
      });
      if (response.ok) {
        setSaveStatus('Saved successfully!');
        setTimeout(() => setSaveStatus(''), 3000);
      } else {
        setSaveStatus('Failed to save.');
      }
    } catch (e) {
      setSaveStatus('Error saving.');
    }
    setLoading(false);
  };

  const markVerified = () => {
    handleUpdate('validationStatus', 'verified');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <div className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/')} className="text-slate-500 hover:text-slate-800 transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-blue-600" /> Admin Data Validation
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          <select 
            value={subject} 
            onChange={e => setSubject(e.target.value)}
            className="border-slate-300 rounded-md shadow-sm text-sm p-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {SUBJECTS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <button 
            onClick={saveToServer}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition"
          >
            <Save className="w-4 h-4" /> Save Bank
          </button>
          {saveStatus && <span className="text-sm font-medium text-emerald-600">{saveStatus}</span>}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {questions.length === 0 ? (
          <div className="m-auto text-center text-slate-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p className="text-xl font-bold text-slate-700">No data found</p>
            <p>Ensure the extraction script has been run.</p>
          </div>
        ) : (
          <>
            {/* Left side: Form */}
            <div className="w-1/2 p-6 overflow-y-auto border-r border-slate-200 bg-white">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-2">
                  <button onClick={() => setCurrentIndex(c => Math.max(0, c - 1))} disabled={currentIndex === 0} className="p-2 border rounded hover:bg-slate-50 disabled:opacity-50"><ChevronLeft className="w-4 h-4" /></button>
                  <span className="text-sm font-bold text-slate-600">Q {currentIndex + 1} of {questions.length}</span>
                  <button onClick={() => setCurrentIndex(c => Math.min(questions.length - 1, c + 1))} disabled={currentIndex === questions.length - 1} className="p-2 border rounded hover:bg-slate-50 disabled:opacity-50"><ChevronRight className="w-4 h-4" /></button>
                </div>
                
                <div className="flex gap-2">
                  <span className={`px-3 py-1 rounded text-xs font-bold ${currentQ.validationStatus === 'verified' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                    {currentQ.validationStatus === 'verified' ? 'VERIFIED' : 'NEEDS REVIEW'}
                  </span>
                  <button 
                    onClick={markVerified}
                    className="px-3 py-1 bg-slate-100 hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 font-bold text-xs rounded border border-slate-200 hover:border-emerald-200 transition"
                  >
                    Mark Verified
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">ID</label>
                  <input type="text" value={currentQ.id} readOnly className="w-full bg-slate-50 border-slate-200 rounded p-2 text-sm text-slate-500" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Original Q Num</label>
                  <input type="number" value={currentQ.originalQuestionNumber} onChange={e => handleUpdate('originalQuestionNumber', parseInt(e.target.value))} className="w-full border-slate-300 rounded p-2 text-sm" />
                </div>
                
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Question Text</label>
                  <textarea 
                    value={currentQ.questionText} 
                    onChange={e => handleUpdate('questionText', e.target.value)}
                    rows={4}
                    className="w-full border-slate-300 rounded p-2 text-sm" 
                  />
                </div>

                {currentQ.hasDiagram && currentQ.diagramPath && (
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Question Diagram</label>
                    <div className="bg-slate-50 border border-slate-200 rounded p-2 inline-block max-w-full">
                      <img 
                        src={currentQ.diagramPath} 
                        alt="Question Diagram" 
                        className="max-w-full h-auto object-contain"
                      />
                    </div>
                  </div>
                )}
                
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1 flex items-center gap-2">Options & Correct Answer</label>
                  <div className="space-y-2">
                    {currentQ.options.map((opt, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <input 
                          type="radio" 
                          name="correctOption" 
                          checked={currentQ.correctAnswerIndex === i}
                          onChange={() => handleUpdate('correctAnswerIndex', i)}
                          className="w-4 h-4 text-emerald-600 focus:ring-emerald-500"
                        />
                        <input 
                          type="text" 
                          value={opt} 
                          onChange={e => handleOptionUpdate(i, e.target.value)}
                          placeholder={`Option ${i + 1}`}
                          className={`w-full p-2 text-sm rounded border ${currentQ.correctAnswerIndex === i ? 'border-emerald-400 bg-emerald-50' : 'border-slate-300'}`} 
                        />
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 flex items-center gap-4">
                   <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                     <input type="checkbox" checked={currentQ.hasDiagram} onChange={e => handleUpdate('hasDiagram', e.target.checked)} />
                     Contains Diagram/Image
                   </label>
                </div>
              </div>
            </div>

            {/* Right side: Image Preview */}
            <div className="w-1/2 bg-slate-100 p-6 overflow-y-auto">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 h-full flex flex-col">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-slate-700 flex items-center gap-2"><ImageIcon className="w-5 h-5 text-slate-400" /> Source PDF Page</h3>
                  <div className="text-sm text-slate-500 bg-slate-100 px-3 py-1 rounded-full font-medium">
                    {currentQ.sourcePdf} - Page {currentQ.sourcePage}
                  </div>
                </div>
                
                <div className="flex-1 bg-slate-50 border border-slate-200 rounded-lg overflow-auto flex items-start justify-center p-4">
                  {currentQ.sourcePagePath ? (
                    <img 
                      src={currentQ.sourcePagePath} 
                      alt={`Source Page ${currentQ.sourcePage}`}
                      className="max-w-full shadow-md object-contain border border-slate-200"
                    />
                  ) : (
                    <div className="text-slate-400 m-auto text-sm">No page image available. Did you run the extraction script?</div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AdminValidation;
