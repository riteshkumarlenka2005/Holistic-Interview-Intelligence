"""
TopicMemory — Tracks what has been covered in an interview session.

Responsibilities:
  - Store topic + subtopic history per session
  - Provide a deduplicated "covered topics" string for LLM prompts
  - Define curated topic progression maps per job role
  - Classify what topic a new question belongs to (for storage)
"""
from typing import Dict, List, Any, Optional


# ---------------------------------------------------------------------------
# Topic Progression Maps
# Each role maps to an ordered topic progression from foundational → advanced.
# The InterviewBrain uses these to pick the next unexplored topic.
# ---------------------------------------------------------------------------
TOPIC_PROGRESSIONS: Dict[str, List[Dict[str, Any]]] = {
    "Frontend Developer": [
        {"topic": "HTML & CSS Fundamentals", "subtopics": ["Semantic HTML", "CSS Box Model", "Flexbox", "Grid", "Responsive Design"]},
        {"topic": "JavaScript Core", "subtopics": ["Data Types", "Closures", "Promises", "Async/Await", "Event Loop"]},
        {"topic": "React Basics", "subtopics": ["Components", "JSX", "Props", "State", "Virtual DOM"]},
        {"topic": "React Advanced", "subtopics": ["Hooks", "Context API", "Performance Optimization", "Reconciliation", "Error Boundaries"]},
        {"topic": "State Management", "subtopics": ["Redux", "Zustand", "MobX", "React Query"]},
        {"topic": "Testing", "subtopics": ["Jest", "React Testing Library", "End-to-End Testing"]},
        {"topic": "Performance", "subtopics": ["Code Splitting", "Lazy Loading", "Web Vitals", "Memoization"]},
        {"topic": "Tooling & Build", "subtopics": ["Webpack", "Vite", "Babel", "TypeScript"]},
    ],
    "Backend Developer": [
        {"topic": "API Design", "subtopics": ["REST Principles", "HTTP Methods", "Status Codes", "Versioning"]},
        {"topic": "Databases", "subtopics": ["SQL Basics", "Indexing", "Transactions", "ACID", "N+1 Problem"]},
        {"topic": "Authentication", "subtopics": ["JWT", "OAuth2", "Session Management", "bcrypt"]},
        {"topic": "System Architecture", "subtopics": ["Monolith vs Microservices", "Event-Driven", "CQRS", "Message Queues"]},
        {"topic": "Caching", "subtopics": ["Redis", "Cache Invalidation", "CDN", "Memoization"]},
        {"topic": "Concurrency", "subtopics": ["Threads", "Async I/O", "Race Conditions", "Deadlocks"]},
        {"topic": "Security", "subtopics": ["SQL Injection", "XSS", "CSRF", "Rate Limiting", "HTTPS"]},
        {"topic": "DevOps Basics", "subtopics": ["Docker", "CI/CD", "Kubernetes Concepts", "Environment Variables"]},
    ],
    "Full Stack Developer": [
        {"topic": "HTML & CSS Fundamentals", "subtopics": ["Semantic HTML", "CSS Box Model", "Flexbox", "Grid"]},
        {"topic": "JavaScript Core", "subtopics": ["Closures", "Promises", "Async/Await", "Event Loop"]},
        {"topic": "React Basics", "subtopics": ["Components", "Props", "State", "Virtual DOM"]},
        {"topic": "API Design", "subtopics": ["REST Principles", "HTTP Methods", "Status Codes"]},
        {"topic": "Databases", "subtopics": ["SQL Basics", "Indexing", "ORM Patterns"]},
        {"topic": "Authentication", "subtopics": ["JWT", "Session Management"]},
        {"topic": "Deployment", "subtopics": ["Docker", "CI/CD", "Cloud Basics"]},
        {"topic": "Performance", "subtopics": ["Frontend Optimization", "Backend Caching", "Query Optimization"]},
    ],
    "Data Scientist": [
        {"topic": "Statistics Foundations", "subtopics": ["Probability", "Distributions", "Hypothesis Testing", "Confidence Intervals"]},
        {"topic": "Machine Learning Basics", "subtopics": ["Supervised Learning", "Unsupervised Learning", "Bias-Variance Tradeoff"]},
        {"topic": "Model Evaluation", "subtopics": ["Cross-Validation", "ROC AUC", "Precision/Recall", "F1 Score"]},
        {"topic": "Feature Engineering", "subtopics": ["Normalization", "Encoding", "Dimensionality Reduction", "PCA"]},
        {"topic": "Deep Learning", "subtopics": ["Neural Networks", "Backpropagation", "CNNs", "RNNs", "Transfer Learning"]},
        {"topic": "Data Wrangling", "subtopics": ["Pandas", "Missing Data", "Outlier Detection", "Data Pipelines"]},
        {"topic": "Model Deployment", "subtopics": ["MLflow", "Model Serving", "A/B Testing", "Monitoring"]},
    ],
    "AI Engineer": [
        {"topic": "LLM Fundamentals", "subtopics": ["Transformer Architecture", "Attention Mechanism", "Tokenization", "Context Window"]},
        {"topic": "Prompt Engineering", "subtopics": ["System Prompts", "Few-Shot Learning", "Chain of Thought", "JSON Mode"]},
        {"topic": "RAG", "subtopics": ["Embedding Models", "Vector Databases", "Chunking", "Retrieval Strategies"]},
        {"topic": "Fine-Tuning", "subtopics": ["LoRA", "PEFT", "Dataset Preparation", "RLHF"]},
        {"topic": "AI Agents", "subtopics": ["Tool Use", "ReAct Pattern", "Memory Systems", "Multi-Agent Orchestration"]},
        {"topic": "Evaluation", "subtopics": ["LLM-as-Judge", "BLEU/ROUGE", "Hallucination Detection", "Latency Benchmarks"]},
        {"topic": "MLOps", "subtopics": ["Model Versioning", "A/B Testing", "Observability", "Cost Optimization"]},
    ],
    "System Design": [
        {"topic": "Scalability", "subtopics": ["Horizontal vs Vertical Scaling", "Load Balancing", "Auto-Scaling"]},
        {"topic": "Databases at Scale", "subtopics": ["Sharding", "Replication", "CAP Theorem", "NoSQL vs SQL"]},
        {"topic": "Caching", "subtopics": ["Redis", "CDN", "Cache Invalidation", "Write-Through vs Write-Behind"]},
        {"topic": "Message Queues", "subtopics": ["Kafka", "RabbitMQ", "Event-Driven Architecture", "Idempotency"]},
        {"topic": "API Design", "subtopics": ["REST vs GraphQL", "Rate Limiting", "API Gateway", "Versioning"]},
        {"topic": "Distributed Systems", "subtopics": ["Consensus", "Leader Election", "Distributed Transactions", "Eventual Consistency"]},
        {"topic": "Monitoring", "subtopics": ["Observability", "Metrics", "Distributed Tracing", "Alerting"]},
    ],
    "HR Interview": [
        {"topic": "Background & Motivation", "subtopics": ["Career Goals", "Reason for Leaving", "Role Interest"]},
        {"topic": "Teamwork & Collaboration", "subtopics": ["Conflict Resolution", "Cross-Functional Teams", "Feedback"]},
        {"topic": "Leadership", "subtopics": ["Team Leadership", "Decision Making", "Delegation"]},
        {"topic": "Problem Solving", "subtopics": ["Approach to Challenges", "Failure Stories", "Learning Agility"]},
        {"topic": "Culture & Values", "subtopics": ["Work Style", "Core Values", "Remote Work", "Work-Life Balance"]},
    ],
    "Behavioral Interview": [
        {"topic": "Teamwork", "subtopics": ["Collaboration", "Conflict", "Feedback Given/Received"]},
        {"topic": "Leadership", "subtopics": ["Influence Without Authority", "Ownership", "Mentoring"]},
        {"topic": "Problem Solving", "subtopics": ["Ambiguity", "Data-Driven Decisions", "Creative Solutions"]},
        {"topic": "Delivery", "subtopics": ["Deadlines", "Prioritization", "Quality vs Speed"]},
        {"topic": "Growth", "subtopics": ["Failure", "Feedback", "Skill Development"]},
    ],
}

# Fallback for unknown roles
DEFAULT_TOPICS = [
    {"topic": "Problem Solving", "subtopics": ["Approach", "Algorithms", "Trade-offs"]},
    {"topic": "Technical Knowledge", "subtopics": ["Core Concepts", "Best Practices"]},
    {"topic": "Communication", "subtopics": ["Clarity", "Structure", "Listening"]},
    {"topic": "Experience", "subtopics": ["Projects", "Challenges", "Achievements"]},
]


class TopicMemory:
    """
    Manages topic history for a single interview session.
    
    Works with the asked_topics JSON field on InterviewSession.
    Each entry: {"topic": str, "subtopic": str | None, "difficulty": str, "question_text": str}
    """

    def __init__(self, asked_topics: List[Dict[str, Any]] = None):
        self._history: List[Dict[str, Any]] = asked_topics or []

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @property
    def covered_topics(self) -> List[str]:
        """Returns list of top-level topic names already asked."""
        return [entry["topic"] for entry in self._history]

    @property
    def covered_subtopics(self) -> List[str]:
        """Returns list of subtopics already asked."""
        return [entry.get("subtopic", "") for entry in self._history if entry.get("subtopic")]

    def format_for_prompt(self) -> str:
        """
        Formats the topic history as a concise string for injection into LLM prompts.
        Tells the LLM exactly what NOT to repeat.
        """
        if not self._history:
            return "(No topics covered yet — this is the first question.)"

        lines = []
        for i, entry in enumerate(self._history, 1):
            sub = f" > {entry['subtopic']}" if entry.get("subtopic") else ""
            lines.append(f"  {i}. {entry['topic']}{sub}")
        return "Topics already covered (DO NOT repeat these):\n" + "\n".join(lines)

    def get_next_suggested_topic(self, job_role: str) -> Optional[Dict[str, Any]]:
        """
        Returns the next uncovered topic from the progression map for the given role.
        Returns None if all mapped topics are exhausted.
        """
        progression = TOPIC_PROGRESSIONS.get(job_role, DEFAULT_TOPICS)
        covered = set(self.covered_topics)
        for topic_entry in progression:
            if topic_entry["topic"] not in covered:
                return topic_entry
        return None  # All topics exhausted

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record(self, topic: str, subtopic: Optional[str], difficulty: str, question_text: str):
        """Adds a new entry to the topic history."""
        self._history.append({
            "topic": topic,
            "subtopic": subtopic,
            "difficulty": difficulty,
            "question_text": question_text,
        })

    def to_list(self) -> List[Dict[str, Any]]:
        """Serializes history for storage back into InterviewSession.asked_topics."""
        return self._history
