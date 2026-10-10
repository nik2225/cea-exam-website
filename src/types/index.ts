export interface Question {
  id: string;
  subject: string;
  originalQuestionNumber: number;
  questionText: string;
  options: string[];
  correctAnswerIndex: number;
  explanation?: string;
  hasDiagram?: boolean;
  needsReview?: boolean;
  rawText?: string;
  sourcePdf?: string;
  sourcePage?: number;
  sourcePagePath?: string;
  diagramPath?: string;
  validationStatus?: 'verified' | 'needs_review';
}

export interface TestSettings {
  subject: string;
  mode: 'Full Test' | 'Practice Test' | 'Custom Test';
  numberOfQuestions: number;
  durationMinutes: number;
  shuffleQuestions: boolean;
  shuffleOptions: boolean;
  negativeMarking: boolean;
  negativeMarksPerWrongAnswer: number;
  unansweredZero: boolean;
}

export type QuestionStatus = 
  | 'not-visited'
  | 'not-answered'
  | 'answered'
  | 'marked'
  | 'answered-marked';

export interface AnswerRecord {
  questionId: string;
  selectedOptionIndex: number | null;
  status: QuestionStatus;
  originalOptionIndices: number[]; // To keep track of shuffled options [shuffledIndex] -> originalIndex
}

export interface TestResult {
  id: string;
  date: string;
  settings: TestSettings;
  questions: Question[]; // The exact questions that appeared in the test
  answers: Record<string, AnswerRecord>;
  totalQuestions: number;
  attempted: number;
  correctAnswers: number;
  incorrectAnswers: number;
  unanswered: number;
  totalMarks: number;
  maxMarks: number;
  percentage: number;
  accuracy: number;
  timeTakenSeconds: number;
}

export interface SubjectStats {
  subject: string;
  totalVerifiedQuestions: number;
  totalQuestions?: number;
  completedTests: number;
  bestScore: number;
  lastTestScore: number;
  averageScore: number;
  totalAccuracy: number;
}
