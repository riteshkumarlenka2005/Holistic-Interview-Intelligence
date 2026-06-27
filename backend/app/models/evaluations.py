from typing import List, Optional
from pydantic import BaseModel, Field

class EvaluationScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="The assigned score from 0 to 100")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this score from 0.0 to 1.0")

class InterviewEvaluation(BaseModel):
    schema_version: str = Field(default="1.0", description="Version of the evaluation schema")
    technical_evaluation: EvaluationScore
    communication_evaluation: EvaluationScore
    confidence_evaluation: EvaluationScore
    strengths: List[str] = Field(..., description="List of strengths demonstrated in the answer")
    weaknesses: List[str] = Field(..., description="List of weaknesses or gaps in the answer")
    improvements: List[str] = Field(..., description="Actionable improvement tips for the candidate")
    summary: str = Field(..., description="A cohesive 1-2 sentence summary of the evaluation")

class InterviewDecision(BaseModel):
    schema_version: str = Field(default="1.0", description="Version of the decision schema")
    next_action: str = Field(..., description="MUST be either 'NEXT_QUESTION' or 'FOLLOW_UP'")
    topic_focus: str = Field(..., description="The primary topic to focus on next")
    difficulty: str = Field(..., description="MUST be 'Easy', 'Easy-Medium', 'Medium', 'Hard', or 'Expert'")
    suggested_prompt: str = Field(..., description="A naturally phrased prompt/question for the candidate")
