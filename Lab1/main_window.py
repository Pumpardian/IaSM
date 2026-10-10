from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit \
    , QFormLayout, QHBoxLayout, QVBoxLayout, QWidget, QMessageBox \
    , QTabWidget, QGroupBox, QSpinBox, QTextBrowser, QLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import tasks

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 1 | Baskin")
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)
        self.create_tab_widget(layout)
        self.create_output_widget(layout)
        
        self.canvas = MplCanvas(self, width=5, height=4, dpi=80)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def create_tab_widget(self, main_layout: QLayout):
        tab_widget = QTabWidget()
        self.tw = tab_widget

        self.create_task_1_tab()
        self.create_task_2_tab()
        self.create_task_3_tab()
        self.create_task_4_tab()
        
        main_layout.addWidget(tab_widget)

    def create_output_widget(self, main_layout: QLayout):
        output_box = QGroupBox()
        output_box.setTitle("Output")

        layout = QHBoxLayout()

        output_widget = QTextBrowser()
        self.output = output_widget
        layout.addWidget(output_widget)

        stats_output_widget = QTextBrowser()
        self.s_output = stats_output_widget
        layout.addWidget(stats_output_widget)

        output_box.setLayout(layout)
        main_layout.addWidget(output_box)

    def create_task_1_tab(self):
        task_box = QGroupBox()
        task_box.setTitle("Task 1 Parameters")
        
        layout = QFormLayout()
        
        event_probability = QSpinBox()
        event_probability.setValue(50)
        event_probability.setRange(1, 99)

        button = QPushButton("Run generator")
        button.clicked.connect(lambda: self.handle_task_1(event_probability.value()))

        layout.addRow("Event probability (%):", event_probability)
        layout.addRow(button)

        task_box.setLayout(layout)
        self.tw.addTab(task_box, "Task 1")

    def create_task_2_tab(self):
        task_box = QGroupBox()
        task_box.setTitle("Task 2 Parameters")
        
        layout = QFormLayout()
        
        event_probabilities = QTextEdit()
        event_probabilities.setText("0.5, 0.75, 0.25")

        button = QPushButton("Run generator")
        button.clicked.connect(lambda: self.handle_task_2(event_probabilities.toPlainText()))

        layout.addRow("Event probabilities (%, %, ...)", event_probabilities)
        layout.addRow(button)

        task_box.setLayout(layout)
        self.tw.addTab(task_box, "Task 2")

    def create_task_3_tab(self):
        task_box = QGroupBox()
        task_box.setTitle("Task 3 Parameters")
        
        layout = QFormLayout()
        
        main_event_probability = QSpinBox()
        main_event_probability.setValue(50)
        main_event_probability.setRange(1, 99)

        dep_event_probability = QSpinBox()
        dep_event_probability.setValue(50)
        dep_event_probability.setRange(1, 99)

        button = QPushButton("Run generator")
        button.clicked.connect(lambda: self.handle_task_3(main_event_probability.value(), dep_event_probability.value()))

        layout.addRow("Main event probability (%):", main_event_probability)
        layout.addRow("Dependant event probability (%):", dep_event_probability)
        layout.addRow(button)

        task_box.setLayout(layout)
        self.tw.addTab(task_box, "Task 3")

    def create_task_4_tab(self):
        task_box = QGroupBox()
        task_box.setTitle("Task 4 Parameters")
        
        layout = QFormLayout()
        
        event_probabilities = QTextEdit()
        event_probabilities.setText("0.3, 0.5, 0.2")

        button = QPushButton("Run generator")
        button.clicked.connect(lambda: self.handle_task_4(event_probabilities.toPlainText()))

        layout.addRow("Event probabilities (%, %, ...)", event_probabilities)
        layout.addRow(button)

        task_box.setLayout(layout)
        self.tw.addTab(task_box, "Task 4")
    
    def update_chart(self, labels, values, ylim = 1.0):
        self.canvas.axes.clear()
        x_positions = range(len(labels))
        bars =self.canvas.axes.bar(x_positions, values, color="darkcyan", linewidth=2)
        self.canvas.axes.bar_label(bars, padding=3)
        self.canvas.axes.set_xticks(x_positions)
        self.canvas.axes.set_xticklabels(labels)
        self.canvas.axes.set_title("Results")
        self.canvas.axes.set_ylabel("Frequency")
        self.canvas.axes.set_ylim(0, ylim)
        self.canvas.draw()

    def handle_task_1(self, event_probability: int):
        results = tasks.task_1(event_probability)
        practice = results.count(True) / len(results)

        self.output.setText(', '.join(str(b) for b in results))
        self.s_output.setText(f"Theory: {event_probability}\n\nPractice: {practice}")
        self.update_chart(labels=[True, False], values=[practice, 1 - practice])

    def handle_task_2(self, event_probabilities: str):
        ep_converted = []
        try:
            ep_converted = [float(value) for value in event_probabilities.split(",")]
        except Exception:
            QMessageBox.warning(self, "Input error", "Probabilities should be correct values divided by ','")
            return
        
        results = tasks.task_2(ep_converted)
        results_set = list(set(results))

        theory = [0] * len(results_set)
        practice = [0] * len(results_set)

        for result in results:
            index = results_set.index(result)
            practice[index] += 1
    
        for i, result in enumerate(results_set):
            cumulative = 1.0
            for j, event_result in enumerate(result):
                prob = ep_converted[j] if event_result else 1 - ep_converted[j]
                cumulative *= prob
            theory[i] = cumulative
        theory = [t * 1000000 for t in theory]
        self.output.setText(', '.join(str(f"[{', '.join([str(b) for b in sub_res])}]") for sub_res in results))
        self.s_output.setText(f"Set: {results_set}\n\nTheory: {theory}\n\nPractice: {practice}")
        self.update_chart(labels=results_set, values=practice, ylim=max(practice))


    def handle_task_3(self, main_event_probability: int, dep_event_probability: int):
        results = tasks.task_3(main_event_probability, dep_event_probability)
        theory = [main_event_probability / 100 * dep_event_probability / 100,
                   main_event_probability / 100 * (1 - dep_event_probability / 100),
                    (1 - main_event_probability / 100) * dep_event_probability / 100,
                     (1 - main_event_probability / 100) * (1 - dep_event_probability / 100)]
        practice = [results.count(0) / len(results), results.count(1) / len(results),
                     results.count(2) / len(results), results.count(3) / len(results)]

        self.output.setText(', '.join(str(r) for r in results))
        self.s_output.setText(f"Theory: {theory}\n\nPractice: {practice}")
        self.update_chart(labels=["A/B", "A/-B", "-A/B", "-A/-B"], values=practice)


    def handle_task_4(self, event_probabilities: str):
        ep_converted = []
        try:
            ep_converted = [float(value) for value in event_probabilities.split(",")]
        except Exception:
            QMessageBox.warning(self, "Input error", "Probabilities should be correct values divided by ','")
            return
        results = tasks.task_4(ep_converted)
        practice = [0] * len(ep_converted)
        for res in results:
            practice[res] += 1
        practice = [r / len(results) for r in practice]

        self.output.setText(', '.join(str(r) for r in results))
        self.s_output.setText(f"Theory: {event_probabilities}\n\nPractice: {practice}")
        self.update_chart(labels=range(len(ep_converted)), values=practice)