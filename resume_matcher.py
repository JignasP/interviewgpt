"""Module for matching resumes with job descriptions using OpenAI"""
from openai import OpenAI
from typing import Tuple
import json
import re

class ResumeJobMatcher:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def calculate_match(self, resume_text: str, job_description: str) -> Tuple[float, str]:
        """Calculate match percentage and level between resume and job description using GPT-3.5"""
        try:
            prompt = f"""Evaluate the candidate's resume against the job description to predict their likelihood of being hired. Focus on the similarity of skills, education, certifications, and the number of years of experience. Critically assess the candidate's *potential* ability to perform the required job, emphasizing transferable skills and learning aptitude.

            Job Description:
            {job_description}

            Resume:
            {resume_text}

            Provide your analysis in the following format (maintain the exact keys and structure):
            {{
                "percentage": <number between 0-100>,
                "level": "<either 'high', 'moderately high', 'moderate', or 'low'>",
                "explanation": "<brief explanation of the match, highlighting potential and transferable skills>"
            }}

            Scoring Rules:
            - Percentage: 30 to 100 (Start from 30 to ensure a baseline percentage acknowledging some level of qualification.  This is your starting point, and it *should* be adjusted upwards.)
            - Level:
              * "high" for 70-100%
              * "moderately high" for 50-69%
              * "moderate" for 40-49%
              * "low" for 30-39% (adjusting the lower bound of "low" to 30)
            - Any similarity in skills, education, certifications, and experience between the candidate and the job description should *significantly* boost the percentage. *Even slight matches should be given considerable weight*.
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
                temperature=0  # Lower temperature for more consistent outputs
            )

            # Get the response text
            response_text = response.choices[0].message.content.strip()

            # Try to extract JSON if it's embedded in other text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)

            # Parse the response
            result = json.loads(response_text)

            # Validate the percentage is within bounds
            percentage = float(result["percentage"])
            percentage = max(0, min(100, percentage))  # Ensure between 0 and 100

            # Validate the level
            valid_levels = {"high", "moderately high", "moderate", "low"}
            level = result["level"].lower()
            if level not in valid_levels:
                # Determine level based on percentage if invalid level provided
                if percentage >= 80:
                    level = "high"
                elif percentage >= 65:
                    level = "moderately high"
                elif percentage >= 45:
                    level = "moderate"
                else:
                    level = "low"

            return percentage, level

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            print(f"Raw response: {response_text}")
            return 0.0, "low"
        except Exception as e:
            print(f"Error calculating match: {str(e)}")
            return 0.0, "low"
