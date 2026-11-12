import re
from typing import Dict, List, Set, Tuple

# Comprehensive taxonomy of skills mapped to their category
SKILLS_TAXONOMY: Dict[str, List[str]] = {
    "programming_languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Dart", "Scala", "R", "SQL", "MATLAB", "Perl",
        "Haskell", "Elixir", "Clojure", "Julia", "Solidity", "Objective-C", "Shell", "Bash",
        "PowerShell", "Groovy", "Visual Basic", "COBOL", "Fortran", "Assembly", "Lua"
    ],
    "frameworks": [
        "React", "React Native", "Next.js", "Angular", "Vue", "Vue.js", "Svelte",
        "Django", "FastAPI", "Flask", "Spring", "Spring Boot", "Express", "Express.js",
        "NestJS", "ASP.NET", ".NET Core", "Ruby on Rails", "Laravel", "Symfony",
        "Flutter", "Electron", "Koa", "Fastify", "Tornado", "Quarkus", "Micronaut",
        "Phoenix", "Gatsby", "Nuxt.js", "Remix", "Astro", "Blazor", "Fiber", "Gin"
    ],
    "libraries": [
        "Redux", "Redux Toolkit", "Zustand", "MobX", "RxJS", "Tailwind CSS", "Bootstrap",
        "Material UI", "Chakra UI", "Shadcn UI", "Ant Design", "Styled Components",
        "NumPy", "Pandas", "Scikit-Learn", "SciPy", "Matplotlib", "Seaborn", "Statsmodels",
        "PyTorch", "TensorFlow", "Keras", "Hugging Face", "Transformers", "SpaCy", "NLTK",
        "OpenCV", "Pydantic", "SQLAlchemy", "Hibernate", "Prisma", "Mongoose", "Celery",
        "Axios", "GraphQL", "Apollo", "Socket.io", "Lodash", "Jest", "Vitest", "PyTest",
        "Cypress", "Selenium", "Playwright", "Mocha", "Chai", "LangChain", "LlamaIndex"
    ],
    "databases": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
        "DynamoDB", "CouchDB", "Neo4j", "MariaDB", "Oracle", "Microsoft SQL Server", "Snowflake",
        "BigQuery", "Firebase Realtime Database", "Firestore", "Supabase", "CockroachDB",
        "ClickHouse", "SingleStore", "TimescaleDB", "FaunaDB", "Memcached", "Vector DB",
        "Pinecone", "ChromaDB", "Milvus", "Weaviate", "Qdrant"
    ],
    "cloud": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "Google Cloud", "Google Cloud Platform",
        "GCP", "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Puppet", "Chef",
        "CloudFormation", "OpenShift", "Helm", "Serverless", "AWS Lambda", "Cloudflare",
        "Vercel", "Netlify", "Heroku", "DigitalOcean", "Linode", "Nginx", "Apache",
        "Traefik", "Envoy", "Istio", "Linux", "Ubuntu", "CentOS", "Debian", "RedHat"
    ],
    "ai_ml": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "AI", "ML", "NLP",
        "Natural Language Processing", "Computer Vision", "LLMs", "Large Language Models",
        "Generative AI", "GenAI", "RAG", "Retrieval-Augmented Generation", "Reinforcement Learning",
        "Prompt Engineering", "Fine-Tuning", "Ollama", "vLLM", "Hugging Face Transformers",
        "BERT", "GPT", "Llama", "Mistral", "Phi-3", "Claude", "Stable Diffusion",
        "Vector Embeddings", "Semantic Search", "Neural Networks", "CNN", "RNN", "LSTM"
    ],
    "tools": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello", "Asana",
        "Postman", "Swagger", "OpenAPI", "VS Code", "Visual Studio", "IntelliJ IDEA",
        "PyCharm", "WebStorm", "Eclipse", "Vim", "Neovim", "Docker Desktop", "Figma",
        "Adobe XD", "Webpack", "Vite", "Babel", "npm", "yarn", "pnpm", "Maven", "Gradle",
        "CMake", "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI", "ArgoCD", "SonarQube"
    ],
    "other_skills": [
        "REST API", "RESTful APIs", "Microservices", "Event-Driven Architecture", "Kafka",
        "RabbitMQ", "ActiveMQ", "WebSockets", "gRPC", "CI/CD", "DevOps", "Agile", "Scrum",
        "Kanban", "TDD", "BDD", "Unit Testing", "System Design", "Object-Oriented Programming",
        "OOP", "Functional Programming", "Data Structures", "Algorithms", "Clean Architecture",
        "Design Patterns", "ETL", "Data Pipelines", "Data Warehousing", "Business Intelligence",
        "Power BI", "Tableau", "Looker", "SEO", "UI/UX", "Authentication", "OAuth", "JWT",
        "SSO", "SAML", "CORS", "Cybersecurity", "OWASP", "Penetration Testing"
    ]
}

# Normalization mapping for standard canonical names
CANONICAL_SKILL_MAP: Dict[str, str] = {
    "py": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "golang": "Go",
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "angularjs": "Angular",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring-boot": "Spring Boot",
    "springboot": "Spring Boot",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mssql": "Microsoft SQL Server",
    "sql server": "Microsoft SQL Server",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud Platform (GCP)",
    "google cloud": "Google Cloud Platform (GCP)",
    "azure": "Microsoft Azure",
    "scikit-learn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "llm": "LLMs",
    "llms": "LLMs",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "rag": "RAG",
    "ci/cd": "CI/CD",
    "rest": "RESTful APIs",
    "restful": "RESTful APIs",
    "rest api": "RESTful APIs",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "jira": "Jira"
}

# Special tokens that need boundary and case protection to prevent false positive substrings
SPECIAL_SHORT_TOKENS = {
    "C": re.compile(r'(?<![A-Za-z0-9+#])C(?![A-Za-z0-9+#])'),
    "R": re.compile(r'(?<![A-Za-z0-9])R(?![A-Za-z0-9])'),
    "Go": re.compile(r'(?<![A-Za-z0-9])Go(?![A-Za-z0-9])'),
    "AI": re.compile(r'(?<![A-Za-z0-9])AI(?![A-Za-z0-9])'),
    "ML": re.compile(r'(?<![A-Za-z0-9])ML(?![A-Za-z0-9])'),
    "NLP": re.compile(r'(?<![A-Za-z0-9])NLP(?![A-Za-z0-9])'),
    "SQL": re.compile(r'(?<![A-Za-z0-9])SQL(?![A-Za-z0-9])'),
    "Git": re.compile(r'(?<![A-Za-z0-9])Git(?![A-Za-z0-9])', re.IGNORECASE),
    ".NET": re.compile(r'(?<![A-Za-z0-9])\.NET(?![A-Za-z0-9])', re.IGNORECASE),
    "C++": re.compile(r'(?<![A-Za-z0-9])C\+\+(?![A-Za-z0-9])'),
    "C#": re.compile(r'(?<![A-Za-z0-9])C#(?![A-Za-z0-9])'),
}

def extract_and_categorize_skills(text: str) -> Dict[str, List[str]]:
    """
    Scans text for skills from the taxonomy using robust word boundaries,
    normalizes them, groups into categories, and eliminates duplicates.
    """
    categorized: Dict[str, List[str]] = {cat: [] for cat in SKILLS_TAXONOMY.keys()}
    found_normalized: Set[str] = set()

    for category, skill_list in SKILLS_TAXONOMY.items():
        for skill in skill_list:
            is_match = False
            
            # Check for special short tokens
            if skill in SPECIAL_SHORT_TOKENS:
                pattern = SPECIAL_SHORT_TOKENS[skill]
                if pattern.search(text):
                    is_match = True
            else:
                # Escape skill name for safe regex
                escaped = re.escape(skill)
                # Word boundary match, case-insensitive
                pattern = re.compile(rf'(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])', re.IGNORECASE)
                if pattern.search(text):
                    is_match = True
            
            if is_match:
                canonical = CANONICAL_SKILL_MAP.get(skill.lower(), skill)
                if canonical.lower() not in found_normalized:
                    found_normalized.add(canonical.lower())
                    categorized[category].append(canonical)

    return categorized
