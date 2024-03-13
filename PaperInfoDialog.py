from PyQt5.QtWidgets import *
import os
import bibtexparser

class PaperInfoDialog(QDialog):
    def __init__(self, paper_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paper Information")
        self.resize(1000, 800)
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(x, y)

        # 글자 크기 크게하는 스타일 시트 생성
        font_size = "13pt"  # 원하는 글자 크기
        self.setStyleSheet(f"font-size: {font_size};")

        self.paper_info = paper_info

        self.title_label = QLabel("Title:")
        self.title_input = QLineEdit(paper_info.get("title", ""))

        self.author_label = QLabel("Author(s):")
        self.author_input = QLineEdit(paper_info.get("author", ""))

        self.keywords_label = QLabel("Keywords:")
        self.keywords_input = QLineEdit(paper_info.get("keywords", ""))

        self.year_label = QLabel("Year:")
        self.year_input = QLineEdit(paper_info.get("year", ""))

        self.conference_label = QLabel("Conference:")
        self.conference_input = QLineEdit(paper_info.get("conference", ""))

        self.journal_label = QLabel("Journal:")
        self.journal_input = QLineEdit(paper_info.get("journal", ""))

        self.read_label = QLabel("Read:")
        self.read_combobox = QComboBox()
        self.read_combobox.addItems(["No", "Yes"])
        read_index = 1 if paper_info.get("read", False) else 0
        self.read_combobox.setCurrentIndex(read_index)

        self.comment_label = QLabel("Comment:")
        self.comment_input = QTextEdit(paper_info.get("comment", ""))

        # Get current path
        self.pdf_path_label = QLabel("Path pdf:")
        self.pdf_path_text = QLineEdit(paper_info.get("pdf_path", ""))
        self.pdf_path_text.setReadOnly(True)

        self.bib_path_label = QLabel("Path bib:")
        self.bib_path_text = QLineEdit(paper_info.get("bib_path", ""))
        self.bib_path_text.setReadOnly(True)

        # PDF 파일 추가 버튼
        self.add_pdf_button = QPushButton("Add PDF")
        self.add_pdf_button.clicked.connect(self.add_pdf_button_clicked)

        # Bib 파일 추가 버튼
        self.add_bib_button = QPushButton("Add Bib")
        self.add_bib_button.clicked.connect(self.add_bib_button_clicked)

        self.modify_button = QPushButton("Modify")
        self.modify_button.clicked.connect(self.modify_paper)


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
        layout.addLayout(form_layout)
        layout.addWidget(self.pdf_path_label)
        layout.addWidget(self.pdf_path_text)
        layout.addWidget(self.bib_path_label)
        layout.addWidget(self.bib_path_text)
        layout.addWidget(self.add_pdf_button)
        layout.addWidget(self.add_bib_button)
        layout.addWidget(self.modify_button)

        self.setLayout(layout)
    def modify_paper(self):
        title = self.title_input.text()
        authors = self.author_input.text()
        keywords = self.keywords_input.text()
        year = self.year_input.text()
        conference = self.conference_input.text()
        journal = self.journal_input.text()
        read = True if self.read_combobox.currentText() == "Yes" else False
        comment = self.comment_input.toPlainText()
        path_pdf = self.pdf_path_text.text()
        path_bib = self.bib_path_text.text()

        self.paper_info["title"] = title
        self.paper_info["author"] = authors
        self.paper_info["keywords"] = keywords
        self.paper_info["year"] = year
        self.paper_info["conference"] = conference
        self.paper_info["journal"] = journal
        self.paper_info["read"] = read
        self.paper_info["comment"] = comment
        self.paper_info["pdf_path"] = path_pdf
        self.paper_info["bib_path"] = path_bib

        self.parent().update_table()  # 수정 후 테이블 업데이트

        self.accept()

    def add_pdf_button_clicked(self):
        # PDF 파일 선택 다이얼로그 열기
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("PDF (*.pdf)")
        file_dialog.setViewMode(QFileDialog.Detail)
        try:
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                file_name = os.path.basename(file_path)
                self.pdf_path_text.setText(file_name)
        except:
            pass

    def add_bib_button_clicked(self):
        # Bib 파일 선택 다이얼로그 열기
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("BibTeX (*.bib)")
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)
            self.bib_path_text.setText(file_name)

            # BibTeX 파일 내용 읽기
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