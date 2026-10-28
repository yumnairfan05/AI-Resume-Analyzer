"""Skill dictionary + extraction. Add your own skills here - it is just a dict."""
import re

# canonical name -> aliases (all lowercase)
SKILLS = {
    # Languages
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript"],
    "C++": ["c++"],
    "C#": ["c#"],
    "Go": ["golang"],
    "R": ["r programming", "rstudio"],
    "PHP": ["php"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift"],
    "Bash": ["bash", "shell scripting"],
    # Data / ML
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite", "t-sql"],
    "NoSQL": ["nosql", "mongodb", "cassandra", "dynamodb"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Keras": ["keras"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "opencv"],
    "LLMs": ["llm", "llms", "large language models", "generative ai", "gpt"],
    "Transformers": ["transformers", "hugging face", "huggingface", "bert"],
    "Data Analysis": ["data analysis", "data analytics", "eda"],
    "Data Visualization": ["data visualization", "matplotlib", "seaborn", "plotly"],
    "Statistics": ["statistics", "statistical analysis"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "microsoft excel"],
    "Spark": ["spark", "pyspark"],
    "ETL": ["etl", "data pipelines", "data pipeline"],
    # Web
    "HTML/CSS": ["html", "css", "html5", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular"],
    "Vue": ["vue", "vue.js"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Streamlit": ["streamlit"],
    "REST APIs": ["rest", "restful", "rest api", "rest apis", "api development"],
    "GraphQL": ["graphql"],
    # DevOps / Cloud
    "Git": ["git", "github", "gitlab", "version control"],
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services", "ec2", "s3"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "CI/CD": ["ci/cd", "cicd", "jenkins", "github actions"],
    "Linux": ["linux", "unix"],
    "MLOps": ["mlops", "mlflow"],
    # Practices / soft skills
    "Agile": ["agile", "scrum", "kanban"],
    "Testing": ["unit testing", "pytest", "test automation", "qa"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Communication": ["communication", "stakeholder management", "stakeholders"],
    "Teamwork": ["teamwork", "collaboration", "cross-functional"],
    "Leadership": ["leadership", "team lead", "mentoring"],
    "Project Management": ["project management", "jira"],
}

_LB = r"(?<![A-Za-z0-9+#.])"
_LA = r"(?![A-Za-z0-9+#])"

_PATTERNS = {
    skill: [re.compile(_LB + re.escape(a) + _LA) for a in aliases]
    for skill, aliases in SKILLS.items()
}


def extract_skills(text: str) -> set:
    lowered = text.lower()
    found = set()
    for skill, patterns in _PATTERNS.items():
        if any(p.search(lowered) for p in patterns):
            found.add(skill)
    return found
