"""Module for generating interview questions"""
from openai import OpenAI
from typing import Optional

class QuestionGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.difficulty_level = "easy"

    def generate_questions(self, job_description: str = "", resume_text: str = "", source_type: str = "Both") -> Optional[str]:
        """Generate interview questions based on selected source"""
        try:
            # Construct prompt based on source type
            if source_type == "Job Description Only":
                prompt = f"""Give any 3 {self.difficulty_level} interview questions to be asked to the candidate based on the given Job/product description,
                and a simple answer which can be understood by a non technical hr. 
                Job Description: {job_description}
Format:            
Question:
    <Question>
Answer:
    <Answer>
                """
            elif source_type == "Resume Only":
                prompt = f"""Generate any 3 {self.difficulty_level} interview questions to be asked to the candidate  to assess the candidate based on their resume.
                Include simple answers that a non-technical HR can understand.
                Resume Content: {resume_text}
                Focus on the candidate's experience, skills, and background mentioned in the resume.
                
Format:            
Question:
    <Question>
Answer:
    <Answer>
                    
                """
            else:  # Both
                prompt = f"""Generate any 3 {self.difficulty_level} interview questions to be asked to the candidate that assess how well the candidate's background matches the job requirements.
                Include simple answers that a non-technical HR can understand. Give in Swedish.
                
                Job Description: {job_description}
                
                Candidate's Resume: {resume_text}
                
                Ensure the questions evaluate both the candidate's experience from the resume and their potential fit for the job requirements.
                
Format:            
Question:
    <Question>
Answer:
    <Answer>
                    
                """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful interview question generator that creates targeted and relevant questions based on the provided context."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=1.35
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating questions: {str(e)}"

    def adjust_difficulty(self, make_harder: bool) -> None:
        """Adjust the difficulty level of questions"""
        self.difficulty_level = "slightly harder" if make_harder else "easy"
