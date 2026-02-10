import sys
import os
import threading
import logging
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTextEdit, QLineEdit, QPushButton, QLabel, 
                             QStatusBar, QMessageBox, QGroupBox, QSplitter)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QTextCursor, QFont

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from poi.core import POICore
from poi.interface.manager import ConfirmationManager
from poi.interface.models import ConfirmationRequest, UserDecision, DecisionType

class LogSignalEmitter(QObject, logging.Handler):
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter('%(levelname)s | %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

class GUIConfirmationManager(ConfirmationManager):
    request_oversight_signal = Signal(object)
    
    def __init__(self, iml, emitter_obj):
        super().__init__(iml)
        self.emitter_obj = emitter_obj
        self.decision = None
        self.condition = threading.Condition()

    def request_human_oversight(self, intent_type, context_signature, risk_level, action, params):
        request_id = "gui_" + str(os.urandom(4).hex())
        consequence = self._generate_consequence_summary(action, params, risk_level)
        
        req = ConfirmationRequest(
            request_id=request_id,
            intent_type=intent_type,
            context_signature=context_signature,
            risk_level=risk_level,
            action=action,
            params=params,
            consequence_summary=consequence
        )
        
        # Reset decision
        with self.condition:
            self.decision = None
            self.emitter_obj.request_oversight_signal.emit(req)
            # Wait for user input from GUI thread
            self.condition.wait()
            
        return UserDecision(request_id=request_id, decision=self.decision)

    def set_user_decision(self, decision_type: DecisionType):
        with self.condition:
            self.decision = decision_type
            self.condition.notify_all()

class EngineSignals(QObject):
    request_oversight_signal = Signal(object)
    status_signal = Signal(str)
    result_signal = Signal(object)

class EngineThread(QThread):
    def __init__(self, core, task, signals):
        super().__init__()
        self.core = core
        self.task = task
        self.signals = signals
        # Bridge the core callback to QT signals
        self.core.status_callback = lambda msg: self.signals.status_signal.emit(msg)

    def run(self):
        res = self.core.handle_request(self.task)
        self.signals.status_signal.emit("Ready")
        # self.signals.result_signal.emit(res)

class TariqMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Tariq AI POI - Control Interface")
        self.resize(1000, 700)
        
        # Init POI Core
        self.core = POICore()
        self.engine_signals = EngineSignals()
        
        # Replace Interface with GUI version
        self.gui_interface = GUIConfirmationManager(self.core.iml, self.engine_signals)
        self.core.interface = self.gui_interface
        
        self._setup_ui()
        self._setup_logging()
        self._connect_signals()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Progress / Status Bar (New in Phase 9.2)
        status_layout = QHBoxLayout()
        self.progress_label = QLabel("Status: Ready")
        self.progress_label.setStyleSheet("font-weight: bold; color: #007acc;")
        status_layout.addWidget(self.progress_label)
        main_layout.addLayout(status_layout)

        # Top Splitter: Transcript and Audit
        splitter = QSplitter(Qt.Horizontal)
        
        # Chat Transcript
        chat_group = QGroupBox("Chat Transcript")
        chat_layout = QVBoxLayout(chat_group)
        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setFont(QFont("Consolas", 10))
        chat_layout.addWidget(self.transcript)
        
        # Audit Log
        audit_group = QGroupBox("Audit Trail")
        audit_layout = QVBoxLayout(audit_group)
        self.audit_view = QTextEdit()
        self.audit_view.setReadOnly(True)
        self.audit_view.setFont(QFont("Consolas", 9))
        self.audit_view.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        audit_layout.addWidget(self.audit_view)
        
        splitter.addWidget(chat_group)
        splitter.addWidget(audit_group)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)

        # Oversight Panel (Hidden by default)
        self.oversight_panel = QGroupBox("🛡️ HUMAN OVERSIGHT REQUIRED")
        self.oversight_panel.setVisible(False)
        self.oversight_panel.setStyleSheet("QGroupBox { border: 2px solid red; color: red; font-weight: bold; }")
        oversight_layout = QVBoxLayout(self.oversight_panel)
        self.oversight_label = QLabel("Details...")
        oversight_layout.addWidget(self.oversight_label)
        
        btn_layout = QHBoxLayout()
        self.btn_once = QPushButton("Approve Once")
        self.btn_always = QPushButton("Approve Always")
        self.btn_reject = QPushButton("Reject")
        self.btn_revoke = QPushButton("Revoke Trust")
        
        for btn in [self.btn_once, self.btn_always, self.btn_reject, self.btn_revoke]:
            btn_layout.addWidget(btn)
        
        oversight_layout.addLayout(btn_layout)
        main_layout.addWidget(self.oversight_panel)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter task for Tariq AI...")
        self.input_field.returnPressed.connect(self.handle_send)
        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self.handle_send)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_send)
        main_layout.addLayout(input_layout)

        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        mode = "LIVE" if os.environ.get("DRY_RUN") == "0" else "DRY_RUN"
        self.statusBar.showMessage(f"System Mode: {mode} | Monitoring D:/TariqAI")

    def _setup_logging(self):
        self.log_emitter = LogSignalEmitter()
        self.log_emitter.log_signal.connect(self.append_audit)
        logging.getLogger().addHandler(self.log_emitter)

    def _connect_signals(self):
        self.engine_signals.status_signal.connect(self.progress_label.setText)
        self.engine_signals.request_oversight_signal.connect(self.show_oversight)
        self.btn_once.clicked.connect(lambda: self.resolve_oversight(DecisionType.APPROVE_ONCE))
        self.btn_always.clicked.connect(lambda: self.resolve_oversight(DecisionType.APPROVE_ALWAYS))
        self.btn_reject.clicked.connect(lambda: self.resolve_oversight(DecisionType.REJECT))
        self.btn_revoke.clicked.connect(lambda: self.resolve_oversight(DecisionType.REVOKE))

    def append_transcript(self, text, color="black"):
        self.transcript.append(f"<span style='color:{color}'>{text}</span>")

    def append_audit(self, msg):
        self.audit_view.append(msg)
        self.audit_view.moveCursor(QTextCursor.End)

    def handle_send(self):
        task = self.input_field.text().strip()
        if not task:
            return
        
        self.append_transcript(f"<b>USER:</b> {task}")
        self.input_field.clear()
        
        # Run in thread
        self.thread = EngineThread(self.core, task, self.engine_signals)
        self.thread.start()

    def show_oversight(self, req: ConfirmationRequest):
        msg = f"<b>INTENT:</b> {req.intent_type}<br>"
        msg += f"<b>RISK:</b> {req.risk_level}<br>"
        msg += f"<b>ACTION:</b> {req.action}<br>"
        msg += f"<b>CONSEQUENCE:</b> {req.consequence_summary}"
        self.oversight_label.setText(msg)
        self.oversight_panel.setVisible(True)
        self.btn_send.setEnabled(False)
        self.input_field.setEnabled(False)

    def resolve_oversight(self, decision: DecisionType):
        self.oversight_panel.setVisible(False)
        self.btn_send.setEnabled(True)
        self.input_field.setEnabled(True)
        self.gui_interface.set_user_decision(decision)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TariqMainWindow()
    window.show()
    sys.exit(app.exec())
