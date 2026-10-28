# ResumeMatch - AI Resume Analyzer & Job Matcher

Upload a CV, paste a job description, and get:
- an overall match score
- matched and missing skills
- the job requirements your CV doesn't answer yet
- a CV quality checklist and concrete improvement tips
- a downloadable report

## How it works
1. `parser.py` extracts text from PDF / DOCX / TXT.
2. `skills.py` finds skills with a keyword dictionary.
3. `matcher.py` embeds every line of the CV and job with Sentence Transformers (`all-MiniLM-L6-v2`)
   and compares them with cosine similarity.
4. `analyzer.py` combines everything: 45% skill coverage, 40% semantic fit, 15% CV quality.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure
```
app.py            Streamlit UI
assets/style.css  Custom styling
src/              parser, skills, matcher, analyzer
sample_data/      example job description
```

## Ideas for next steps
- Replace the skill dictionary with a spaCy / LLM-based extractor
- Rewrite weak bullets with an LLM
- Add multi-job comparison
