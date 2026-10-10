import type { TestResult, Question } from '../types';

const HISTORY_KEY = 'cea_exam_history';

export const saveTestResult = (result: TestResult) => {
  const history = getTestHistory();
  history.push(result);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
};

export const getTestHistory = (): TestResult[] => {
  try {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error("Failed to parse test history", e);
    return [];
  }
};

export const clearTestHistory = () => {
  localStorage.removeItem(HISTORY_KEY);
};

export const getQuestionsBySubject = async (subject: string): Promise<Question[]> => {
  try {
    const safeName = subject.replace(/ /g, '_').replace(/&/g, 'and').replace(/,/g, '');
    const data = await import(`../data/${safeName}.json`);
    const allQuestions = data.default as Question[];
    return allQuestions.filter(q => q.validationStatus === 'verified');
  } catch (e) {
    console.error("Failed to load questions for subject", subject, e);
    return [];
  }
};

export const getAllQuestionsRaw = async (subject: string): Promise<Question[]> => {
  try {
    const safeName = subject.replace(/ /g, '_').replace(/&/g, 'and').replace(/,/g, '');
    const data = await import(`../data/${safeName}.json`);
    return data.default as Question[];
  } catch (e) {
    return [];
  }
};
