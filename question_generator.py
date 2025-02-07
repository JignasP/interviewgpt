"""Module for generating interview questions"""
from openai import OpenAI
from typing import Optional


class QuestionGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.difficulty_level = "easy"

    def generate_questions(self, job_description: str) -> Optional[str]:
        """Generate interview questions based on job description"""
        try:
            prompt = f"""Give  any 3 {self.difficulty_level} questions for interview question for the given Job/product description,
            and a simple answer which can be understood by a non technical hr. 
            Job Description: {job_description}

            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful interview question generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating questions: {str(e)}"

    def adjust_difficulty(self, make_harder: bool) -> None:
        """Adjust the difficulty level of questions"""
        self.difficulty_level = "slightly harder" if make_harder else "easy"
