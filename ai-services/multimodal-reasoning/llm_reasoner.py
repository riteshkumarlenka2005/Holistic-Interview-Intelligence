"""
LLM Reasoner Module
Uses LLMs (OpenAI GPT or Google Gemini) for intelligent analysis and feedback
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os

# Lazy imports
openai = None
genai = None


def _load_openai():
    """Lazy load OpenAI"""
    global openai
    if openai is None:
        try:
            import openai as _openai
            openai = _openai
        except ImportError:
            raise ImportError("OpenAI required: pip install openai")
    return openai


def _load_gemini():
    """Lazy load Google Generative AI"""
    global genai
    if genai is None:
        try:
            import google.generativeai as _genai
            genai = _genai
        except ImportError:
            raise ImportError("Google GenAI required: pip install google-generativeai")
    return genai


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "openai"  # openai or gemini
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None


@dataclass
class FeedbackResult:
    """LLM-generated feedback result"""
    overall_assessment: str
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_feedback: Dict[str, str]
    actionable_tips: List[str]
    sample_responses: Optional[List[str]]
    follow_up_questions: List[str]


class LLMReasoner:
    """
    LLM-based reasoning for interview analysis.
    Provides intelligent feedback, answer evaluation, and coaching.
    """
    
    # System prompts for different tasks
    SYSTEM_PROMPTS = {
        "analyze_interview": """You are an expert interview coach analyzing a candidate's interview performance.
Provide constructive, actionable feedback that helps the candidate improve.
Be specific about what was done well and what needs improvement.
Consider both verbal and non-verbal communication aspects.""",

        "evaluate_answer": """You are an experienced hiring manager evaluating interview responses.
Assess the quality, relevance, and structure of the candidate's answer.
Use the STAR method (Situation, Task, Action, Result) as a framework when applicable.
Provide specific suggestions for improvement.""",

        "generate_feedback": """You are a supportive career coach providing personalized interview feedback.
Focus on practical, actionable advice the candidate can immediately apply.
Be encouraging while being honest about areas needing improvement.
Tailor feedback to the specific role and industry context.""",

        "suggest_improvements": """You are an interview preparation expert.
Based on the analysis provided, suggest specific practice exercises and improvements.
Provide example phrases and techniques the candidate can use.
Consider the balance between verbal content and non-verbal delivery."""
    }
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM reasoner.
        
        Args:
            config: LLM configuration or None for defaults
        """
        self.config = config or LLMConfig()
        self._client = None
        self._model = None
    
    def _ensure_client(self):
        """Ensure LLM client is initialized"""
        if self._client is not None:
            return
        
        api_key = self.config.api_key or os.getenv(
            "OPENAI_API_KEY" if self.config.provider == "openai" else "GOOGLE_API_KEY"
        )
        
        if not api_key:
            raise ValueError(f"API key not found for {self.config.provider}")
        
        if self.config.provider == "openai":
            _load_openai()
            self._client = openai.OpenAI(api_key=api_key)
        else:
            _load_gemini()
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self.config.model)
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make LLM API call"""
        self._ensure_client()
        
        if self.config.provider == "openai":
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        else:
            # Gemini
            prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self._model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens
                }
            )
            return response.text
    
    def analyze_interview_performance(
        self,
        speech_analysis: Dict,
        vision_analysis: Dict,
        fusion_result: Dict,
        question: Optional[str] = None,
        job_role: Optional[str] = None
    ) -> FeedbackResult:
        """
        Provide comprehensive interview performance analysis.
        
        Args:
            speech_analysis: Speech analysis results
            vision_analysis: Vision analysis results
            fusion_result: Multimodal fusion results
            question: The interview question asked
            job_role: Target job role for context
            
        Returns:
            FeedbackResult with detailed analysis
        """
        # Build context prompt
        context = self._build_analysis_context(
            speech_analysis, vision_analysis, fusion_result,
            question, job_role
        )
        
        prompt = f"""Analyze this interview performance and provide detailed feedback.

{context}

Provide your analysis in the following JSON format:
{{
    "overall_assessment": "A 2-3 sentence summary of the overall performance",
    "strengths": ["List of 3-5 specific strengths demonstrated"],
    "areas_for_improvement": ["List of 3-5 specific areas to work on"],
    "specific_feedback": {{
        "communication": "Feedback on verbal communication",
        "body_language": "Feedback on non-verbal cues",
        "content": "Feedback on answer content and structure",
        "confidence": "Feedback on projected confidence"
    }},
    "actionable_tips": ["List of 3-5 specific, actionable tips"],
    "follow_up_questions": ["List of 2-3 questions the interviewer might ask next"]
}}"""
        
        try:
            response = self._call_llm(
                self.SYSTEM_PROMPTS["analyze_interview"],
                prompt
            )
            result = self._parse_json_response(response)
            
            return FeedbackResult(
                overall_assessment=result.get("overall_assessment", ""),
                strengths=result.get("strengths", []),
                areas_for_improvement=result.get("areas_for_improvement", []),
                specific_feedback=result.get("specific_feedback", {}),
                actionable_tips=result.get("actionable_tips", []),
                sample_responses=result.get("sample_responses"),
                follow_up_questions=result.get("follow_up_questions", [])
            )
        except Exception as e:
            return self._generate_fallback_feedback(fusion_result, str(e))
    
    def evaluate_answer_quality(
        self,
        transcript: str,
        question: str,
        job_role: str,
        expected_topics: Optional[List[str]] = None
    ) -> Dict:
        """
        Evaluate the quality of an interview answer.
        
        Args:
            transcript: The candidate's response
            question: The interview question
            job_role: Target job role
            expected_topics: Optional list of expected topics/keywords
            
        Returns:
            Answer quality evaluation
        """
        expected_str = f"\nExpected topics to cover: {', '.join(expected_topics)}" if expected_topics else ""
        
        prompt = f"""Evaluate this interview answer:

Question: {question}
Job Role: {job_role}
{expected_str}

Candidate's Response:
{transcript}

Evaluate and provide:
1. Relevance score (0-100): How relevant is the answer to the question?
2. Completeness score (0-100): How complete is the answer?
3. Structure score (0-100): How well-structured is the response?
4. STAR compliance: Does it follow Situation-Task-Action-Result format?
5. Key points covered: What important points were included?
6. Missing elements: What should have been included?
7. Suggested improvements: How could this answer be improved?

Respond in JSON format."""
        
        try:
            response = self._call_llm(
                self.SYSTEM_PROMPTS["evaluate_answer"],
                prompt
            )
            return self._parse_json_response(response)
        except Exception as e:
            return {
                "error": str(e),
                "relevance_score": 50,
                "completeness_score": 50,
                "structure_score": 50,
                "suggestions": ["Unable to evaluate - please try again"]
            }
    
    def generate_improved_response(
        self,
        original_response: str,
        question: str,
        job_role: str,
        improvement_areas: List[str]
    ) -> str:
        """
        Generate an improved version of the candidate's response.
        
        Args:
            original_response: The original answer
            question: The interview question
            job_role: Target job role
            improvement_areas: Areas that need improvement
            
        Returns:
            Improved sample response
        """
        prompt = f"""The candidate gave the following response to an interview question.
Provide an improved version that addresses the identified weaknesses while maintaining the candidate's authentic voice.

Question: {question}
Job Role: {job_role}

Original Response:
{original_response}

Areas for Improvement:
{chr(10).join(f'- {area}' for area in improvement_areas)}

Provide an improved response that:
1. Maintains the candidate's key points and experiences
2. Addresses the improvement areas
3. Follows the STAR format where applicable
4. Sounds natural and authentic, not scripted

Improved Response:"""
        
        try:
            return self._call_llm(
                self.SYSTEM_PROMPTS["suggest_improvements"],
                prompt
            )
        except Exception as e:
            return f"Unable to generate improved response: {str(e)}"
    
    def generate_practice_question(
        self,
        job_role: str,
        difficulty: str = "medium",
        category: str = "behavioral",
        weak_areas: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate a practice interview question.
        
        Args:
            job_role: Target job role
            difficulty: easy, medium, or hard
            category: Question category (behavioral, technical, situational)
            weak_areas: Areas the candidate needs to practice
            
        Returns:
            Generated question with guidance
        """
        weak_str = f"\nFocus on these weak areas: {', '.join(weak_areas)}" if weak_areas else ""
        
        prompt = f"""Generate a {difficulty} {category} interview question for a {job_role} position.
{weak_str}

Provide:
1. The interview question
2. What the interviewer is looking for
3. Key points a strong answer should include
4. Common mistakes to avoid
5. A framework for structuring the answer

Respond in JSON format with keys: question, evaluation_criteria, key_points, common_mistakes, answer_framework"""
        
        try:
            response = self._call_llm(
                self.SYSTEM_PROMPTS["generate_feedback"],
                prompt
            )
            return self._parse_json_response(response)
        except Exception as e:
            return {
                "question": f"Tell me about a challenging situation you faced as a {job_role}.",
                "evaluation_criteria": "Looking for problem-solving skills and resilience",
                "key_points": ["Specific situation", "Your actions", "Results achieved"],
                "error": str(e)
            }
    
    def _build_analysis_context(
        self,
        speech: Dict,
        vision: Dict,
        fusion: Dict,
        question: Optional[str],
        job_role: Optional[str]
    ) -> str:
        """Build context string for LLM analysis"""
        parts = []
        
        if question:
            parts.append(f"Interview Question: {question}")
        if job_role:
            parts.append(f"Target Role: {job_role}")
        
        # Speech analysis summary
        if speech:
            parts.append("\n--- Speech Analysis ---")
            
            transcript = speech.get("transcription", {}).get("text", "")
            if transcript:
                parts.append(f"Transcript: {transcript[:500]}...")
            
            confidence = speech.get("confidence", {})
            if confidence:
                parts.append(f"Confidence Score: {confidence.get('overall_score', 0):.0%}")
            
            fillers = speech.get("fillers", {})
            if fillers:
                parts.append(f"Filler Rate: {fillers.get('filler_rate_per_minute', 0):.1f}/min")
            
            prosody = speech.get("prosody", {})
            pace = prosody.get("pace", {})
            if pace:
                parts.append(f"Speaking Pace: {pace.get('assessment', 'unknown')}")
        
        # Vision analysis summary
        if vision:
            parts.append("\n--- Visual Analysis ---")
            
            gaze = vision.get("gaze_analysis", {})
            if gaze:
                parts.append(f"Eye Contact: {gaze.get('eye_contact_percentage', 0):.0f}%")
            
            posture = vision.get("posture_analysis", {})
            if posture:
                parts.append(f"Posture: {posture.get('dominant_posture', 'unknown')}")
            
            expression = vision.get("expression_analysis", {})
            if expression:
                parts.append(f"Expression: {expression.get('dominant_expression', 'unknown')}")
        
        # Fusion results
        if fusion:
            parts.append("\n--- Integrated Analysis ---")
            parts.append(f"Communication Score: {fusion.get('communication_score', 0):.0%}")
            parts.append(f"Presence Score: {fusion.get('presence_score', 0):.0%}")
            parts.append(f"Authenticity: {fusion.get('authenticity_score', 0):.0%}")
            parts.append(f"Congruence: {fusion.get('congruence_score', 0):.0%}")
        
        return "\n".join(parts)
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response"""
        # Try to extract JSON from response
        import re
        
        # Look for JSON block
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try to parse entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}
    
    def _generate_fallback_feedback(
        self,
        fusion_result: Dict,
        error: str
    ) -> FeedbackResult:
        """Generate fallback feedback when LLM fails"""
        # Use fusion results to generate basic feedback
        strengths = []
        improvements = []
        
        if fusion_result.get("communication_score", 0) > 0.7:
            strengths.append("Clear verbal communication")
        else:
            improvements.append("Work on verbal clarity and fluency")
        
        if fusion_result.get("presence_score", 0) > 0.7:
            strengths.append("Professional presence")
        else:
            improvements.append("Improve posture and body language")
        
        if fusion_result.get("congruence_score", 0) > 0.7:
            strengths.append("Authentic communication style")
        else:
            improvements.append("Align verbal and non-verbal communication")
        
        return FeedbackResult(
            overall_assessment=f"Analysis based on metrics (LLM unavailable: {error})",
            strengths=strengths or ["Keep practicing with confidence"],
            areas_for_improvement=improvements or ["Continue developing interview skills"],
            specific_feedback={
                "note": "Detailed feedback unavailable - using metric-based analysis"
            },
            actionable_tips=[
                "Practice answering questions out loud",
                "Record yourself and review body language",
                "Prepare STAR-format stories for common questions"
            ],
            sample_responses=None,
            follow_up_questions=["What are your greatest strengths?"]
        )


def analyze_with_llm(
    speech_analysis: Dict,
    vision_analysis: Dict,
    fusion_result: Dict,
    config: Optional[Dict] = None
) -> Dict:
    """
    Convenience function for LLM analysis.
    
    Args:
        speech_analysis: Speech analysis results
        vision_analysis: Vision analysis results  
        fusion_result: Multimodal fusion results
        config: Optional LLM configuration
        
    Returns:
        LLM-generated feedback as dictionary
    """
    llm_config = LLMConfig(**config) if config else LLMConfig()
    reasoner = LLMReasoner(llm_config)
    
    result = reasoner.analyze_interview_performance(
        speech_analysis, vision_analysis, fusion_result
    )
    
    return {
        "overall_assessment": result.overall_assessment,
        "strengths": result.strengths,
        "areas_for_improvement": result.areas_for_improvement,
        "specific_feedback": result.specific_feedback,
        "actionable_tips": result.actionable_tips,
        "follow_up_questions": result.follow_up_questions
    }


def generate_feedback(analysis: Dict, question: str, role: str) -> Dict:
    """
    Generate feedback for a specific question response.
    
    Args:
        analysis: Complete analysis results
        question: The interview question
        role: Target job role
        
    Returns:
        Feedback as dictionary
    """
    reasoner = LLMReasoner()
    
    if "transcription" in analysis:
        transcript = analysis["transcription"].get("text", "")
    else:
        transcript = ""
    
    return reasoner.evaluate_answer_quality(transcript, question, role)
