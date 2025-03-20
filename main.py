import sys
import openai
import dotenv
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
import re

dotenv.load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class CommentGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Main layout
        layout = QVBoxLayout()

        self.original_code_display = QTextEdit(self)
        self.original_code_display.setReadOnly(True)
        self.original_code_display.setPlaceholderText("Original Code (Read-only)")
        layout.addWidget(self.original_code_display)

        self.commented_code_display = QTextEdit(self)
        self.commented_code_display.setReadOnly(True)
        self.commented_code_display.setPlaceholderText("Generated Comments will appear here...")
        layout.addWidget(self.commented_code_display)

        """______________________________Buttons___________________________________________"""

        #browse
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)
        
        # generate
        self.generate_button = QPushButton("Generate Comments", self)
        self.generate_button.clicked.connect(self.generate_comments)
        layout.addWidget(self.generate_button)

        
        # remove
        self.remove_comments_button = QPushButton("Remove Comments", self)
        self.remove_comments_button.clicked.connect(self.remove_comments)
        layout.addWidget(self.remove_comments_button)

        # push
        self.push_button = QPushButton("Push (Overwrite File)", self)
        self.push_button.clicked.connect(self.overwrite_file)
        layout.addWidget(self.push_button)
        """______________________________________________________________________________"""

        self.setLayout(layout)
        self.setWindowTitle("Python Code Commenter")
        self.setGeometry(100, 100, 800, 600)

        # Store file path
        self.file_path = ""

    def browse_file(self):
        options = QFileDialog().options()

        file_path, _ = QFileDialog.getOpenFileName(self, "Open Python File", "", "Python Files (*.py);;All Files (*)", options=options)
        
        if file_path:
            self.file_path = file_path
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()

            # Show original code in the top window
            self.original_code_display.setPlainText(code)

    def generate_comments(self):
        if not self.file_path:
            self.commented_code_display.setPlainText("Please select a file first!")
            return

        original_code = self.original_code_display.toPlainText()

        # Call OpenAI API to generate comments
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that adds concise, DevOps-style comments to Python code."},
                {"role": "user", "content": f"Please add brief, functional comments inside the given python code."
                                            f"Do NOT include Markdown formatting (no triple backticks). Do not change the code itself in ANY WAY, only add small, necessary, and important comments for a reviewer to understand it."
                                            f"Do not change the code, do not change existing comments. ONLY ADD THEM ABOVE CLASSES OR FUNCTIONS, keep rest of the code as it is.:\n\n{original_code}"}
            ],
            max_tokens=1500,
            temperature=0.3
        )

        commented_code = response['choices'][0]['message']['content'].strip()

        # Display commented code in the bottom window
        self.commented_code_display.setPlainText(commented_code)

    def overwrite_file(self):
        """ Overwrites the original file with the commented version. """
        if not self.file_path:
            self.commented_code_display.setPlainText("Please select a file first!")
            return
        
        commented_code = self.commented_code_display.toPlainText()

        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(commented_code)

        self.commented_code_display.setPlainText("File successfully overwritten!")

    def remove_comments(self):
        """ Removes all # comments from the code while preserving docstrings. """
        if not self.file_path:
            self.commented_code_display.setPlainText("Please select a file first!")
            return

        code = self.original_code_display.toPlainText()
    
        
        in_triple_quotes = False
        quote_type = None
    
        def clean_line(line):
            nonlocal in_triple_quotes, quote_type
        
            stripped = line.strip()
        
            
            if stripped.startswith(('"""', "'''")):
                if in_triple_quotes and stripped.endswith(quote_type) and stripped != quote_type:
                    in_triple_quotes = False
                else:
                    in_triple_quotes = True   
                    quote_type = stripped[:3]  
                return line 
        
            if in_triple_quotes:
                return line
        
            
            return re.sub(r'\s*#.*', '', line).rstrip() 

        cleaned_code = "\n".join(clean_line(line) for line in code.splitlines())

        
        self.commented_code_display.setPlainText(cleaned_code)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommentGeneratorApp()
    window.show()
    sys.exit(app.exec())
