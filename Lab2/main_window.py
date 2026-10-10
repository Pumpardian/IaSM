from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox \
    , QFormLayout, QHBoxLayout, QVBoxLayout, QWidget \
    , QTabWidget, QGroupBox, QSpinBox, QTextBrowser, QLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from task1 import solve as run_task1
from task2 import solve as run_task2

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 2 | Baskin")
        
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

        n = QSpinBox()
        n.setMinimum(1)
        n.setMaximum(1000000)
        n.setValue(1000000)

        button = QPushButton("Run")
        button.clicked.connect(lambda: self.handle_task_1(n.value()))

        layout.addRow("n: ", n)
        layout.addRow(button)

        task_box.setLayout(layout)
        self.tw.addTab(task_box, "Task 1")

    def create_task_2_tab(self):
        task_box = QGroupBox()
        task_box.setTitle("Task 2 Parameters")
        
        layout = QFormLayout()
        
        n = QSpinBox()
        n.setMinimum(1)
        n.setMaximum(1000000)
        n.setValue(1000000)

        p = QSpinBox()
        p.setMinimum(0)
        p.setMaximum(100)
        p.setValue(50)

        x = QSpinBox()
        x.setMinimum(1)
        x.setMaximum(100)
        x.setValue(7)

        button = QPushButton("Run")
        button.clicked.connect(lambda: self.handle_task_2(n.value(), p.value() / 100, x.value()))

        layout.addRow("n: ", n)
        layout.addRow("p: ", p)
        layout.addRow("x: ", x)
        layout.addRow(button)

        task_box.setLayout(layout)
        self.tw.addTab(task_box, "Task 2")

    def update_chart(self, values, bins=100):
        self.canvas.axes.clear()
        self.canvas.axes.hist(values, bins=bins, color="darkcyan", linewidth=2, edgecolor="black")
        self.canvas.axes.set_title("Results")
        self.canvas.axes.set_xlabel("Values")
        self.canvas.axes.set_ylabel("Frequency")
        self.canvas.draw()

    def handle_task_1(self, n: int):
        data, mx_p, mx_t, dx_p, dx_t, ci_mx, ci_dx = run_task1(n)
        self.output.setText(", ".join(str(v) for v in data))
        self.s_output.setText(f"MX_practical: {mx_p}\n\nDX_practical: {dx_p}\n\n"\
                            f"MX_theory: {mx_t}\n\nDX_theory: {dx_t}\n\n"\
                            f"CI_MX: {ci_mx}\n\nCI_DX: {ci_dx}")
        self.update_chart(data)

    def handle_task_2(self, n: int, p: float, x: int):
        data, mx_p, mx_t, dx_p, dx_t, ci_mx, ci_dx = run_task2(n, p, x)
        if data is None:
            QMessageBox.information(self, "Error", "Chi-square test fail")
            return
        self.output.setText(", ".join(str(v) for v in data))
        self.s_output.setText(f"MX_practical: {mx_p}\n\nDX_practical: {dx_p}\n\n"\
                            f"MX_theory: {mx_t}\n\nDX_theory: {dx_t}\n\n"\
                            f"CI_MX: {ci_mx}\n\nCI_DX: {ci_dx}")
        self.update_chart(data, range(min(data), max(data)))