"""Module for matching resumes with job descriptions using OpenAI"""
from openai import OpenAI
from typing import Tuple, Dict
import json
import re

class ResumeJobMatcher:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def calculate_match(self, resume_text: str, job_description: str) -> Tuple[float, str, Dict]:
        """Calculate match percentage and provide detailed feedback"""
        try:
            prompt = f"""Compare the candidate's resume and job description, how likely it is that he could be hired based on an educated prediction and if the resume has similar skills to thatof the resume also make shure to consider how well can the aplicant do the required job.Based on that provide a score . and provide specific feedback.

            Job Description:
            {job_description}

            Resume:
            {resume_text}

            Provide your analysis in the following format (maintain the exact keys and structure):
            {{
                "percentage": <number between 0-100>,
                "level": "<either 'high', 'moderately high', 'moderate', or 'low'>",
                "explanation": "<brief explanation of the match>",
                "drawbacks": [
                    "<drawback 1>",
                    "<drawback 2>",
                    "..."
                ],
                "improvement_areas": [
                    "<improvement suggestion 1>",
                    "<improvement suggestion 2>",
                    "..."
                ]
            }}
            - Any similarity in skills, education, certifications, and experience between the candidate and the job description should  boost the percentage. *Even slight matches should be given considerable weight*.
            - *Assume the candidate possesses a strong ability to learn quickly and adapt to the job requirements.  This is a KEY factor in raising the percentage.  Actively seek out evidence of learning agility in the resume (e.g., diverse experiences, projects demonstrating initiative, mention of learning new tools/technologies).*
            - If even two requirement matches, the percentage should be in the moderately  range or higher.
            - *In the explanation, focus on the candidate's strengths and potential, even if they require some interpretation. Frame any gaps in experience as opportunities for growth and learning.*
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI recruiter that analyzes resume matches. You MUST return responses in valid JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            response_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)

            result = json.loads(response_text)
            percentage = float(result["percentage"])
            percentage = max(0, min(100, percentage))

            valid_levels = {"high", "moderately high", "moderate", "low"}
            level = result["level"].lower()
            if level not in valid_levels:
                if percentage >= 80:
                    level = "high"
                elif percentage >= 65:
                    level = "moderately high"
                elif percentage >= 45:
                    level = "moderate"
                else:
                    level = "low"

            feedback = {
                "drawbacks": result.get("drawbacks", []),
                "improvement_areas": result.get("improvement_areas", [])
            }

            return percentage, level, feedback

        except Exception as e:
            print(f"Error calculating match: {str(e)}")
            return 0.0, "low", {"drawbacks": [], "improvement_areas": []}
