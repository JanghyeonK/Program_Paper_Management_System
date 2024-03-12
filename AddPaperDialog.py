from PyQt5.QtWidgets import *
import bibtexparser
import os
class AddPaperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Paper")
        self.resize(1000, 800)
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(x, y)

        # 글자 크기 크게하는 스타일 시트 생성
        font_size = "14pt"  # 원하는 글자 크기
        self.setStyleSheet(f"font-size: {font_size};")

        self.title_label = QLabel("Title:")
        self.title_input = QLineEdit()

        self.author_label = QLabel("Author(s):")
        self.author_input = QLineEdit()

        self.keywords_label = QLabel("Keywords:")
        self.keywords_input = QLineEdit()

        self.year_label = QLabel("Year:")
        self.year_input = QLineEdit()

        self.conference_label = QLabel("Conference:")
        self.conference_input = QLineEdit()

        self.journal_label = QLabel("Journal:")
        self.journal_input = QLineEdit()

        self.comment_label = QLabel("Comment:")
        self.comment_input = QTextEdit()

        self.read_label = QLabel("Read:")
        self.read_combobox = QComboBox()
        self.read_combobox.addItems(["No", "Yes"])

        self.bib_label = QLabel("BibTeX Path:")
        self.bib_input = QLineEdit()
        self.bib_input.setReadOnly(True)

        self.pdf_label = QLabel("PDF Path:")
        self.pdf_input = QLineEdit()
        self.pdf_input.setReadOnly(True)

        self.pdf_button = QPushButton("PDF Browse")
        self.pdf_button.clicked.connect(self.browse_pdf)

        self.bib_button = QPushButton("Import from BibTeX")
        self.bib_button.clicked.connect(self.import_from_bibtex)

        self.add_button = QPushButton("Add Paper")
        self.add_button.clicked.connect(self.add_paper)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow(self.title_label, self.title_input)
        form_layout.addRow(self.author_label, self.author_input)
        form_layout.addRow(self.keywords_label, self.keywords_input)
        form_layout.addRow(self.year_label, self.year_input)
        form_layout.addRow(self.conference_label, self.conference_input)
        form_layout.addRow(self.journal_label, self.journal_input)
        form_layout.addRow(self.comment_label, self.comment_input)
        form_layout.addRow(self.read_label, self.read_combobox)
        form_layout.addRow(self.bib_label, self.bib_input)
        form_layout.addRow(self.pdf_label, self.pdf_input)
        layout.addLayout(form_layout)
        layout.addWidget(self.bib_button)
        layout.addWidget(self.pdf_button)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def import_from_bibtex(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Import from BibTeX", "", "BibTeX Files (*.bib)")
        if file_path:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bib_relative_path = os.path.relpath(file_path, current_dir)
            self.bib_input.setText(bib_relative_path)
            with open(file_path, 'r') as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
                if bib_database.entries:
                    entry = bib_database.entries[0]
                    self.title_input.setText(entry.get("title", ""))
                    self.author_input.setText(entry.get("author", ""))
                    self.keywords_input.setText(entry.get("keywords", ""))
                    self.year_input.setText(entry.get("year", ""))
                    self.conference_input.setText(entry.get("conference", ""))
                    self.journal_input.setText(entry.get("journal", ""))

    def browse_pdf(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            pdf_relative_path = os.path.relpath(file_path, current_dir)
            self.pdf_input.setText(pdf_relative_path)

    def is_duplicate_title(self, title):
        for paper in self.parent().paper_database:
            if paper["title"] == title:
                return True
        return False

    def add_paper(self):
        title = self.title_input.text()
        authors = self.author_input.text()
        keywords = self.keywords_input.text()
        year = self.year_input.text()
        conference = self.conference_input.text()
        journal = self.journal_input.text()
        comment = self.comment_input.text()
        read = True if self.read_combobox.currentText() == "Yes" else False
        path_pdf = self.pdf_input.text()
        path_bib = self.bib_input.text()

        if not title or not authors:
            QMessageBox.warning(self, "Warning", "Please enter both title and authors.")
            return

        if self.is_duplicate_title(title):
            QMessageBox.warning(self, "Warning", "This paper already exists.")
            return

        if title and authors:
            self.parent().add_paper_to_list({
                "title": title,
                "author": authors,
                "keywords": keywords,
                "year": year,
                "conference": conference,
                "journal": journal,
                "comment": comment,
                "read": read,
                "pdf_path": path_pdf,
                "bib_path": path_bib
            })
            QMessageBox.information(self, "Success", "Paper added successfully.")
            self.accept()