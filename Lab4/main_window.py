from PyQt5.QtWidgets import QMainWindow, QPushButton \
    , QFormLayout, QHBoxLayout, QVBoxLayout, QWidget \
    , QGroupBox, QDoubleSpinBox, QTextBrowser, QLayout
from matplotlib.figure import Figure
import matplotlib.animation as animation
from functools import partial
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from task import solve as run_task
from anim import generate_events, np, update_frame, init_animation

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 4 | Baskin")

        self.anim = None
        self.events = []
        self.t_max = 15.0
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)
        self.create_task_tab(layout)
        self.create_output_widget(layout)
        
        self.canvas = MplCanvas(self, width=5, height=4, dpi=80)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def create_output_widget(self, main_layout: QLayout):
        output_box = QGroupBox()
        output_box.setTitle("Output")

        layout = QHBoxLayout()

        output_widget = QTextBrowser()
        self.output = output_widget
        layout.addWidget(output_widget)

        output_box.setLayout(layout)
        main_layout.addWidget(output_box)

    def create_task_tab(self, main_layout: QLayout):
        task_box = QGroupBox()
        task_box.setTitle("Task Parameters")
        
        layout = QFormLayout()
        
        lambda_ = QDoubleSpinBox()
        lambda_.setDecimals(2)
        lambda_.setSingleStep(0.01)
        lambda_.setMinimum(0.1)
        lambda_.setMaximum(10.0)
        lambda_.setValue(2.0)

        mu = QDoubleSpinBox()
        mu.setDecimals(2)
        mu.setSingleStep(0.01)
        mu.setMinimum(0.1)
        mu.setMaximum(10.0)
        mu.setValue(3.0)

        button = QPushButton("Run")
        button.clicked.connect(lambda: self.handle_task(lambda_.value(), mu.value()))

        layout.addRow("lambda: ", lambda_)
        layout.addRow("mu: ", mu)
        layout.addRow(button)

        task_box.setLayout(layout)
        main_layout.addWidget(task_box)

    def start_animation(self, lam, mu):
        if self.anim is not None:
            if self.anim.event_source is not None:
                self.anim.event_source.stop()
            self.anim = None

        self.events = generate_events(lam, mu, self.t_max)
        frames = np.linspace(0, self.t_max, 300)
        self.anim = animation.FuncAnimation(
            self.canvas.fig,
            partial(update_frame, self.canvas.axes, self.events, self.t_max),
            frames=frames,
            init_func=partial(init_animation, self.canvas.axes, self.t_max),
            blit=False,
            repeat=False,
            interval=6.06,
        )
        self.canvas.draw()

    def handle_task(self, lambda_: float, mu: float):
        q_theor, a_theor, q_sim, a_sim, served, total, error_q, error_a = run_task(lambda_, mu)
        self.output.setText(f"System parameters:\n Request flow intensity: {lambda_}\n Service intensity: {mu}\n Service time: {1/mu:.4f}\n\n"\
                            f"Analytical solution:\n Relative throughput (Q): {q_theor}\n Absolute throughput (A): {a_theor}\n\n"\
                            f"Imitation model (1 000 000 requests):\n Served requests {served} from a total of {total}\n "\
                            f"Relative throughput (Q): {q_sim:.4f}\n Absolute throughput (A): {a_sim:.4f}\n "\
                            f"Simulation error for Q: {error_q:.2f}%\n Simulation error for A: {error_a:.2f}%")
        self.start_animation(lambda_, mu)