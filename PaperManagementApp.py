from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import csv
from PaperInfoDialog import PaperInfoDialog
from AddPaperDialog import AddPaperDialog


class PaperManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paper Management System")
        self.setWindowIcon(QIcon('icon.png'))  # 아이콘 파일의 경로를 전달하여 아이콘 설정
        self.setGeometry(200, 200, 1200, 600)
        self.setMinimumSize(1200, 600)

        # 글자 크기 크게하는 스타일 시트 생성
        font_size = "13pt"  # 원하는 글자 크기
        self.setStyleSheet(f"font-size: {font_size};")

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(9)
        self.table_widget.setHorizontalHeaderLabels(["Title", "Authors", "Keywords", "Read", "PDF", "bib", "Year", "Conf.", "Journal"])
        self.table_widget.setFixedWidth(self.width() - 40)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

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

        # 테이블 열 헤더를 클릭하여 정렬할 수 있도록 설정
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_table)
        # 테이블 헤더의 스타일 지정
        header_stylesheet = """
        QHeaderView::section {
            background-color: lightblue; /* 헤더의 배경색 */
            color: black; /* 헤더의 텍스트 색상 */
            font-size: 14pt; /* 헤더의 글자 크기 */
            font-weight: bold; /* 헤더의 글자 두께 */
            border: 1px solid black; /* 헤더의 테두리 스타일 */
        }
        """
        self.table_widget.horizontalHeader().setStyleSheet(header_stylesheet)
        # 테이블 열의 너비 조정
        self.init_table = True
        self.adjust_table_column_widths()
        # 테이블에서 아이템을 더블 클릭하면 해당 논문을 열도록 설정
        self.table_widget.itemDoubleClicked.connect(self.open_paper)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_table_column_widths()

    def adjust_table_column_widths(self):
        self.table_widget.setFixedWidth(self.width()-30)
        total_width = self.table_widget.width() - 40  # 여백을 고려하여 총 너비 계산
        column_count = self.table_widget.columnCount()

        # (["Title", "Authors", "Keywords", "Read", "PDF", "bib", "Year", "Conf.", "Journal"])
        # initialization
        if self.init_table :
            init_width = [300, 150, 150, 50, 50, 50, 50, 50, 50]
            for column in range(column_count):
                # 각 열의 비율 계산
                column_width = init_width[column]
                # 열의 너비 조정
                self.table_widget.setColumnWidth(column, column_width)
            self.init_table = False

        # 각 열의 비율을 구하기 위해 열들의 너비를 총합한 값 계산
        total_column_widths = sum(self.table_widget.columnWidth(column) for column in range(column_count))

        for column in range(column_count):
            # 각 열의 비율 계산
            column_ratio = self.table_widget.columnWidth(column) / total_column_widths
            # 열당 비율을 기준으로 해당 열의 너비 계산
            new_width = total_width * column_ratio
            # 열의 너비 조정
            self.table_widget.setColumnWidth(column, new_width)


    def sort_table(self, logical_index):
        self.table_widget.sortItems(logical_index, Qt.AscendingOrder)

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

            path_pdf_item = QTableWidgetItem("No" if not paper.get("pdf_path", "") else "Yes")
            path_pdf_item.setTextAlignment(Qt.AlignCenter)

            path_bib_item = QTableWidgetItem("No" if not paper.get("bib_path", "") else "Yes")
            path_bib_item.setTextAlignment(Qt.AlignCenter)

            # (["Title", "Authors", "Keywords", "Read", "PDF", "bib", "Year", "Conference", "Journal"])
            self.table_widget.setItem(row, 0, title_item)
            self.table_widget.setItem(row, 1, authors_item)
            self.table_widget.setItem(row, 2, keywords_item)
            self.table_widget.setItem(row, 3, read_item)
            self.table_widget.setItem(row, 4, path_pdf_item)
            self.table_widget.setItem(row, 5, path_bib_item)
            self.table_widget.setItem(row, 6, year_item)
            self.table_widget.setItem(row, 7, conference_item)
            self.table_widget.setItem(row, 8, journal_item)


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

    def open_paper(self, item):
        # 현재 선택된 행 가져오기
        row = self.table_widget.currentRow()
        # 선택된 행의 첫 번째 열에 있는 paper name 가져오기
        paper_name = self.table_widget.item(row, 0).text()

        # 선택된 paper name에 해당하는 논문 찾기
        selected_paper = None
        for paper in self.paper_database:
            if paper.get("title", "") == paper_name:
                selected_paper = paper
                break

        # 선택된 paper가 있을 경우에만 PaperInfoDialog 열기
        if selected_paper:
            dialog = PaperInfoDialog(selected_paper, self)
            dialog.exec_()


    def save_to_csv(self):
        with open('paper_database.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Authors", "Keywords", "Year", "Conference", "Journal", "Read", "Comment", "Path_pdf", "Path_bib"])
            for paper in self.paper_database:
                writer.writerow([
                    paper.get("title", ""),
                    paper.get("author", ""),
                    paper.get("keywords", ""),
                    paper.get("year", ""),
                    paper.get("conference", ""),
                    paper.get("journal", ""),
                    "Yes" if paper.get("read", False) else "No",
                    paper.get("comment", ""),
                    paper.get("pdf_path", ""),
                    paper.get("bib_path", ""),
                ])

    def load_from_csv(self):
        self.paper_database = []
        try:
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
                        "read": True if row["Read"] == "Yes" else False,
                        "comment": row["Comment"],
                        "pdf_path": row["Path_pdf"],
                        "bib_path": row["Path_bib"]
                    })
        except FileNotFoundError:
            pass
        self.update_table()