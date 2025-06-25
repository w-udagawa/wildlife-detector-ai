"""
Wildlife Detector - メインGUIウィンドウ
PySide6ベースのデスクトップアプリケーションUI
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import threading
import time

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QGroupBox,
    QSplitter, QFrame, QScrollArea, QApplication, QStatusBar,
    QMenuBar, QToolBar
)
from PySide6.QtCore import Qt, QThread, QTimer, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QAction

from core.config import ConfigManager, AppConfig
from core.species_detector import SpeciesDetector, DetectionResult
from core.batch_processor import BatchProcessor, ProcessingStats
from utils.csv_exporter import CSVExporter
from utils.file_manager import FileManager

logger = logging.getLogger(__name__)

class ProcessingThread(QThread):
    """バッチ処理用スレッド"""
    
    progress_updated = Signal(int, int, str, str)  # current, total, status, filename
    processing_completed = Signal(list, object)  # results, stats
    processing_error = Signal(str)
    
    def __init__(self, image_files: List[str], config: AppConfig):
        super().__init__()
        self.image_files = image_files
        self.config = config
        self.processor = None
        self.is_cancelled = False
    
    def run(self):
        """処理実行"""
        try:
            # Convert AppConfig to dict for BatchProcessor
            config_dict = {
                'max_workers': self.config.max_workers,
                'batch_size': self.config.batch_size,
                'use_gpu': self.config.use_gpu,
                'confidence_threshold': self.config.confidence_threshold,
                'country_code': self.config.country_code,
                'timeout': self.config.timeout,
                'max_image_size_mb': self.config.max_image_size_mb
            }
            
            self.processor = BatchProcessor(config_dict)
            
            # 初期化進捗コールバック
            def init_progress_callback(message):
                if not self.is_cancelled:
                    self.progress_updated.emit(0, len(self.image_files), message, "")
            
            if not self.processor.initialize(init_progress_callback):
                self.processing_error.emit("バッチ処理器の初期化に失敗しました")
                return
            
            # 進捗コールバック設定
            def progress_callback(current, total, status, filename):
                if not self.is_cancelled:
                    self.progress_updated.emit(current, total, status, filename)
            
            # バッチ処理実行
            results = self.processor.process_batch(self.image_files, progress_callback)
            stats = self.processor.get_statistics()
            
            if not self.is_cancelled:
                self.processing_completed.emit(results, stats)
        
        except Exception as e:
            logger.error(f"処理スレッドエラー: {str(e)}")
            self.processing_error.emit(str(e))
        
        finally:
            if self.processor:
                self.processor.cleanup()
    
    def cancel_processing(self):
        """処理キャンセル"""
        self.is_cancelled = True
        if self.processor:
            self.processor.cancel_processing()

class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    
    def __init__(self):
        super().__init__()
        
        # 設定管理
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        
        # データ
        self.image_files = []
        self.results = []
        self.stats = None
        self.processing_thread = None
        
        # UI初期化
        self.init_ui()
        self.apply_config()
        
        logger.info("MainWindow初期化完了")
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("Wildlife Detector - 野生生物検出アプリケーション")
        self.setMinimumSize(1000, 700)
        
        # メニューバー作成
        self.create_menu_bar()
        
        # ツールバー作成
        self.create_toolbar()
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # タブ作成
        self.create_input_tab()
        self.create_progress_tab()
        self.create_results_tab()
        self.create_settings_tab()
        
        # ステータスバー
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("準備完了")
        
        # ウィンドウサイズ設定
        self.resize(self.config.window_width, self.config.window_height)
    
    def create_menu_bar(self):
        """メニューバー作成"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu('ファイル(&F)')
        
        open_files_action = QAction('画像ファイルを開く(&O)', self)
        open_files_action.setShortcut('Ctrl+O')
        open_files_action.triggered.connect(self.select_image_files)
        file_menu.addAction(open_files_action)
        
        open_folder_action = QAction('フォルダを開く(&D)', self)
        open_folder_action.setShortcut('Ctrl+D')
        open_folder_action.triggered.connect(self.select_image_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        import_csv_action = QAction('CSVから検出結果を読み込み(&I)', self)
        import_csv_action.triggered.connect(self.import_csv_results)
        file_menu.addAction(import_csv_action)
        
        file_menu.addSeparator()
        
        export_results_action = QAction('結果をエクスポート(&E)', self)
        export_results_action.triggered.connect(self.export_results)
        file_menu.addAction(export_results_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('終了(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 処理メニュー
        process_menu = menubar.addMenu('処理(&P)')
        
        start_processing_action = QAction('検出処理開始(&S)', self)
        start_processing_action.setShortcut('F5')
        start_processing_action.triggered.connect(self.start_processing)
        process_menu.addAction(start_processing_action)
        
        stop_processing_action = QAction('処理停止(&T)', self)
        stop_processing_action.setShortcut('Esc')
        stop_processing_action.triggered.connect(self.stop_processing)
        process_menu.addAction(stop_processing_action)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu('ヘルプ(&H)')
        
        about_action = QAction('Wildlife Detectorについて(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """ツールバー作成"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # ファイル選択ボタン
        open_files_btn = QPushButton("📁 ファイル選択")
        open_files_btn.clicked.connect(self.select_image_files)
        toolbar.addWidget(open_files_btn)
        
        # フォルダ選択ボタン
        open_folder_btn = QPushButton("📂 フォルダ選択")
        open_folder_btn.clicked.connect(self.select_image_folder)
        toolbar.addWidget(open_folder_btn)
        
        toolbar.addSeparator()
        
        # 処理開始ボタン
        self.start_btn = QPushButton("▶️ 検出処理開始")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        toolbar.addWidget(self.start_btn)
        
        # 処理停止ボタン
        self.stop_btn = QPushButton("⏹️ 処理停止")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        toolbar.addWidget(self.stop_btn)
    
    def create_input_tab(self):
        """入力・設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "📁 入力・設定")
        
        layout = QVBoxLayout(tab)
        
        # 入力ファイル/フォルダ選択
        input_group = QGroupBox("入力画像の選択")
        input_layout = QGridLayout(input_group)
        
        # ファイル選択
        input_layout.addWidget(QLabel("選択された画像:"), 0, 0)
        self.selected_files_label = QLabel("ファイルが選択されていません")
        self.selected_files_label.setStyleSheet("color: #666; font-style: italic;")
        input_layout.addWidget(self.selected_files_label, 0, 1)
        
        btn_layout = QHBoxLayout()
        select_files_btn = QPushButton("📄 ファイルを選択")
        select_files_btn.clicked.connect(self.select_image_files)
        btn_layout.addWidget(select_files_btn)
        
        select_folder_btn = QPushButton("📁 フォルダを選択")
        select_folder_btn.clicked.connect(self.select_image_folder)
        btn_layout.addWidget(select_folder_btn)
        
        clear_btn = QPushButton("🗑️ クリア")
        clear_btn.clicked.connect(self.clear_selection)
        btn_layout.addWidget(clear_btn)
        
        input_layout.addLayout(btn_layout, 1, 0, 1, 2)
        
        layout.addWidget(input_group)
        
        # 出力設定
        output_group = QGroupBox("出力設定")
        output_layout = QGridLayout(output_group)
        
        output_layout.addWidget(QLabel("出力フォルダ:"), 0, 0)
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setText(self.config.default_output_directory)
        output_layout.addWidget(self.output_path_edit, 0, 1)
        
        select_output_btn = QPushButton("📂 選択")
        select_output_btn.clicked.connect(self.select_output_folder)
        output_layout.addWidget(select_output_btn, 0, 2)
        
        layout.addWidget(output_group)
        
        # 検出設定
        detection_group = QGroupBox("検出設定")
        detection_layout = QGridLayout(detection_group)
        
        detection_layout.addWidget(QLabel("信頼度閾値:"), 0, 0)
        self.confidence_spinbox = QDoubleSpinBox()
        self.confidence_spinbox.setRange(0.0, 1.0)
        self.confidence_spinbox.setSingleStep(0.1)
        self.confidence_spinbox.setValue(self.config.confidence_threshold)
        detection_layout.addWidget(self.confidence_spinbox, 0, 1)
        
        detection_layout.addWidget(QLabel("バッチサイズ:"), 1, 0)
        self.batch_size_spinbox = QSpinBox()
        self.batch_size_spinbox.setRange(1, 128)
        self.batch_size_spinbox.setValue(self.config.batch_size)
        detection_layout.addWidget(self.batch_size_spinbox, 1, 1)
        
        detection_layout.addWidget(QLabel("最大ワーカー数:"), 2, 0)
        self.workers_spinbox = QSpinBox()
        self.workers_spinbox.setRange(1, 16)
        self.workers_spinbox.setValue(self.config.max_workers)
        detection_layout.addWidget(self.workers_spinbox, 2, 1)
        
        self.gpu_checkbox = QCheckBox("GPU使用")
        self.gpu_checkbox.setChecked(self.config.use_gpu)
        detection_layout.addWidget(self.gpu_checkbox, 3, 0, 1, 2)
        
        layout.addWidget(detection_group)
        
        # 画像ファイル一覧
        files_group = QGroupBox("選択された画像ファイル")
        files_layout = QVBoxLayout(files_group)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["ファイル名", "パス", "サイズ"])
        files_layout.addWidget(self.files_table)
        
        layout.addWidget(files_group)
    
    def create_progress_tab(self):
        """進捗タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "⏳ 処理進捗")
        
        layout = QVBoxLayout(tab)
        
        # 進捗情報
        progress_group = QGroupBox("処理進捗")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("待機中...")
        progress_layout.addWidget(self.progress_label)
        
        self.current_file_label = QLabel("")
        self.current_file_label.setStyleSheet("color: #666; font-size: 12px;")
        progress_layout.addWidget(self.current_file_label)
        
        layout.addWidget(progress_group)
        
        # 処理ログ
        log_group = QGroupBox("処理ログ")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # リアルタイム統計
        stats_group = QGroupBox("リアルタイム統計")
        stats_layout = QGridLayout(stats_group)
        
        self.stats_labels = {}
        stats_items = [
            ("処理済み画像", "processed"),
            ("検出成功", "success"),
            ("検出失敗", "failed"),
            ("平均処理時間", "avg_time")
        ]
        
        for i, (name, key) in enumerate(stats_items):
            stats_layout.addWidget(QLabel(f"{name}:"), i // 2, (i % 2) * 2)
            label = QLabel("0")
            label.setStyleSheet("font-weight: bold; color: #2196F3;")
            self.stats_labels[key] = label
            stats_layout.addWidget(label, i // 2, (i % 2) * 2 + 1)
        
        layout.addWidget(stats_group)
    
    def create_results_tab(self):
        """結果タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "📊 結果")
        
        layout = QVBoxLayout(tab)
        
        # 結果サマリー
        summary_group = QGroupBox("処理サマリー")
        summary_layout = QGridLayout(summary_group)
        
        self.summary_labels = {}
        summary_items = [
            ("総画像数", "total_images"),
            ("処理成功数", "processed_images"),
            ("検出成功数", "successful_detections"),
            ("総検出数", "total_detections"),
            ("処理時間", "processing_time"),
            ("平均処理時間", "average_time_per_image")
        ]
        
        for i, (name, key) in enumerate(summary_items):
            summary_layout.addWidget(QLabel(f"{name}:"), i // 3, (i % 3) * 2)
            label = QLabel("-")
            label.setStyleSheet("font-weight: bold;")
            self.summary_labels[key] = label
            summary_layout.addWidget(label, i // 3, (i % 3) * 2 + 1)
        
        layout.addWidget(summary_group)
        
        # 結果テーブル
        results_group = QGroupBox("検出結果")
        results_layout = QVBoxLayout(results_group)
        
        # 結果操作ボタン
        results_btn_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("📄 CSV出力")
        export_csv_btn.clicked.connect(self.export_csv)
        results_btn_layout.addWidget(export_csv_btn)
        
        organize_files_btn = QPushButton("📁 ファイル振り分け")
        organize_files_btn.clicked.connect(self.organize_files)
        results_btn_layout.addWidget(organize_files_btn)
        
        organize_from_csv_btn = QPushButton("📄 CSVから振り分け")
        organize_from_csv_btn.clicked.connect(self.organize_from_csv)
        results_btn_layout.addWidget(organize_from_csv_btn)
        
        results_btn_layout.addStretch()
        
        results_layout.addLayout(results_btn_layout)
        
        # 結果テーブル
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "画像", "検出数", "種名", "信頼度", "カテゴリ", "処理時間"
        ])
        results_layout.addWidget(self.results_table)
        
        layout.addWidget(results_group)
        
        # 種別統計
        species_group = QGroupBox("種別統計")
        species_layout = QVBoxLayout(species_group)
        
        self.species_table = QTableWidget()
        self.species_table.setColumnCount(3)
        self.species_table.setHorizontalHeaderLabels(["種名", "検出数", "平均信頼度"])
        species_layout.addWidget(self.species_table)
        
        layout.addWidget(species_group)
    
    def create_settings_tab(self):
        """設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "⚙️ 設定")
        
        layout = QVBoxLayout(tab)
        
        # 一般設定
        general_group = QGroupBox("一般設定")
        general_layout = QGridLayout(general_group)
        
        general_layout.addWidget(QLabel("テーマ:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.config.theme)
        general_layout.addWidget(self.theme_combo, 0, 1)
        
        general_layout.addWidget(QLabel("言語:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["ja", "en"])
        self.language_combo.setCurrentText(self.config.language)
        general_layout.addWidget(self.language_combo, 1, 1)
        
        self.auto_save_checkbox = QCheckBox("結果を自動保存")
        self.auto_save_checkbox.setChecked(self.config.auto_save_results)
        general_layout.addWidget(self.auto_save_checkbox, 2, 0, 1, 2)
        
        layout.addWidget(general_group)
        
        # パフォーマンス設定
        performance_group = QGroupBox("パフォーマンス設定")
        performance_layout = QGridLayout(performance_group)
        
        performance_layout.addWidget(QLabel("メモリ制限 (GB):"), 0, 0)
        self.memory_spinbox = QDoubleSpinBox()
        self.memory_spinbox.setRange(0.5, 64.0)
        self.memory_spinbox.setValue(self.config.memory_limit_gb)
        performance_layout.addWidget(self.memory_spinbox, 0, 1)
        
        performance_layout.addWidget(QLabel("最大画像サイズ (MB):"), 1, 0)
        self.max_image_size_spinbox = QDoubleSpinBox()
        self.max_image_size_spinbox.setRange(1.0, 500.0)
        self.max_image_size_spinbox.setValue(self.config.max_image_size_mb)
        performance_layout.addWidget(self.max_image_size_spinbox, 1, 1)
        
        self.resize_images_checkbox = QCheckBox("大きな画像をリサイズ")
        self.resize_images_checkbox.setChecked(self.config.resize_large_images)
        performance_layout.addWidget(self.resize_images_checkbox, 2, 0, 1, 2)
        
        layout.addWidget(performance_group)
        
        # 設定ボタン
        settings_btn_layout = QHBoxLayout()
        
        save_settings_btn = QPushButton("💾 設定保存")
        save_settings_btn.clicked.connect(self.save_settings)
        settings_btn_layout.addWidget(save_settings_btn)
        
        reset_settings_btn = QPushButton("🔄 デフォルトに戻す")
        reset_settings_btn.clicked.connect(self.reset_settings)
        settings_btn_layout.addWidget(reset_settings_btn)
        
        settings_btn_layout.addStretch()
        
        layout.addLayout(settings_btn_layout)
        
        layout.addStretch()
    
    def apply_config(self):
        """設定をUIに適用"""
        self.resize(self.config.window_width, self.config.window_height)
        
        # テーマ適用（簡易版）
        if self.config.theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 2px solid #555;
                    border-radius: 5px;
                    margin-top: 1ex;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
    
    def select_image_files(self):
        """画像ファイル選択"""
        file_dialog = QFileDialog()
        files, _ = file_dialog.getOpenFileNames(
            self,
            "画像ファイルを選択",
            "",
            "画像ファイル (*.jpg *.jpeg *.png *.bmp *.tiff *.tif);;すべてのファイル (*)"
        )
        
        if files:
            self.image_files.extend(files)
            self.update_file_list()
            logger.info(f"{len(files)} 個のファイルを選択しました")
    
    def select_image_folder(self):
        """画像フォルダ選択"""
        folder = QFileDialog.getExistingDirectory(self, "画像フォルダを選択")
        
        if folder:
            # フォルダ内の画像ファイルを検索
            folder_path = Path(folder)
            supported_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
            
            found_files = []
            for file_path in folder_path.rglob('*'):
                if file_path.suffix.lower() in supported_exts:
                    found_files.append(str(file_path))
            
            if found_files:
                self.image_files.extend(found_files)
                self.update_file_list()
                logger.info(f"フォルダから {len(found_files)} 個のファイルを発見しました")
            else:
                QMessageBox.information(self, "情報", "選択されたフォルダに画像ファイルが見つかりませんでした。")
    
    def select_output_folder(self):
        """出力フォルダ選択"""
        folder = QFileDialog.getExistingDirectory(self, "出力フォルダを選択")
        if folder:
            self.output_path_edit.setText(folder)
    
    def clear_selection(self):
        """選択クリア"""
        self.image_files.clear()
        self.update_file_list()
    
    def update_file_list(self):
        """ファイルリスト更新"""
        # 重複除去
        self.image_files = list(set(self.image_files))
        
        # ラベル更新
        if self.image_files:
            self.selected_files_label.setText(f"{len(self.image_files)} 個のファイルが選択されています")
            self.selected_files_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.selected_files_label.setText("ファイルが選択されていません")
            self.selected_files_label.setStyleSheet("color: #666; font-style: italic;")
        
        # テーブル更新
        self.files_table.setRowCount(len(self.image_files))
        for i, file_path in enumerate(self.image_files):
            path = Path(file_path)
            
            # ファイル名
            self.files_table.setItem(i, 0, QTableWidgetItem(path.name))
            
            # パス
            self.files_table.setItem(i, 1, QTableWidgetItem(str(path)))
            
            # サイズ
            try:
                size_mb = path.stat().st_size / (1024 * 1024)
                size_text = f"{size_mb:.2f} MB"
            except:
                size_text = "不明"
            self.files_table.setItem(i, 2, QTableWidgetItem(size_text))
        
        # 処理開始ボタンの有効/無効
        self.start_btn.setEnabled(len(self.image_files) > 0)
    
    def start_processing(self):
        """処理開始"""
        if not self.image_files:
            QMessageBox.warning(self, "警告", "画像ファイルが選択されていません。")
            return
        
        if not self.output_path_edit.text().strip():
            QMessageBox.warning(self, "警告", "出力フォルダが選択されていません。")
            return
        
        # 設定更新
        self.update_config_from_ui()
        
        # UI状態更新
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.tab_widget.setCurrentIndex(1)  # 進捗タブに切り替え
        
        # ログクリア
        self.log_text.clear()
        self.add_log("検出処理を開始します...")
        
        # 処理開始時刻を記録
        self._start_time = time.time()
        
        # 処理スレッド開始
        self.processing_thread = ProcessingThread(self.image_files, self.config)
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.processing_completed.connect(self.processing_completed)
        self.processing_thread.processing_error.connect(self.processing_error)
        self.processing_thread.start()
        
        logger.info("バッチ処理開始")
    
    def stop_processing(self):
        """処理停止"""
        if self.processing_thread and self.processing_thread.isRunning():
            self.add_log("処理停止を要求しています...")
            self.processing_thread.cancel_processing()
            
            # スレッド終了待機（最大5秒）
            if not self.processing_thread.wait(5000):
                self.processing_thread.terminate()
                self.add_log("処理を強制終了しました")
            else:
                self.add_log("処理が正常に停止されました")
        
        # UI状態復元
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        logger.info("バッチ処理停止")
    
    def update_config_from_ui(self):
        """UIから設定更新"""
        self.config.confidence_threshold = self.confidence_spinbox.value()
        self.config.batch_size = self.batch_size_spinbox.value()
        self.config.max_workers = self.workers_spinbox.value()
        self.config.use_gpu = self.gpu_checkbox.isChecked()
        self.config.default_output_directory = self.output_path_edit.text()
    
    def update_progress(self, current: int, total: int, status: str, filename: str):
        """進捗更新"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar.setValue(int(percentage))
            self.progress_label.setText(f"{status} ({current}/{total}) - {percentage:.1f}%")
        
        if filename:
            self.current_file_label.setText(f"現在の処理: {filename}")
        
        # リアルタイム統計更新
        self.stats_labels["processed"].setText(str(current))
        
        if current > 0:
            # 簡易統計（実際の値は処理完了時に更新）
            elapsed_time = time.time() - getattr(self, '_start_time', time.time())
            avg_time = elapsed_time / current if current > 0 else 0
            self.stats_labels["avg_time"].setText(f"{avg_time:.2f}秒")
    
    def processing_completed(self, results: List[DetectionResult], stats: ProcessingStats):
        """処理完了"""
        self.results = results
        self.stats = stats
        
        # UI状態復元
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 結果表示
        self.update_results_display()
        
        # 結果タブに切り替え
        self.tab_widget.setCurrentIndex(2)
        
        # 完了メッセージ
        stats_dict = stats.to_dict()
        message = (f"処理が完了しました！\n\n"
                  f"処理画像数: {stats_dict['processed_images']}/{stats_dict['total_images']}\n"
                  f"検出成功: {stats_dict['successful_detections']}\n"
                  f"総検出数: {stats_dict['total_detections']}\n"
                  f"処理時間: {stats_dict['processing_time']:.2f}秒")
        
        QMessageBox.information(self, "処理完了", message)
        
        self.add_log("処理が完了しました")
        logger.info("バッチ処理完了")
    
    def processing_error(self, error_message: str):
        """処理エラー"""
        # UI状態復元
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # エラーメッセージ表示
        QMessageBox.critical(self, "処理エラー", f"処理中にエラーが発生しました:\n\n{error_message}")
        
        self.add_log(f"エラー: {error_message}")
        logger.error(f"バッチ処理エラー: {error_message}")
    
    def update_results_display(self):
        """結果表示更新"""
        if not self.results or not self.stats:
            return
        
        # サマリー更新
        stats_dict = self.stats.to_dict()
        self.summary_labels["total_images"].setText(str(stats_dict['total_images']))
        self.summary_labels["processed_images"].setText(str(stats_dict['processed_images']))
        self.summary_labels["successful_detections"].setText(str(stats_dict['successful_detections']))
        self.summary_labels["total_detections"].setText(str(stats_dict['total_detections']))
        self.summary_labels["processing_time"].setText(f"{stats_dict['processing_time']:.2f}秒")
        self.summary_labels["average_time_per_image"].setText(f"{stats_dict['average_time_per_image']:.3f}秒")
        
        # 結果テーブル更新
        self.results_table.setRowCount(len(self.results))
        for i, result in enumerate(self.results):
            path = Path(result.image_path)
            
            # 画像名
            self.results_table.setItem(i, 0, QTableWidgetItem(path.name))
            
            # 検出数
            detection_count = len(result.detections)
            self.results_table.setItem(i, 1, QTableWidgetItem(str(detection_count)))
            
            # 種名（最も信頼度の高いもの）
            if result.detections:
                best = result.get_best_detection()
                species_name = best['common_name'] if best else "不明"
                confidence = best['confidence'] if best else 0.0
                category = best['category'] if best else "不明"
            else:
                species_name = "検出なし"
                confidence = 0.0
                category = "-"
            
            self.results_table.setItem(i, 2, QTableWidgetItem(species_name))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{confidence:.3f}"))
            self.results_table.setItem(i, 4, QTableWidgetItem(category))
            self.results_table.setItem(i, 5, QTableWidgetItem(f"{result.processing_time:.2f}秒"))
        
        # 種別統計テーブル更新
        species_counts = stats_dict.get('species_counts', {})
        self.species_table.setRowCount(len(species_counts))
        
        for i, (species, count) in enumerate(sorted(species_counts.items(), 
                                                  key=lambda x: x[1], 
                                                  reverse=True)):
            self.species_table.setItem(i, 0, QTableWidgetItem(species))
            self.species_table.setItem(i, 1, QTableWidgetItem(str(count)))
            
            # 平均信頼度計算（簡易版）
            confidences = []
            for result in self.results:
                for detection in result.detections:
                    if detection['common_name'] == species:
                        confidences.append(detection['confidence'])
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            self.species_table.setItem(i, 2, QTableWidgetItem(f"{avg_confidence:.3f}"))
    
    def export_csv(self):
        """CSV出力"""
        if not self.results:
            QMessageBox.warning(self, "警告", "出力する結果がありません。")
            return
        
        try:
            output_dir = self.output_path_edit.text() or str(Path.home() / "WildlifeDetector")
            exporter = CSVExporter(output_dir)
            
            output_files = exporter.export_all(self.results, self.stats)
            
            message = "CSV出力が完了しました！\n\n"
            for file_type, file_path in output_files.items():
                message += f"• {Path(file_path).name}\n"
            
            QMessageBox.information(self, "CSV出力完了", message)
            
            self.add_log("CSV出力が完了しました")
            
        except Exception as e:
            QMessageBox.critical(self, "CSV出力エラー", f"CSV出力中にエラーが発生しました:\n\n{str(e)}")
            logger.error(f"CSV出力エラー: {str(e)}")
    
    def organize_files(self):
        """ファイル振り分け"""
        if not self.results:
            QMessageBox.warning(self, "警告", "振り分ける結果がありません。")
            return
        
        try:
            output_dir = self.output_path_edit.text() or str(Path.home() / "WildlifeDetector")
            file_manager = FileManager(output_dir)
            
            # 確認ダイアログ
            reply = QMessageBox.question(
                self, 
                "ファイル振り分け確認",
                "画像ファイルを種別フォルダに振り分けますか？\n\n"
                "※ファイルは移動されます（元の場所からなくなります）",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 出力ディレクトリを指定
                output_dir = QFileDialog.getExistingDirectory(
                    self, 
                    "振り分け先フォルダを選択",
                    self.output_path_edit.text() or str(Path.home() / "WildlifeDetector")
                )
                
                if not output_dir:
                    return
                
                confidence_threshold = self.confidence_spinbox.value()
                result = file_manager.organize_images_by_species(
                    self.results,
                    output_base=output_dir,
                    copy_files=False,  # 移動モードに変更
                    confidence_threshold=confidence_threshold
                )
                
                if result['success']:
                    message = (f"ファイル振り分けが完了しました！\n\n"
                              f"処理済み: {result['processed_images']}/{result['total_images']}\n"
                              f"種別フォルダ数: {len(result['species_folders'])}\n"
                              f"出力ディレクトリ: {Path(result['output_directory']).name}")
                    
                    QMessageBox.information(self, "振り分け完了", message)
                    self.add_log("ファイル振り分けが完了しました")
                else:
                    QMessageBox.critical(self, "振り分けエラー", f"振り分け中にエラーが発生しました:\n\n{result.get('error', '不明なエラー')}")
        
        except Exception as e:
            QMessageBox.critical(self, "振り分けエラー", f"振り分け中にエラーが発生しました:\n\n{str(e)}")
            logger.error(f"ファイル振り分けエラー: {str(e)}")
    
    def export_results(self):
        """結果エクスポート（メニュー用）"""
        if not self.results:
            QMessageBox.warning(self, "警告", "エクスポートする結果がありません。")
            return
        
        self.export_csv()
    
    def save_settings(self):
        """設定保存"""
        try:
            # UI設定を収集
            self.config.theme = self.theme_combo.currentText()
            self.config.language = self.language_combo.currentText()
            self.config.auto_save_results = self.auto_save_checkbox.isChecked()
            self.config.memory_limit_gb = self.memory_spinbox.value()
            self.config.max_image_size_mb = self.max_image_size_spinbox.value()
            self.config.resize_large_images = self.resize_images_checkbox.isChecked()
            
            # ウィンドウサイズ保存
            self.config.window_width = self.width()
            self.config.window_height = self.height()
            
            # 設定保存
            if self.config_manager.save_config():
                QMessageBox.information(self, "設定保存", "設定が保存されました。")
                self.add_log("設定が保存されました")
            else:
                QMessageBox.warning(self, "設定保存エラー", "設定の保存に失敗しました。")
        
        except Exception as e:
            QMessageBox.critical(self, "設定保存エラー", f"設定保存中にエラーが発生しました:\n\n{str(e)}")
            logger.error(f"設定保存エラー: {str(e)}")
    
    def reset_settings(self):
        """設定リセット"""
        reply = QMessageBox.question(
            self, 
            "設定リセット確認",
            "設定をデフォルトに戻しますか？\n\n※この操作は元に戻せません。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.config_manager.reset_to_default():
                self.config = self.config_manager.get_config()
                self.apply_config()
                QMessageBox.information(self, "設定リセット", "設定がデフォルトにリセットされました。")
                self.add_log("設定がリセットされました")
    
    def import_csv_results(self):
        """CSVファイルから検出結果を読み込み"""
        file_dialog = QFileDialog()
        csv_file, _ = file_dialog.getOpenFileName(
            self,
            "検出結果CSVファイルを選択",
            "",
            "CSVファイル (*.csv);;すべてのファイル (*)"
        )
        
        if csv_file:
            try:
                from utils.csv_exporter import CSVExporter
                exporter = CSVExporter()
                
                # CSVから検出結果を読み込み
                self.results = exporter.import_from_csv(csv_file)
                
                # ファイルパスを確認し、必要に応じて絶対パスに変換
                csv_dir = Path(csv_file).parent
                missing_files = []
                
                for result in self.results:
                    file_path = Path(result.image_path)
                    
                    # 相対パスの場合、CSVファイルからの相対パスとして解決
                    if not file_path.is_absolute():
                        abs_path = csv_dir / file_path
                        if abs_path.exists():
                            result.image_path = str(abs_path)
                        else:
                            missing_files.append(str(file_path))
                    elif not file_path.exists():
                        missing_files.append(str(file_path))
                
                # 欠落ファイルがある場合は警告
                if missing_files:
                    warning_msg = f"以下の画像ファイルが見つかりませんでした:\n\n"
                    warning_msg += "\n".join(missing_files[:10])  # 最初の10件のみ表示
                    if len(missing_files) > 10:
                        warning_msg += f"\n... 他 {len(missing_files) - 10} 件"
                    
                    QMessageBox.warning(self, "ファイルが見つかりません", warning_msg)
                
                # 統計情報は簡易的に生成
                from core.batch_processor import ProcessingStats
                self.stats = ProcessingStats()
                self.stats.total_images = len(self.results)
                self.stats.processed_images = sum(1 for r in self.results if r.success)
                self.stats.successful_detections = sum(1 for r in self.results if r.success and r.detections)
                self.stats.total_detections = sum(len(r.detections) for r in self.results if r.success)
                self.stats.processing_time = sum(r.processing_time for r in self.results)
                
                # 種別カウント
                species_counts = {}
                for result in self.results:
                    if result.success:
                        for detection in result.detections:
                            species = detection.get('common_name', 'Unknown')
                            species_counts[species] = species_counts.get(species, 0) + 1
                self.stats.species_counts = species_counts
                
                # 結果表示を更新
                self.update_results_display()
                
                # 結果タブに切り替え
                self.tab_widget.setCurrentIndex(2)
                
                QMessageBox.information(
                    self, 
                    "読み込み完了", 
                    f"CSVファイルから{len(self.results)}件の検出結果を読み込みました。"
                )
                
                self.add_log(f"CSVファイルから{len(self.results)}件の検出結果を読み込みました: {Path(csv_file).name}")
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "読み込みエラー", 
                    f"CSVファイルの読み込み中にエラーが発生しました:\n\n{str(e)}"
                )
                logger.error(f"CSV読み込みエラー: {str(e)}")
    
    def organize_from_csv(self):
        """CSVファイルから読み込んだ結果を振り分け"""
        if not self.results:
            # 結果がない場合は、CSVファイルを選択させる
            self.import_csv_results()
            
            # 読み込みがキャンセルされた場合
            if not self.results:
                return
        
        # 通常の振り分け処理を実行
        self.organize_files()
    
    def show_about(self):
        """アプリケーション情報表示"""
        about_text = """
<h2>Wildlife Detector</h2>
<p><b>野生生物検出デスクトップアプリケーション</b></p>
<p>バージョン: 2.0.0</p>

<p>Google SpeciesNetを使用した高精度な野生生物検出システムです。</p>

<h3>主な機能:</h3>
<ul>
<li>94.5%の種レベル分類精度</li>
<li>数万枚規模のバッチ処理</li>
<li>CSV結果出力</li>
<li>画像の自動振り分け</li>
<li>詳細な統計情報</li>
</ul>

<h3>サポート:</h3>
<p>技術的な問題やご質問は開発チームまでお問い合わせください。</p>

<p><small>Powered by Google SpeciesNet</small></p>
        """
        
        QMessageBox.about(self, "Wildlife Detectorについて", about_text)
    
    def add_log(self, message: str):
        """ログメッセージ追加"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        
        # 自動スクロール
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """ウィンドウクローズイベント"""
        # 処理中の場合は確認
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "終了確認",
                "処理が実行中です。終了しますか？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            # 処理停止
            self.stop_processing()
        
        # 設定保存
        self.config.window_width = self.width()
        self.config.window_height = self.height()
        self.config_manager.save_config()
        
        event.accept()
        logger.info("アプリケーション終了")