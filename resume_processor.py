"""Module for handling resume processing with improved markdown display"""
import json
import os
from openai import OpenAI
from typing import Optional, Callable
from datetime import datetime
from rich.console import Console
import tkinter as tk
import tkinter.font as tkfont
import tkinter.scrolledtext as tkscroll
import re

class SimpleMarkdownText(tkscroll.ScrolledText):
    """Enhanced Markdown display widget"""

    def __init__(self, api_key: str, output_dir: str = "resume_outputs"):
        """Initialize the resume processor with OpenAI API key"""
        self.client = OpenAI(api_key=api_key)
        self.cache_file = os.path.join(os.path.expanduser("~"), ".resume_cache.json")
        self.output_dir = output_dir
        self.user_login = "JignasP"  # Current user's login
        self.current_datetime = "2025-02-07 07:20:09"  # Current UTC datetime
        self.console = Console()

        # Initialize Tkinter window and widgets
        self.root = None
        self.markdown_text = None

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def display_markdown(self, content: str) -> None:
        """Display markdown content using the enhanced markdown widget"""
        if not self.root:
            self._setup_gui()

        if self.markdown_text:
            self.markdown_text.delete(1.0, tk.END)

            # Format the content as proper markdown with clear section headers
            formatted_content = "# Resume Analysis\n\n"

            # Split the content by sections and format each
            sections = content.split('\n')
            for section in sections:
                if section.startswith('**') and ':' in section:
                    # Convert the section header to proper markdown format
                    header = section.split(':')[0].strip('*')
                    content = section.split(':', 1)[1].strip()
                    formatted_content += f"## **{header}**\n{content}\n\n"
                else:
                    formatted_content += f"{section}\n"

            self.markdown_text.insert_markdown(formatted_content)
            self.root.mainloop()

    def insert_bullet(self, position, text):
        self.insert(position, f"\u2022 {text}", "bullet")

    def insert_numbered(self, position, text):
        self.insert(position, f"{self.numbered_index}. {text}", "numbered")
        self.numbered_index += 1

    def insert_markdown(self, mkd_text):
        """Enhanced markdown parser"""
        current_text = ""

        for line in mkd_text.split("\n"):
            if line == "":
                self.numbered_index = 1
                self.insert("end", "\n")
                continue

            # Handle headers with bold text
            if line.startswith("## **"):
                line = line.replace("## **", "").replace("**", "")
                self.insert("end", line, "##")
                self.insert("end", "\n")
                continue

            # Handle headers
            if line.startswith("#"):
                tag = re.match(r"(#+) (.*)", line)
                if tag:
                    line = tag.group(2)
                    self.insert("end", line, tag.group(1))
                    self.insert("end", "\n")
                continue

            # Handle bold text
            parts = re.split(r"(\*\*.*?\*\*)", line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    # Remove the ** and apply bold tag
                    text = part[2:-2]
                    self.insert("end", text, "**")
                else:
                    self.insert("end", part)

            self.insert("end", "\n")

class ResumeProcessor:
    def __init__(self, api_key: str, output_dir: str = "resume_outputs"):
        """Initialize the resume processor with OpenAI API key"""
        self.client = OpenAI(api_key=api_key)
        self.cache_file = os.path.join(os.path.expanduser("~"), ".resume_cache.json")
        self.output_dir = output_dir
        self.user_login = "JignasP"  # Current user's login
        self.current_datetime = "2025-02-07 07:17:43"  # Current UTC datetime
        self.console = Console()

        # Initialize Tkinter window and widgets
        self.root = None
        self.markdown_text = None

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_pdf(self, pdf_path: str, status_callback: Optional[Callable] = None) -> Optional[str]:
        """Process a PDF resume and return analyzed content"""
        # Check cache first
        cached_result = self._get_cached(pdf_path)
        if cached_result:
            self._save_markdown(cached_result, pdf_path)  # Save cached result as markdown
            return cached_result

        try:
            # Extract text from PDF
            if status_callback:
                status_callback("Reading PDF...", "info")

            text = self._extract_pdf_text(pdf_path, status_callback)
            if not text:
                return None

            # Analyze text using OpenAI
            if status_callback:
                status_callback("Analyzing resume...", "info")

            analyzed_text = self._analyze_text(text)
            if analyzed_text:
                self._cache_result(pdf_path, analyzed_text)
                self._save_markdown(analyzed_text, pdf_path)  # Save new analysis as markdown

            return analyzed_text

        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            return None

    def _extract_pdf_text(self, pdf_path: str, status_callback: Optional[Callable]) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            from PyPDF2 import PdfReader  # Import here to avoid initial import issues
            pdf_reader = PdfReader(pdf_path)
            text = ""

            for i, page in enumerate(pdf_reader.pages):
                if status_callback:
                    status_callback(f"Processing page {i + 1}/{len(pdf_reader.pages)}...", "info")
                text += page.extract_text()

            return text
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return None

    def _analyze_text(self, text: str) -> Optional[str]:
        """Analyze resume text using OpenAI API with improved markdown formatting"""
        try:
            chunk_size = 4000
            chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

            analyzed_parts = []
            for chunk in chunks:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a helpful resume analyzer. Format your response using proper markdown with specific formatting requirements:

    1. All section headers must be formatted with both ## and wrapped in ** for bold:
       Example: ## **Section Header**

    2. Use bold text with double asterisks for emphasis:
       Example: **Important text**

    3. Use proper list formatting:
       * Use asterisks for bullet points
       * Indent sub-points properly

    Use this exact format:

    ## **Professional Summary**
    [Summary with **bold** key points]

    ## **Education**
    [Education details with **bold** institutions]

    ## **Skills**
    * **Technical Skills**: [List of skills]
    * **Soft Skills**: [List of skills]

    ## **Experience Analysis**
    [Analysis with **bold** company names and positions]
    """
                        },
                        {
                            "role": "user",
                            "content": f"Analyze this resume text and format the response exactly as shown in the example: {chunk}"
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                analyzed_text = response.choices[0].message.content.strip()
                # Ensure section headers are properly formatted
                analyzed_text = re.sub(r'^## ([^*])', r'## **\1**', analyzed_text, flags=re.MULTILINE)
                analyzed_parts.append(analyzed_text)

            return "\n\n".join(analyzed_parts)

        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return None

    def _setup_gui(self):
        """Setup the Tkinter GUI with enhanced markdown support"""
        self.root = tk.Tk()
        self.root.title("Resume Analysis")

        # Configure default font
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=12)

        # Create main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Add markdown text widget
        self.markdown_text = SimpleMarkdownText(main_frame, width=80, height=30, font=default_font)
        self.markdown_text.pack(fill="both", expand=True)

    def display_markdown(self, content: str) -> None:
        """Display markdown content using the enhanced markdown widget"""
        if not self.root:
            self._setup_gui()

        if self.markdown_text:
            self.markdown_text.delete(1.0, tk.END)
            self.markdown_text.insert_markdown(content)
            self.root.mainloop()

    def _get_cached(self, pdf_path: str) -> Optional[str]:
        """Get cached analysis result"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    return cache.get(pdf_path)
        except Exception:
            pass
        return None

    def _cache_result(self, pdf_path: str, result: str) -> None:
        """Cache analysis result"""
        try:
            cache = {}
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)

            cache[pdf_path] = result

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error caching result: {str(e)}")

    def get_cached_resume(self, pdf_path: str) -> Optional[str]:
        """
        Get cached resume analysis if available.
        This method maintains backward compatibility with the original implementation.
        """
        return self._get_cached(pdf_path)

    def _save_markdown(self, content: str, pdf_path: str) -> str:
        """Save the analysis as a markdown file with metadata"""
        try:
            filename = os.path.basename(pdf_path).replace('.pdf', '')
            output_path = os.path.join(self.output_dir, f"{filename}_analysis.md")

            markdown_content = f"""# Resume Analysis Report

## **Metadata**
- **Analysis Date (UTC)**: {self.current_datetime}
- **User**: {self.user_login}
- **Source File**: {filename}.pdf

## **Analysis Content**
{content}

---
*Generated by Resume Analyzer*
"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return output_path

        except Exception as e:
            print(f"Error saving markdown: {str(e)}")
            return ""