"""Main application file""" 
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from datetime import datetime
import pytz
import os
from config import OPENAI_API_KEY, UI_CONFIG
from resume_matcher import ResumeJobMatcher
from question_generator import QuestionGenerator
from resume_processor import ResumeProcessor

class ModernInterviewGeneratorUI:
    def __init__(self):
        self.setup_window()
        self.setup_components()
        self.initialize_processors()
        self.resume_matcher = ResumeJobMatcher(OPENAI_API_KEY)
        self.simplified_resume_text = None
        self.simplified_resume_window = None

    def setup_window(self):
        """Initialize main window and configure appearance"""
        self.root = ctk.CTk()
        self.root.title("Interview Question Generator")
        self.root.geometry(UI_CONFIG['WINDOW_SIZE'])
        self.root.minsize(*UI_CONFIG['MIN_WINDOW_SIZE'])
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def initialize_processors(self):
        """Initialize resume processor and question generator"""
        if not OPENAI_API_KEY:
            self.show_error("OpenAI API key not found in environment variables")
            self.root.quit()
            return
        self.resume_processor = ResumeProcessor(OPENAI_API_KEY)
        self.question_generator = QuestionGenerator(OPENAI_API_KEY)
        self.uploaded_resume_path = None

    def setup_components(self):
        """Setup all UI components"""
        self.setup_main_frame()
        self.setup_header()
        self.setup_content_frame()
        self.setup_resume_section()
        self.setup_job_description_section()
        self.setup_buttons()
        self.setup_output_section()

    def setup_main_frame(self):
        """Setup main container frame"""
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def setup_header(self):
        """Setup header with datetime and user info"""
        self.header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UI_CONFIG['DARK_BG'],
            corner_radius=10
        )
        self.header_frame.pack(fill="x", pady=(0, 20))

        # DateTime display
        current_time = datetime.now(pytz.UTC)
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

        self.datetime_label = ctk.CTkLabel(
            self.header_frame,
            text=f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {formatted_time}",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            text_color=UI_CONFIG['SUCCESS_COLOR']
        )
        self.datetime_label.pack(fill="x", padx=20, pady=(15, 5))

        # User info
        self.user_label = ctk.CTkLabel(
            self.header_frame,
            text="Current User's Login: Username",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            text_color=UI_CONFIG['SUCCESS_COLOR']
        )
        self.user_label.pack(fill="x", padx=20, pady=(5, 15))

    def setup_content_frame(self):
        """Setup main content area"""
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

    def setup_resume_section(self):
        """Setup resume upload section"""
        self.resume_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=UI_CONFIG['DARK_BG'],
            corner_radius=10
        )
        self.resume_frame.pack(fill="x", pady=(0, 20))

        self.upload_button = ctk.CTkButton(
            self.resume_frame,
            text="Upload Resume (PDF)",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            height=UI_CONFIG['BUTTON_HEIGHT'],
            command=self.upload_resume,
            corner_radius=8
        )
        self.upload_button.pack(side="left", padx=20, pady=10)

        self.view_resume_button = ctk.CTkButton(
            self.resume_frame,
            text="View Simplified Resume",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            height=UI_CONFIG['BUTTON_HEIGHT'],
            command=self.show_simplified_resume,
            state="disabled",
            corner_radius=8
        )
        self.view_resume_button.pack(side="left", padx=5, pady=10)

        self.resume_label = ctk.CTkLabel(
            self.resume_frame,
            text="No resume uploaded",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            text_color=UI_CONFIG['DISABLED_COLOR']
        )
        self.resume_label.pack(side="left", padx=20, pady=10)

    def setup_job_description_section(self):
        """Setup job description input and feedback section"""
        # Container for JD and feedback
        self.jd_container = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.jd_container.pack(fill="x", pady=(0, 20))

        # Left side - Job Description
        self.jd_frame = ctk.CTkFrame(
            self.jd_container,
            fg_color="transparent"
        )
        self.jd_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.jd_label = ctk.CTkLabel(
            self.jd_frame,
            text="Enter Job Description:",
            font=(UI_CONFIG['FONT_FAMILY'], 14, "bold")
        )
        self.jd_label.pack(anchor="w", pady=(0, 5))

        self.jd_input = ctk.CTkTextbox(
            self.jd_frame,
            height=150,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            border_width=2,
            border_color="#333333",
            corner_radius=8
        )
        self.jd_input.pack(fill="both", expand=True)

        # Right side - Feedback section
        self.feedback_frame = ctk.CTkFrame(
            self.jd_container,
            fg_color=UI_CONFIG['DARK_BG'],
            corner_radius=10,
            width=300
        )
        self.feedback_frame.pack(side="right", fill="y", padx=(5, 0))
        self.feedback_frame.pack_propagate(False)

        self.feedback_title = ctk.CTkLabel(
            self.feedback_frame,
            text="Discrepancies And Additional Skills",
            font=(UI_CONFIG['FONT_FAMILY'], 14, "bold")
        )
        self.feedback_title.pack(padx=15, pady=(10, 5))

        self.feedback_text = ctk.CTkTextbox(
            self.feedback_frame,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            height=150,  # Match job description height
            wrap="word"
        )
        self.feedback_text.pack(fill="both", padx=15, pady=10)

    def setup_buttons(self):
        """Setup action buttons"""
        self.buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=(0, 20))

        # Add question source selection
        self.source_label = ctk.CTkLabel(
            self.buttons_frame,
            text="Generate questions based on:",
            font=(UI_CONFIG['FONT_FAMILY'], 12)
        )
        self.source_label.pack(side="left", padx=(0, 10))

        # Create a StringVar to store the selected option
        self.question_source = tk.StringVar(value="both")

        # Create a dropdown/combobox for selection
        self.source_dropdown = ctk.CTkOptionMenu(
            self.buttons_frame,
            values=["Job Description Only", "Resume Only", "Both"],
            variable=self.question_source,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            width=150,
            height=UI_CONFIG['BUTTON_HEIGHT']
        )
        self.source_dropdown.pack(side="left", padx=(0, 20))

        self.generate_button = ctk.CTkButton(
            self.buttons_frame,
            text="Generate Question",
            font=(UI_CONFIG['FONT_FAMILY'], 12, "bold"),
            height=UI_CONFIG['BUTTON_HEIGHT'],
            command=self.generate_question,
            corner_radius=8
        )
        self.generate_button.pack(side="left", padx=(0, 10))

        self.harder_button = ctk.CTkButton(
            self.buttons_frame,
            text="Make Harder",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            height=UI_CONFIG['BUTTON_HEIGHT'],
            fg_color=UI_CONFIG['ERROR_COLOR'],
            hover_color="#cc0000",
            command=lambda: self.adjust_difficulty(True),
            corner_radius=8
        )
        self.harder_button.pack(side="left", padx=5)

        self.reset_button = ctk.CTkButton(
            self.buttons_frame,
            text="Reset Difficulty",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            height=UI_CONFIG['BUTTON_HEIGHT'],
            fg_color="#666666",
            hover_color="#4d4d4d",
            command=lambda: self.adjust_difficulty(False),
            corner_radius=8
        )
        self.reset_button.pack(side="left", padx=5)

    def setup_output_section(self):
        """Setup output display section"""
        # Match indicator section
        self.match_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=UI_CONFIG['DARK_BG'],
            corner_radius=10
        )
        self.match_frame.pack(fill="x", pady=(0, 10))

        # Match indicator label
        self.match_label = ctk.CTkLabel(
            self.match_frame,
            text="Resume Match:",
            font=(UI_CONFIG['FONT_FAMILY'], 14, "bold")
        )
        self.match_label.pack(side="left", padx=20, pady=10)

        # Match percentage label
        self.match_percentage = ctk.CTkLabel(
            self.match_frame,
            text="",
            font=(UI_CONFIG['FONT_FAMILY'], 14, "bold")
        )
        self.match_percentage.pack(side="left", padx=5, pady=10)

        # Match level indicator
        self.match_level = ctk.CTkLabel(
            self.match_frame,
            text="",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            width=120,
            height=28,
            corner_radius=14
        )
        self.match_level.pack(side="left", padx=20, pady=10)

        # Question output section
        self.output_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=UI_CONFIG['DARK_BG'],
            corner_radius=10
        )
        self.output_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.qa_output = ctk.CTkTextbox(
            self.output_frame,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            wrap="word"
        )
        self.qa_output.pack(fill="both", expand=True, padx=10, pady=10)

    def upload_resume(self):
        """Handle resume upload and processing"""
        file_path = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not file_path:
            return

        try:
            self.uploaded_resume_path = file_path
            filename = os.path.basename(file_path)

            self.update_status("Processing resume...", "info")
            self.root.update()

            simplified = self.resume_processor.process_pdf(
                file_path,
                status_callback=self.update_status
            )

            if simplified:
                self.simplified_resume_text = simplified
                self.update_status(f"Uploaded: {filename}", "success")
                self.view_resume_button.configure(state="normal")
                self.update_match_indicator()
            else:
                self.update_status("Error processing resume", "error")
                self.view_resume_button.configure(state="disabled")

        except Exception as e:
            self.update_status(f"Error: {str(e)}", "error")
            self.uploaded_resume_path = None
            self.view_resume_button.configure(state="disabled")

    def show_simplified_resume(self):
        """Display simplified resume in a popup window"""
        if not self.uploaded_resume_path:
            self.update_status("No resume uploaded", "error")
            return

        simplified = self.resume_processor.get_cached_resume(self.uploaded_resume_path)
        if not simplified:
            self.update_status("Could not retrieve simplified resume", "error")
            return

        if self.simplified_resume_window:
            self.simplified_resume_window.destroy()

        self.simplified_resume_window = ctk.CTkToplevel(self.root)
        self.simplified_resume_window.title("Simplified Resume")
        self.simplified_resume_window.geometry("800x600")

        text_widget = ctk.CTkTextbox(
            self.simplified_resume_window,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", simplified)
        text_widget.configure(state="disabled")

    def update_status(self, message: str, status_type: str = "info"):
        """Update status label with appropriate color"""
        colors = {
            "success": UI_CONFIG['SUCCESS_COLOR'],
            "warning": UI_CONFIG['WARNING_COLOR'],
            "error": UI_CONFIG['ERROR_COLOR'],
            "info": UI_CONFIG['DISABLED_COLOR']
        }
        self.resume_label.configure(
            text=message,
            text_color=colors.get(status_type, colors["info"])
        )
        self.root.update()

    def update_match_indicator(self):
        """Update match indicator and feedback"""
        if not self.simplified_resume_text:
            self.feedback_text.configure(state="normal")
            self.feedback_text.delete("1.0", tk.END)
            self.feedback_text.insert("1.0", "Please upload a resume first.")
            self.feedback_text.configure(state="disabled")
            self.match_percentage.configure(text="")
            self.match_level.configure(text="")
            return

        job_description = self.jd_input.get("1.0", tk.END).strip()
        if not job_description:
            self.feedback_text.configure(state="normal")
            self.feedback_text.delete("1.0", tk.END)
            self.feedback_text.insert("1.0", "Please enter a job description.")
            self.feedback_text.configure(state="disabled")
            self.match_percentage.configure(text="")
            self.match_level.configure(text="")
            return

        try:
            # Show loading state
            self.match_percentage.configure(
                text="Analyzing...",
                text_color="white"
            )
            self.match_level.configure(
                text="LOADING",
                fg_color="#666666",
                text_color="white"
            )
            self.feedback_text.configure(state="normal")
            self.feedback_text.delete("1.0", tk.END)
            self.feedback_text.insert("1.0", "Analyzing...")
            self.root.update()

            match_percentage, match_level, feedback = self.resume_matcher.calculate_match(
                self.simplified_resume_text,
                job_description
            )

            # Update match indicators
            self.match_percentage.configure(
                text=f"{match_percentage:.1f}%",
                text_color="white"
            )
            self.match_level.configure(
                text=match_level.upper(),
                fg_color=UI_CONFIG['MATCH_COLORS'][match_level],
                text_color="white"
            )

            # Update feedback section
            self.feedback_text.configure(state="normal")
            self.feedback_text.delete("1.0", tk.END)

            # Display only drawbacks and improvements
            if feedback["Discrepancies"] or feedback["Skills"]:
                if feedback["Discrepancies"]:
                    self.feedback_text.insert("1.0", "Discrepancies:\n\n")
                    for drawback in feedback["Discrepancies"]:
                        self.feedback_text.insert(tk.END, f"• {drawback}\n")

                if feedback["Skills"]:
                    if feedback["Discrepancies"]:
                        self.feedback_text.insert(tk.END, "\n")
                    self.feedback_text.insert(tk.END, "Additional Skills:\n\n")
                    for tip in feedback["Skills"]:
                        self.feedback_text.insert(tk.END, f"• {tip}\n")
            else:
                if match_level == "high":
                    self.feedback_text.insert(tk.END,
                                              " Perfect Match!\nResume aligns exceptionally well with the job requirements.")
                else:
                    self.feedback_text.insert(tk.END, "No specific feedback available.")

            self.feedback_text.configure(state="disabled")

        except Exception as e:
            print(f"Error updating match indicator: {str(e)}")
            self.match_percentage.configure(
                text="Error",
                text_color=UI_CONFIG['ERROR_COLOR']
            )
            self.match_level.configure(
                text="ERROR",
                fg_color="#666666",
                text_color="white"
            )
            self.feedback_text.configure(state="normal")
            self.feedback_text.delete("1.0", tk.END)
            self.feedback_text.insert("1.0", "Error analyzing resume match")
            self.feedback_text.configure(state="disabled")
        finally:
            self.root.update()

    def generate_question(self):
        """Generate interview questions"""
        self.update_match_indicator()

        job_description = self.jd_input.get("1.0", tk.END).strip()
        selected_source = self.source_dropdown.get()

        # Validate inputs based on selection
        if selected_source in ["Job Description Only", "Both"] and not job_description:
            self.qa_output.delete("1.0", tk.END)
            self.qa_output.insert("1.0", "Please enter a job description.")
            return

        if selected_source in ["Resume Only", "Both"] and not self.simplified_resume_text:
            self.qa_output.delete("1.0", tk.END)
            self.qa_output.insert("1.0", "Please upload a resume.")
            return

        # Clear previous output
        self.qa_output.delete("1.0", tk.END)
        self.qa_output.insert("1.0", "Generating questions...")
        self.root.update()

        try:
            response = self.question_generator.generate_questions(
                job_description=job_description,
                resume_text=self.simplified_resume_text,
                source_type=selected_source
            )
            self.qa_output.delete("1.0", tk.END)
            self.qa_output.insert("1.0", response)
        except Exception as e:
            self.qa_output.delete("1.0", tk.END)
            self.qa_output.insert("1.0", f"Error generating questions: {str(e)}")

    def adjust_difficulty(self, make_harder: bool):
        """Adjust question difficulty and regenerate"""
        self.question_generator.adjust_difficulty(make_harder)
        self.generate_question()

    def show_error(self, message: str):
        """Display error message in a popup"""
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("Error")
        error_window.geometry("400x200")

        label = ctk.CTkLabel(
            error_window,
            text=message,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            wraplength=350
        )
        label.pack(expand=True, padx=20, pady=20)

        button = ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy
        )
        button.pack(pady=(0, 20))

    def update_clock(self):
        """Update datetime display"""
        current_time = datetime.now(pytz.UTC)
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        self.datetime_label.configure(
            text=f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {formatted_time}"
        )
        self.root.after(1000, self.update_clock)

    def run(self):
        """Start the application"""
        try:
            self.update_clock()  # Start the clock update
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {str(e)}")
            self.root.quit()


def main():
    """Main entry point"""
    try:
        app = ModernInterviewGeneratorUI()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()
