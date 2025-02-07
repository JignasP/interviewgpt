"""Main application file"""
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import pytz
from tkinter import filedialog
import os
from config import OPENAI_API_KEY, UI_CONFIG
from resume_processor import ResumeProcessor
from question_generator import QuestionGenerator
from resume_processor import ResumeProcessor, SimpleMarkdownText

class ModernInterviewGeneratorUI:
    def __init__(self):
        self.setup_window()
        self.setup_components()
        self.initialize_processors()

    def setup_window(self):
        """Initialize main window and configure appearance"""
        self.root = ctk.CTk()
        self.root.title("Interview Question Generator")
        self.root.geometry(UI_CONFIG['WINDOW_SIZE'])
        self.root.minsize(*UI_CONFIG['MIN_WINDOW_SIZE'])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.simplified_resume_window = None

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

        # DateTime display with specified format
        self.datetime_text = ctk.StringVar()
        self.datetime_label = ctk.CTkLabel(
            self.header_frame,
            textvariable=self.datetime_text,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            text_color=UI_CONFIG['SUCCESS_COLOR'],
            anchor="w",
            justify="left"
        )
        self.datetime_label.pack(fill="x", padx=20, pady=(15, 5))

        # User info with specified format
        self.user_label = ctk.CTkLabel(
            self.header_frame,
            text="Current User's Login: JignasP",
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            text_color=UI_CONFIG['SUCCESS_COLOR'],
            anchor="w",
            justify="left"
        )
        self.user_label.pack(fill="x", padx=20, pady=(5, 15))

        self.update_clock()

    def update_clock(self):
        """Update datetime display with specified format"""
        current_time = datetime.now(pytz.UTC)
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        self.datetime_text.set(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {formatted_time}")
        self.root.after(1000, self.update_clock)

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
        """Setup job description input section"""
        self.jd_label = ctk.CTkLabel(
            self.content_frame,
            text="Enter Job Description:",
            font=(UI_CONFIG['FONT_FAMILY'], 14, "bold")
        )
        self.jd_label.pack(anchor="w", pady=(0, 5))

        self.jd_input = ctk.CTkTextbox(
            self.content_frame,
            height=150,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            border_width=2,
            border_color="#333333",
            corner_radius=8
        )
        self.jd_input.pack(fill="x", pady=(0, 20))

    def setup_buttons(self):
        """Setup action buttons"""
        self.buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=(0, 20))

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
        self.output_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=UI_CONFIG['DARK_BG'],
            corner_radius=10
        )
        self.output_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.qa_output = ctk.CTkTextbox(
            self.output_frame,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            border_width=0,
            wrap="word"
        )
        self.qa_output.pack(fill="both", expand=True, padx=10, pady=10)

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

            simplified = self.resume_processor.process_pdf(
                file_path,
                status_callback=self.update_status
            )

            if simplified:
                self.update_status(f"Uploaded: {filename}", "success")
                self.view_resume_button.configure(state="normal")
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

        # Close existing window if open
        if self.simplified_resume_window:
            try:
                self.simplified_resume_window.destroy()
            except:
                pass

        # Create new popup window
        self.simplified_resume_window = ctk.CTkToplevel(self.root)
        self.simplified_resume_window.title("Simplified Resume")
        self.simplified_resume_window.geometry("800x600")
        self.simplified_resume_window.minsize(600, 400)

        # Create main frame with padding
        main_frame = ctk.CTkFrame(self.simplified_resume_window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create text widget with styling
        text_widget = ctk.CTkTextbox(
            main_frame,
            font=(UI_CONFIG['FONT_FAMILY'], 12),
            fg_color=UI_CONFIG['DARK_BG'],
            text_color="white",
            corner_radius=8,
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True)

        # Insert plain text content
        text_widget.insert(tk.END, simplified)

        # Make read-only
        text_widget.configure(state="disabled")

        # Bind window close event
        self.simplified_resume_window.protocol("WM_DELETE_WINDOW", self.on_popup_close)

    def on_popup_close(self):
        """Handle popup window closing"""
        if self.simplified_resume_window:
            self.simplified_resume_window.destroy()
            self.simplified_resume_window = None

    def generate_question(self):
        """Generate interview questions based on job description"""
        job_description = self.jd_input.get("1.0", tk.END).strip()
        if not job_description:
            self.qa_output.delete("1.0", tk.END)
            self.qa_output.insert("1.0", "Please enter a job description.")
            return

        # Clear previous output
        self.qa_output.delete("1.0", tk.END)
        self.qa_output.insert("1.0", "Generating questions...")
        self.root.update()

        try:
            response = self.question_generator.generate_questions(job_description)
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

    def run(self):
        """Start the application"""
        try:
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
