import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QAbstractItemView,
)

from .fetcher import FetchThread
from .downloader import DownloadThread
from .models import Track
from .utils import format_duration, ffmpeg_available

COL_CHECK, COL_TITLE, COL_ORIGIN, COL_DURATION, COL_STATUS = range(5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube → MP3")
        self.resize(940, 660)

        self.tracks: list[Track] = []
        self.dest_folder = os.path.expanduser("~/Music")
        self.fetch_thread: FetchThread | None = None
        self.download_thread: DownloadThread | None = None

        self._build_ui()
        self._check_ffmpeg()

    # ---------------------------------------------------------- UI setup --
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("YouTube → MP3")
        title.setObjectName("appTitle")
        subtitle = QLabel(
            "Cole links de vídeos, playlists ou músicas — um por linha. "
            "Playlists e múltiplos links são expandidos em uma lista para você escolher."
        )
        subtitle.setObjectName("appSubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(subtitle)

        self.input_box = QPlainTextEdit()
        self.input_box.setPlaceholderText(
            "https://www.youtube.com/watch?v=...\n"
            "https://www.youtube.com/playlist?list=...\n"
            "(pode colar vários links, um por linha)"
        )
        self.input_box.setFixedHeight(110)
        root.addWidget(self.input_box)

        fetch_row = QHBoxLayout()
        self.fetch_btn = QPushButton("Buscar links")
        self.fetch_btn.setObjectName("primaryBtn")
        self.fetch_btn.clicked.connect(self.on_fetch)
        self.select_all_btn = QPushButton("Selecionar tudo")
        self.select_all_btn.clicked.connect(lambda: self._set_all_checked(True))
        self.select_none_btn = QPushButton("Desmarcar tudo")
        self.select_none_btn.clicked.connect(lambda: self._set_all_checked(False))
        fetch_row.addWidget(self.fetch_btn)
        fetch_row.addStretch()
        fetch_row.addWidget(self.select_all_btn)
        fetch_row.addWidget(self.select_none_btn)
        root.addLayout(fetch_row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["", "Título (clique para renomear)", "Origem", "Duração", "Status"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(COL_CHECK, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_TITLE, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(COL_ORIGIN, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_DURATION, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_STATUS, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemClicked.connect(self._on_item_clicked)
        self.table.itemChanged.connect(self._on_item_changed)
        root.addWidget(self.table, stretch=1)

        dest_row = QHBoxLayout()
        self.dest_label = QLabel(self._dest_label_text())
        self.dest_btn = QPushButton("Escolher pasta de destino...")
        self.dest_btn.clicked.connect(self.on_choose_folder)
        dest_row.addWidget(self.dest_label, stretch=1)
        dest_row.addWidget(self.dest_btn)
        root.addLayout(dest_row)

        download_row = QHBoxLayout()
        self.download_btn = QPushButton("Baixar selecionados")
        self.download_btn.setObjectName("primaryBtn")
        self.download_btn.clicked.connect(self.on_download)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        download_row.addWidget(self.download_btn)
        download_row.addWidget(self.progress, stretch=1)
        root.addLayout(download_row)

        self.status_label = QLabel("")
        root.addWidget(self.status_label)

    def _dest_label_text(self) -> str:
        return f"Pasta de destino: {self.dest_folder}"

    def _check_ffmpeg(self):
        if not ffmpeg_available():
            QMessageBox.warning(
                self,
                "ffmpeg não encontrado",
                "O ffmpeg não foi encontrado no PATH. Ele é necessário para converter "
                "o áudio para MP3.\n\nInstale-o e reinicie o app, por exemplo:\n"
                "  sudo apt install ffmpeg",
            )

    # ------------------------------------------------------------ Fetch --
    def on_fetch(self):
        text = self.input_box.toPlainText().strip()
        if not text:
            return
        urls = [line.strip() for line in text.splitlines() if line.strip()]
        if not urls:
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Buscando...")
        self.status_label.setText("Buscando informações dos links...")

        self.fetch_thread = FetchThread(urls)
        self.fetch_thread.tracks_found.connect(self._on_tracks_found)
        self.fetch_thread.error.connect(self._on_fetch_error)
        self.fetch_thread.log.connect(self.status_label.setText)
        self.fetch_thread.finished.connect(self._on_fetch_finished)
        self.fetch_thread.start()

    def _on_fetch_finished(self):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Buscar links")

    def _on_fetch_error(self, message: str):
        QMessageBox.critical(self, "Erro ao buscar", message)
        self.status_label.setText("Erro ao buscar links.")

    def _on_tracks_found(self, tracks: list[Track]):
        if not tracks:
            self.status_label.setText("Nenhuma faixa encontrada.")
            return
        self.tracks = tracks
        self._populate_table()
        self.status_label.setText(
            f"{len(tracks)} faixa(s) encontrada(s). Marque o que deseja baixar "
            "e clique no título para renomear o arquivo final."
        )

    def _populate_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.tracks))
        for row, track in enumerate(self.tracks):
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_item.setCheckState(
                Qt.CheckState.Checked if track.selected else Qt.CheckState.Unchecked
            )
            self.table.setItem(row, COL_CHECK, check_item)

            title_item = QTableWidgetItem(track.output_name)
            title_item.setFlags(
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, COL_TITLE, title_item)

            origin_item = QTableWidgetItem(track.origin)
            origin_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, COL_ORIGIN, origin_item)

            duration_item = QTableWidgetItem(format_duration(track.duration))
            duration_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, COL_DURATION, duration_item)

            status_item = QTableWidgetItem("Pendente")
            status_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, COL_STATUS, status_item)
        self.table.blockSignals(False)

    def _on_item_clicked(self, item: QTableWidgetItem):
        if item.column() == COL_TITLE:
            self.table.editItem(item)

    def _on_item_changed(self, item: QTableWidgetItem):
        row = item.row()
        if row >= len(self.tracks):
            return
        if item.column() == COL_CHECK:
            self.tracks[row].selected = item.checkState() == Qt.CheckState.Checked
        elif item.column() == COL_TITLE:
            new_name = item.text().strip()
            self.tracks[row].output_name = new_name or self.tracks[row].title

    def _set_all_checked(self, checked: bool):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.table.rowCount()):
            item = self.table.item(row, COL_CHECK)
            if item:
                item.setCheckState(state)

    # ------------------------------------------------------- Destination --
    def on_choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Escolher pasta de destino", self.dest_folder
        )
        if folder:
            self.dest_folder = folder
            self.dest_label.setText(self._dest_label_text())

    # ----------------------------------------------------------- Download --
    def on_download(self):
        selected = [(row, t) for row, t in enumerate(self.tracks) if t.selected]
        if not selected:
            QMessageBox.information(
                self, "Nada selecionado", "Selecione ao menos uma faixa para baixar."
            )
            return
        if not ffmpeg_available():
            QMessageBox.warning(
                self, "ffmpeg não encontrado", "Instale o ffmpeg antes de baixar."
            )
            return

        os.makedirs(self.dest_folder, exist_ok=True)

        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.progress.setValue(0)
        for row, _ in selected:
            self.table.item(row, COL_STATUS).setText("Na fila")

        self.download_thread = DownloadThread(selected, self.dest_folder)
        self.download_thread.item_status.connect(self._on_item_status)
        self.download_thread.item_progress.connect(self._on_item_progress)
        self.download_thread.overall_progress.connect(self._on_overall_progress)
        self.download_thread.item_error.connect(self._on_item_error)
        self.download_thread.finished_all.connect(self._on_download_finished)
        self.download_thread.start()

    def _on_item_status(self, row: int, text: str):
        item = self.table.item(row, COL_STATUS)
        if item:
            item.setText(text)

    def _on_item_progress(self, row: int, percent: int):
        item = self.table.item(row, COL_STATUS)
        if item and percent < 100:
            item.setText(f"Baixando... {percent}%")

    def _on_item_error(self, row: int, message: str):
        item = self.table.item(row, COL_STATUS)
        if item:
            item.setText("Erro")
        self.status_label.setText(f"Erro na faixa {row + 1}: {message}")

    def _on_overall_progress(self, done: int, total: int):
        self.progress.setMaximum(total)
        self.progress.setValue(done)
        self.status_label.setText(f"Baixando {done}/{total}...")

    def _on_download_finished(self):
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.status_label.setText("Download concluído.")
        QMessageBox.information(self, "Concluído", "Download e conversão concluídos.")
