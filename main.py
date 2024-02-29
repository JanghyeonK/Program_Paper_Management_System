import sys
import csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import bibtexparser


class AddPaperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Paper")
        self.setMinimumWidth(400)

        self.setStyleSheet("font-size: 14px;")

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

        self.bib_button = QPushButton("Import from BibTeX")
        self.bib_button.clicked.connect(self.import_from_bibtex)

        self.add_button = QPushButton("Add Paper")
        self.add_button.clicked.connect(self.add_paper)

        self.read_label = QLabel("Read:")
        self.read_combobox = QComboBox()
        self.read_combobox.addItems(["No", "Yes"])

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow(self.title_label, self.title_input)
        form_layout.addRow(self.author_label, self.author_input)
        form_layout.addRow(self.keywords_label, self.keywords_input)
        form_layout.addRow(self.year_label, self.year_input)
        form_layout.addRow(self.conference_label, self.conference_input)
        form_layout.addRow(self.journal_label, self.journal_input)
        form_layout.addRow(self.read_label, self.read_combobox)
        layout.addLayout(form_layout)
        layout.addWidget(self.bib_button)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def import_from_bibtex(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Import from BibTeX", "", "BibTeX Files (*.bib)")
        if file_path:
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

    def add_paper(self):
        title = self.title_input.text()
        authors = self.author_input.text()
        keywords = self.keywords_input.text()
        year = self.year_input.text()
        conference = self.conference_input.text()
        journal = self.journal_input.text()
        read = True if self.read_combobox.currentText() == "Yes" else False

        if title and authors:
            self.parent().add_paper_to_list({
                "title": title,
                "author": authors,
                "keywords": keywords,
                "year": year,
                "conference": conference,
                "journal": journal,
                "read": read
            })
            QMessageBox.information(self, "Success", "Paper added successfully.")
            self.accept()


class PaperInfoDialog(QDialog):
    def __init__(self, paper_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paper Information")
        self.setMinimumWidth(400)

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
        form_layout.addRow(self.read_label, self.read_combobox)
        form_layout.addRow(self.comment_label, self.comment_input)
        layout.addLayout(form_layout)
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

        self.paper_info["title"] = title
        self.paper_info["author"] = authors
        self.paper_info["keywords"] = keywords
        self.paper_info["year"] = year
        self.paper_info["conference"] = conference
        self.paper_info["journal"] = journal
        self.paper_info["read"] = read
        self.paper_info["comment"] = comment

        self.parent().update_table()  # 수정 후 테이블 업데이트

        self.accept()



class PaperManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paper Management System")
        self.setGeometry(200, 200, 800, 600)

        self.setMinimumSize(800, 600)
        self.setMinimumSize(400, 300)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["Title", "Authors", "Keywords", "Year", "Conference", "Journal", "Read"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_widget.doubleClicked.connect(self.display_paper_info)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, author, or keyword...")
        self.search_input.textChanged.connect(self.search_papers)

        self.add_button = QPushButton("Add Paper")
        self.add_button.clicked.connect(self.add_paper_dialog)

        self.delete_button = QPushButton("Delete Paper")
        self.delete_button.clicked.connect(self.delete_paper)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_to_csv)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_from_csv)

        self.add_button = QPushButton("Add Paper")
        self.add_button.clicked.connect(self.add_paper_dialog)

        self.delete_button = QPushButton("Delete Paper")
        self.delete_button.clicked.connect(self.delete_paper)

        # 좌우로 버튼을 정렬하기 위한 수평 레이아웃 생성
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.setContentsMargins(10, 10, 10, 10)  # 여백 조정
        # 버튼 간 간격 조정
        button_layout.setSpacing(10)
        # 각 버튼의 크기 정책 설정
        self.add_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.load_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


        # Main 레이아웃
        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.table_widget)
        layout.addLayout(button_layout)  # 버튼 레이아웃 추가

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.paper_database = []
        self.load_from_csv()
        self.update_table()

        completer = QCompleter(self.get_search_suggestions())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(completer)

    def update_table(self):
        self.table_widget.setRowCount(len(self.paper_database))
        for row, paper in enumerate(self.paper_database):
            title_item = QTableWidgetItem(paper.get("title", ""))
            title_item.setTextAlignment(Qt.AlignCenter)
            authors_item = QTableWidgetItem(paper.get("author", ""))
            authors_item.setTextAlignment(Qt.AlignCenter)
            keywords_item = QTableWidgetItem(paper.get("keywords", ""))
            keywords_item.setTextAlignment(Qt.AlignCenter)
            year_item = QTableWidgetItem(paper.get("year", ""))
            year_item.setTextAlignment(Qt.AlignCenter)
            conference_item = QTableWidgetItem(paper.get("conference", ""))
            conference_item.setTextAlignment(Qt.AlignCenter)
            journal_item = QTableWidgetItem(paper.get("journal", ""))
            journal_item.setTextAlignment(Qt.AlignCenter)
            read_item = QTableWidgetItem("Yes" if paper.get("read", False) else "No")
            read_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 0, title_item)
            self.table_widget.setItem(row, 1, authors_item)
            self.table_widget.setItem(row, 2, keywords_item)
            self.table_widget.setItem(row, 3, year_item)
            self.table_widget.setItem(row, 4, conference_item)
            self.table_widget.setItem(row, 5, journal_item)
            self.table_widget.setItem(row, 6, read_item)

            # 자동완성 기능을 위한 Completer 설정
            completer = QCompleter(self.get_search_suggestions())
            completer.setCaseSensitivity(Qt.CaseInsensitive)  # 대소문자 구분 없이 검색
            self.search_input.setCompleter(completer)

    def add_paper_dialog(self):
        dialog = AddPaperDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_table()

    def delete_paper(self):
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if selected_rows:
            row_indices = [idx.row() for idx in selected_rows]
            row_indices.sort(reverse=True)
            for row_index in row_indices:
                del self.paper_database[row_index]
            self.update_table()

    def add_paper_to_list(self, paper_info):
        self.paper_database.append(paper_info)
        self.update_table()

    def search_papers(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table_widget.rowCount()):
            match = False
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table_widget.setRowHidden(row, not match)

    def get_search_suggestions(self):
        suggestions = []
        for paper in self.paper_database:
            title = paper.get("title", "")
            author = paper.get("author", "").split(", ")
            keywords = paper.get("keywords", "").split(", ")  # 각 키워드를 분리하여 리스트로 변환
            suggestions.extend([title] + author + keywords)  # 타이틀, 저자, 키워드 모두 추천에 추가
        return suggestions

    def display_paper_info(self, item):
        row = item.row()
        selected_paper = self.paper_database[row]
        dialog = PaperInfoDialog(selected_paper, self)
        dialog.exec_()

    def save_to_csv(self):
        with open('paper_database.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Authors", "Keywords", "Year", "Conference", "Journal", "Read"])
            for paper in self.paper_database:
                writer.writerow([
                    paper.get("title", ""),
                    paper.get("author", ""),
                    paper.get("keywords", ""),
                    paper.get("year", ""),
                    paper.get("conference", ""),
                    paper.get("journal", ""),
                    "Yes" if paper.get("read", False) else "No"
                ])

    def load_from_csv(self):
        self.paper_database = []
        with open('paper_database.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.paper_database.append({
                    "title": row["Title"],
                    "author": row["Authors"],
                    "keywords": row["Keywords"],
                    "year": row["Year"],
                    "conference": row["Conference"],
                    "journal": row["Journal"],
                    "read": True if row["Read"] == "Yes" else False
                })
        self.update_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaperManagementApp()
    window.show()
    sys.exit(app.exec_())
