from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import bibtexparser
import re

class PaperInfoDialog(QDialog):
    def __init__(self, paper_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paper Information")
        self.resize(1200, 1000)
        self.setMinimumSize(1200, 1000)
        self.setMaximumSize(1200, 1000)
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
        self.keywords_input.textChanged.connect(self.show_keyword_suggestions)  # 키워드 추천 표시

        self.suggestion_list = QListWidget()
        self.suggestion_list.itemClicked.connect(self.fill_keyword_from_suggestion)  # 추천 키워드 선택 시 입력 필드 채우기

        self.year_label = QLabel("Year:")
        self.year_input = QLineEdit(paper_info.get("year", ""))

        self.publication_label = QLabel("Publication:")
        self.publication_input = QLineEdit(paper_info.get("publication", ""))

        self.read_label = QLabel("Read:")
        self.read_combobox = QComboBox()
        self.read_combobox.addItems(["X", "O"])
        read_index = 1 if paper_info.get("read", False) else 0
        self.read_combobox.setCurrentIndex(read_index)

        self.comment_label = QLabel("Comment:")
        self.comment_input = QTextEdit(paper_info.get("comment", ""))

        # Get current path
        self.pdf_label = QLabel("Path pdf:")
        self.pdf_text = QLineEdit(paper_info.get("pdf_path", ""))
        self.pdf_text.setReadOnly(True)

        self.bib_label = QLabel("Path bib:")
        self.bib_text = QLineEdit(paper_info.get("bib_path", ""))
        self.bib_text.setReadOnly(True)

        # Drag and drop area for BibTeX and PDF files
        self.drop_area = QLineEdit()
        self.drop_area.setText("Drag and Drop BibTeX or PDF file here")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setReadOnly(True)
        self.drop_area.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #aaa; border-radius: 5px;")
        self.drop_area.setFont(QFont("Arial", 60, QFont.Bold))
        self.drop_area.setMinimumHeight(300)
        

        self.modify_button = QPushButton("Modify")
        self.modify_button.clicked.connect(self.modify_paper)


        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow(self.title_label, self.title_input)
        form_layout.addRow(self.author_label, self.author_input)
        form_layout.addRow(self.keywords_label, self.keywords_input)
        form_layout.addWidget(self.suggestion_list)  # 키워드 추천 목록 추가
        form_layout.addRow(self.year_label, self.year_input)
        form_layout.addRow(self.publication_label, self.publication_input)
        form_layout.addRow(self.comment_label, self.comment_input)
        form_layout.addRow(self.read_label, self.read_combobox)
        form_layout.addRow(self.bib_label, self.bib_text)
        form_layout.addRow(self.pdf_label, self.pdf_text)
        layout.addLayout(form_layout)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.modify_button)
        self.setLayout(layout)

        # 이미 있는 키워드에서 추천 목록을 가져옵니다.
        self.existing_keywords = self.get_existing_keywords()
        self.show_keyword_suggestions()

        # 드래그 앤 드롭을 처리할 이벤트 필터 추가
        self.comment_input.setAcceptDrops(False)
        self.drop_area.setAcceptDrops(True)
        self.drop_area.installEventFilter(self)
          
    def eventFilter(self, obj, event):
        if obj == self.drop_area:
            if event.type() == QEvent.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
                    return True
            elif event.type() == QEvent.Drop:
                urls = event.mimeData().urls()
                for url in urls:
                    file_path = url.toLocalFile()
                    file_name = os.path.basename(url.toLocalFile())  # 파일 경로에서 파일 이름 추출
                    # bib
                    if file_name.endswith(".bib"):
                        if file_name:
                            self.bib_text.setText(file_name)
                            with open(file_path, 'r') as bibtex_file:
                                bib_database = bibtexparser.load(bibtex_file)
                                if bib_database.entries:
                                    entry = bib_database.entries[0]
                                    self.title_input.setText(entry.get("title", ""))
                                    authors = entry.get("author", "")
                                    formatted_authors = self.reformat_names(authors)
                                    self.author_input.setText(formatted_authors)
                                    self.keywords_input.setText(entry.get("keywords", ""))
                                    self.year_input.setText(entry.get("year", ""))
                                    self.publication_input.setText(entry.get("journal", ""))
                                    if not self.publication_input.text():
                                        self.publication_input.setText(entry.get("conference", ""))
                                    if not self.publication_input.text():
                                        self.publication_input.setText(entry.get("booktitle", ""))

                    # pdf
                    elif file_name.endswith(".pdf"):
                        self.pdf_text.setText(file_name)


                event.accept()
                return True
        return super().eventFilter(obj, event)


    def get_existing_keywords(self):
        existing_keywords = set()
        for paper in self.parent().paper_database:
            keywords = paper.get("keywords", "").split(", ")
            for keyword in keywords:
                # 쉼표 다음에 나오는 단어만 추출하여 사용
                keyword = keyword.split(",")[0].strip()
                if keyword:  # 공백이 아닌 경우에만 추가
                    existing_keywords.add(keyword)
        return existing_keywords


    def show_keyword_suggestions(self):
        text = self.keywords_input.text().strip()
        last_word = text.split(",")[-1].strip().lower()
        suggestions = [keyword for keyword in self.existing_keywords if keyword.lower().startswith(last_word)]
        suggestions.sort()
        self.suggestion_list.clear()
        if suggestions:
            self.suggestion_list.addItems(suggestions)
            self.suggestion_list.setCurrentRow(0)
            self.suggestion_list.show()


    def fill_keyword_from_suggestion(self, item):
        selected_keyword = item.text()
        current_text = self.keywords_input.text().strip()
        if current_text:
            # 입력창의 마지막 쉼표를 기준으로 키워드를 추가합니다.
            last_comma_index = current_text.rfind(",")
            if last_comma_index != -1:
                updated_text = current_text[:last_comma_index] + ", " + selected_keyword
            else:
                updated_text = selected_keyword
            self.keywords_input.setText(updated_text)
        else:
            self.keywords_input.setText(selected_keyword)
        self.keywords_input.setFocus()


    def remove_special_characters(self, text):
        # 알파벳과 하이픈을 제외한 모든 문자 제거
        cleaned_text = re.sub(r'[^a-zA-Z\-]', '', text)
        return cleaned_text
    

    def reformat_names(self, name_string):
        try:
            # 유니코드 이스케이프 시퀀스를 일반 문자로 변환
            name_string = self.remove_special_characters(name_string)

            # 쉼표와 "and"로 이름 요소 분할
            names = [name.strip() for name in name_string.split("and")]
            reformatted_names = []
            for name in names:
                # 이름 요소에서 성과 이름 분리
                parts = name.split(",")
                if len(parts) == 2:
                    # 성과 이름이 모두 있는 경우
                    reformatted_names.append(f"{parts[1].strip()} {parts[0].strip()}")
                else:
                    # 성만 있는 경우
                    reformatted_names.append(parts[0].strip())
            # 포맷된 이름들을 쉼표로 구분하여 하나의 문자열로 결합
            return ", ".join(reformatted_names)
        except Exception as e:
            print(f"Error reformatting names: {e}")
            return name_string


    def is_duplicate_title(self, title):
        try:
            for paper in self.parent().paper_database:
                if paper["title"] == title:
                    return True
        except:
            pass
        return False


    def modify_paper(self):
        title = self.title_input.text()
        authors = self.author_input.text()
        keywords = self.keywords_input.text()
        year = self.year_input.text()
        publication = self.publication_input.text()
        read = True if self.read_combobox.currentText() == "O" else False
        comment = self.comment_input.toPlainText()
        path_pdf = self.pdf_text.text()
        path_bib = self.bib_text.text()

        self.paper_info["title"] = title
        self.paper_info["author"] = authors
        self.paper_info["keywords"] = keywords
        self.paper_info["year"] = year
        self.paper_info["publication"] = publication
        self.paper_info["read"] = read
        self.paper_info["comment"] = comment
        self.paper_info["pdf_path"] = path_pdf
        self.paper_info["bib_path"] = path_bib

        self.parent().update_table()  # 수정 후 테이블 업데이트
        self.parent().save_to_csv()
        self.accept()