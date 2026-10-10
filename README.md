# CEA Departmental Exam Practice Website

A complete, responsive MCQ examination website for preparing for the Maharashtra PWD Civil Engineering Assistant (CEA) departmental examination. Built with React, TypeScript, Vite, and Tailwind CSS.

## Features

- **Subject Selection Dashboard**: View your progress and select a subject.
- **Configurable Test**: Choose test mode (Full, Practice, Custom), number of questions, duration, shuffling options, and negative marking.
- **Real Examination Interface**: Timer, question palette, mark for review, clear response, and immediate auto-saving.
- **Scoring Engine**: Calculates total marks, percentage, accuracy, and factors in negative marking (if enabled).
- **Result & Answer Review**: Detailed result summary and the ability to review correct/incorrect answers.
- **Test History**: Local persistence of test history and performance analytics.

## Installation & Running Locally

1. Ensure you have Node.js installed.
2. In the project root, run:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the application in your browser (usually `http://localhost:5173`).

## Data Import Pipeline

This project includes a Python script (`extract_pdfplumber.py`) to parse tabular questions directly from the original PDFs and convert them into structured JSON files located in `src/data/`.

### Adding more subjects and question PDFs later:

1. Place the new PDF inside the `questionsssss` folder.
2. Ensure the filename matches the subject map in `extract_pdfplumber.py` (e.g., `_GCE_`, `_Maths_APM_`).
3. Run the Python extraction script:
   ```bash
   pip install pdfplumber PyMuPDF
   python extract_pdfplumber.py
   ```
4. A validation report will be updated at `src/data/validation_report.md` detailing extraction accuracy, missing data, and items requiring manual review.

*Note: Some PDFs contain diagrams that cannot be cleanly parsed to text. These questions are flagged for manual review in the validation report.*
