# DocChat v1 - PRD

## 1. Overview

DocChat is a web-based PDF chat tool for everyday users who need to review important documents before signing or making a decision. In Version 1, users can upload a PDF then get an instant summary, ask questions, and identify possible risks or confusing clauses. The product helps users understand what they are agreeing to without manually reading the entire document, while clearly stating that it does not provide legal advice.

## 2. User Stories

1. **PDF Upload**

   As a user reviewing an important document, I want to upload a PDF so that the system can read the document and help me understand it.

2. **Instant Summary**

   As a user, I want to generate a quick summary of the uploaded document so that I can understand the main points without reading the full document manually.

3. **Chat Interface**

   As a user, I want to ask questions in a simple chat interface so that I can get answers about specific parts of the document.

4. **Possible Risk or Confusing Clause Identification**

   As a user, I want the system to highlight possible risks or confusing clauses so that I know what sections I should review more carefully before signing.

## 3. Functional Requirements

### 3.1 PDF Upload

- The system must allow the user to upload one PDF file at a time.
- The upload area must support selecting a file from the user's device.
- The system must only accept files in PDF format.
- The system must show an error message if the user uploads a non-PDF file.
- The system must show an error message if the PDF cannot be processed.
- After a successful upload, the system must confirm that the file has been uploaded successfully.
- The system must send the uploaded PDF for text extraction so the content can be used for summaries and question answering.

### 3.2 Text Extraction

- The system must extract readable text from the uploaded PDF.
- The extracted text must be stored temporarily during the active session so it can be used for summary generation and chat responses.
- If the PDF has no readable text or the extraction fails, the system must show a clear error message to the user.
- Version 1 does not need to support scanned image-based PDFs that require OCR.

### 3.3 Instant Summary

- The system must provide a button or action that allows the user to generate a summary of the uploaded PDF.
- The summary must be based only on the extracted PDF content.
- The summary must explain the main purpose of the document in simple language.
- The summary must include important terms, obligations, deadlines, fees, penalties, or responsibilities if they are found in the document.
- The summary must include a disclaimer that the output is for understanding only and does not provide legal advice.

### 3.4 Chat Interface

- The system must provide a chat input where the user can type questions about the uploaded PDF.
- The system must display the user's question and the system's response in a conversation-style layout.
- The system must only answer questions related to the uploaded document.
- If the user asks a question that cannot be answered from the document, the system must say that the answer was not found in the uploaded document.
- The system must allow the user to ask multiple follow-up questions during the same session.

### 3.5 Document-Based Question and Answer

- The system must generate answers using the extracted PDF content as the main source.
- The system must respond in simple and understandable language.
- The system must help users understand key terms, obligations, risks, fees, deadlines, and confusing sections from the document.
- The system must avoid giving legal advice or telling the user what decision to make.
- The system must include a short disclaimer when the answer relates to legal, financial, or contractual interpretation.

### 3.6 Possible Risk or Confusing Clause Identification

- The system must identify possible risks or confusing sections based on the uploaded document content.
- The system must flag items such as penalties, cancellation terms, renewal terms, payment obligations, late fees, deposits, liability clauses, or user responsibilities when present.
- The system must explain why each flagged item may require careful review.
- The system must clearly state that flagged risks are not legal advice and should be reviewed by the user or a qualified professional if needed.

## 4. Non-Functional Requirements

### 4.1 Performance

- PDF upload must complete within 5 seconds for files under 10MB under normal network conditions.
- Text extraction must complete within 10 seconds for PDFs under 10MB and up to 50 pages.
- Summary generation must complete within 15 seconds after text extraction is complete.
- Chat responses must be generated within 10 seconds for document-based questions under normal system load.
- The system must support one uploaded PDF per user session in Version 1.

### 4.2 Security

- The system must only allow PDF file uploads.
- The system must validate the uploaded file type before processing.
- Uploaded files must not be publicly accessible.
- The system must not expose one user's uploaded document or chat content to another user.
- The system must not store uploaded documents permanently in Version 1 unless explicitly required.
- If temporary storage is used, uploaded files and extracted text must be deleted after the session ends or after a defined expiration period.

### 4.3 Privacy

- The system must handle uploaded documents as private user content.
- The system must not use uploaded documents for public display or sharing.
- The system must show a clear disclaimer that users should avoid uploading highly sensitive personal, financial, or legal documents unless they understand how the tool handles data.

### 4.4 Reliability

- The system must show a clear error message if PDF upload fails.
- The system must show a clear error message if text extraction fails.
- The system must show a clear message if the document has no readable text.
- The system must not generate answers if the uploaded document content cannot be processed.
- The system must continue to allow the user to ask questions after a successful upload and text extraction.

### 4.5 Usability

- The upload flow must be simple enough for a first-time user to complete without instructions.
- The chat interface must clearly separate user questions from system responses.
- Error messages must be written in simple, user-friendly language.
- The system must clearly state that responses are for understanding only and do not replace professional or legal advice.

### 4.6 Compatibility

- Version 1 must work in a modern web browser.
- Version 1 does not require a dedicated mobile app.
- Version 1 must support standard text-based PDF documents.
- Scanned PDFs or image-only PDFs are not required for Version 1.

## 5. Acceptance Criteria

### 5.1 PDF Upload

- **Given** the user is on the upload screen, **when** the user selects a valid PDF file, **then** the system uploads the file successfully.
- **Given** the user uploads a non-PDF file, **when** the system validates the file, **then** the system shows an error message saying only PDF files are supported.
- **Given** the user uploads a PDF that cannot be processed, **when** text extraction fails, **then** the system shows a clear error message and does not continue to summary or chat.

### 5.2 Text Extraction

- **Given** the user uploads a valid text-based PDF, **when** the upload is complete, **then** the system extracts readable text from the PDF.
- **Given** the uploaded PDF has readable text, **when** extraction is complete, **then** the system makes the extracted content available for summary and question answering.
- **Given** the uploaded PDF has no readable text, **when** extraction fails, **then** the system informs the user that the document cannot be processed in Version 1.

### 5.3 Instant Summary

- **Given** a PDF has been uploaded and processed, **when** the user requests a summary, **then** the system generates a summary based only on the uploaded document.
- **Given** the system generates a summary, **when** the summary is displayed, **then** it includes the main purpose of the document and important terms found in the content.
- **Given** the document contains possible fees, deadlines, penalties, responsibilities, or cancellation terms, **when** the summary is generated, **then** the system highlights them as items the user should review carefully.
- **Given** the summary is displayed, **when** the user reads it, **then** the system shows a disclaimer that the summary is for understanding only and is not legal advice.

### 5.4 Chat Interface

- **Given** a PDF has been uploaded and processed, **when** the user types a question in the chat box, **then** the system displays the question in the chat conversation.
- **Given** the user submits a document-related question, **when** the system finds relevant information in the document, **then** it returns an answer in simple language.
- **Given** the user asks multiple questions in the same session, **when** each question is submitted, **then** the system continues the conversation without requiring the user to upload the PDF again.

### 5.5 Document-Based Question and Answer

- **Given** the user asks a question about the uploaded document, **when** the answer exists in the document, **then** the system answers based on the extracted PDF content.
- **Given** the user asks a question that is not answered in the uploaded document, **when** the system cannot find relevant content, **then** it says the answer was not found in the document.
- **Given** the user asks about terms, obligations, fees, deadlines, or risks, **when** the system responds, **then** it explains the information clearly without giving legal advice.
- **Given** the response involves legal, financial, or contractual interpretation, **when** the answer is shown, **then** the system includes a disclaimer that the response is not professional or legal advice.

### 5.6 Possible Risk or Confusing Clause Identification

- **Given** the uploaded document contains clauses related to penalties, cancellation, renewal, late fees, deposits, liability, or user responsibilities, **when** the user requests a summary or asks about risks, **then** the system identifies those sections as items to review carefully.
- **Given** the system flags a possible risk or confusing clause, **when** it displays the result, **then** it explains why the section may require attention.
- **Given** the system flags possible risks, **when** the user reads them, **then** the system clearly states that these are not legal conclusions or legal advice.
