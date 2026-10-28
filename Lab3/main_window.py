from PyQt5.QtWidgets import QMainWindow, QPushButton, QSizePolicy, QHBoxLayout, \
    QVBoxLayout, QWidget, QGroupBox, QScrollArea, QTextBrowser, QLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
from scipy.stats import norm
from task1 import run_task as run_task1
from task2 import run_task as run_task2


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, projection=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection=projection)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(350)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 3 | Baskin")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        scroll.setWidget(content)

        self.create_tasks_widget(layout)
        self.create_output_widget(layout)

        self.canvases, self.toolbars = [], []
        for _ in range(3):
            cv = MplCanvas(self, width=5, height=4, dpi=80, projection='3d')
            self.canvases.append(cv)
            self.toolbars.append(NavigationToolbar(cv, self))

        self.canvases_hist, self.toolbars_hist = [], []
        for _ in range(2):
            cv = MplCanvas(self, width=5, height=4, dpi=80)
            self.canvases_hist.append(cv)
            self.toolbars_hist.append(NavigationToolbar(cv, self))

        self.canvases_plot, self.toolbars_plot = [], []
        for _ in range(2):
            cv = MplCanvas(self, width=5, height=4, dpi=80)
            self.canvases_plot.append(cv)
            self.toolbars_plot.append(NavigationToolbar(cv, self))

        self.canvases_hist3d, self.toolbars_hist3d = [], []
        for _ in range(1):
            cv = MplCanvas(self, width=5, height=4, dpi=80, projection='3d')
            self.canvases_hist3d.append(cv)
            self.toolbars_hist3d.append(NavigationToolbar(cv, self))

        for tb, cv in zip(self.toolbars, self.canvases):
            layout.addWidget(tb); layout.addWidget(cv)
        for tb, cv in zip(self.toolbars_hist3d, self.canvases_hist3d):
            layout.addWidget(tb); layout.addWidget(cv)
        for tb, cv in zip(self.toolbars_plot, self.canvases_plot):
            layout.addWidget(tb); layout.addWidget(cv)
        for tb, cv in zip(self.toolbars_hist, self.canvases_hist):
            layout.addWidget(tb); layout.addWidget(cv)

        self.hide_canvases()
        layout.addStretch()

    def hide_canvases(self):
        for cv in (self.canvases + self.canvases_hist +
                   self.canvases_plot + self.canvases_hist3d):
            cv.setVisible(False)
        for tb in (self.toolbars + self.toolbars_hist +
                   self.toolbars_plot + self.toolbars_hist3d):
            tb.setVisible(False)

    def show_canvases(self, wire, hist, plot, hist3d=False):
        canvases, toolbars = [], []
        if wire:   canvases += self.canvases;   toolbars += self.toolbars
        if hist:   canvases += self.canvases_hist; toolbars += self.toolbars_hist
        if plot:   canvases += self.canvases_plot; toolbars += self.toolbars_plot
        if hist3d: canvases += self.canvases_hist3d; toolbars += self.toolbars_hist3d

        for cv in canvases: cv.setVisible(True)
        for tb in toolbars: tb.setVisible(True)

    def create_tasks_widget(self, main_layout: QLayout):
        button1 = QPushButton("Run task1")
        button1.clicked.connect(lambda: self.handle_task_1())
        button2 = QPushButton("Run task2")
        button2.clicked.connect(lambda: self.handle_task_2())
        main_layout.addWidget(button1)
        main_layout.addWidget(button2)

    def create_output_widget(self, main_layout: QLayout):
        output_box = QGroupBox(); output_box.setTitle("Output")
        layout = QHBoxLayout()
        output_widget = QTextBrowser()
        self.output = output_widget
        layout.addWidget(output_widget)
        output_box.setLayout(layout)
        output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        output_box.setMinimumHeight(350)
        main_layout.addWidget(output_box)

    def update_wireframe(self, chart_number, values, title, labels):
        X, Y, Z = values
        ax = self.canvases[chart_number].axes
        ax.clear()
        ax.plot_wireframe(X, Y, Z, color='orange')
        ax.set_title(title)
        ax.set_xlabel(labels[0]); ax.set_ylabel(labels[1]); ax.set_zlabel(labels[2])
        self.canvases[chart_number].draw()

    def update_histogram(self, chart_number, x_sample, x_list, f_x, title, labels, bins=10):
        ax = self.canvases_hist[chart_number].axes
        ax.clear()
        ax.hist(x_sample, density=True, bins=bins,
                color="darkcyan", edgecolor="black", linewidth=1)
        if x_list is not None and f_x is not None:
            ax.plot(x_list, f_x(x_list), color="orange", linewidth=2)
        ax.set_title(title)
        ax.set_xlabel(labels[0]); ax.set_ylabel(labels[1])
        self.canvases_hist[chart_number].draw()

    def update_plot(self, chart_number, v, p_v, p_v_imp, title):
        ax = self.canvases_plot[chart_number].axes
        ax.clear()
        ax.plot(v, p_v, label="theoretical", color="gray", alpha=0.5, ls="--")
        ax.plot(v, p_v_imp, label="imperical", color="r", alpha=0.5)
        ax.set_title(title); ax.legend()
        self.canvases_plot[chart_number].draw()

    def update_hist3d(self, chart_number, positions, heights, dx, dy,
                    title, labels, xticks=None, yticks=None, surface=None):
        ax = self.canvases_hist3d[chart_number].axes
        ax.clear()

        Xp, Yp = positions
        ax.bar3d(Xp, Yp, np.zeros_like(Xp), dx, dy, heights,
                color='darkcyan', alpha=0.6, edgecolor='black', linewidth=0.3)

        if surface is not None:
            ax.plot_surface(*surface, color='orange', alpha=0.5, edgecolor='none')

        ax.set_title(title)
        ax.set_xlabel(labels[0]); ax.set_ylabel(labels[1]); ax.set_zlabel(labels[2])

        if xticks is not None:
            ax.set_xticks(xticks[0]); ax.set_xticklabels(xticks[1])
        if yticks is not None:
            ax.set_yticks(yticks[0]); ax.set_yticklabels(yticks[1])

        self.canvases_hist3d[chart_number].draw()

    def format_hypothesis_tests(self, hyp):
        alpha = hyp['alpha']
        z_crit = norm.ppf(1 - alpha / 2)
        lines = [
            f"Statistical hypothesis tests (alpha = {alpha})",
            f"Two-sided critical |Z| = {z_crit:.4f}",
            "",
        ]
        for name, stat, p in hyp['tests']:
            verdict = "REJECT Hypothesis" if p < alpha else "ACCEPT Hypothesis"
            lines.append(f"Hypothesis: {name} = theoretical  |  stat = {stat:+.4f}, "
                        f"p = {p:.3f}  ->  {verdict}")
        return "\n".join(lines)

    def handle_task_1(self):
        (X, Y, Z1, Z2, Z3, integral_value, multiplied_sp, f_x_pipe_y_sp, f_y_pipe_x_sp,
        expected_mean, observed_mean, expected_variance, observed_variance,
        expected_r_xy, observed_r_xy, delta_x, delta_y, val_x, val_y,
        x_sample, x_list, y_sample, y_list, f_x, f_y,
        hist3d_data, hyp_tests, irv_bounds, func) = run_task1()

        self.output.setText(
            f"Definite integral value (should be 1 if correct): {integral_value}\n\n"
            f"f(x)*f(y): {multiplied_sp}\n"
            f"f(x | y): {f_x_pipe_y_sp}\n"
            f"f(y | x): {f_y_pipe_x_sp}\n\n"
            f"Expected mean: {expected_mean}\n"
            f"Observed mean: {observed_mean}\n\n"
            f"Expected variance: {expected_variance}\n"
            f"Observed variance: {observed_variance}\n\n"
            f"Expected std: {expected_variance[0]**0.5, expected_variance[1]**0.5}\n"
            f"Observed std: {observed_variance[0]**0.5, observed_variance[1]**0.5}\n\n"
            f"Expected r_xy: {expected_r_xy}\n"
            f"Observed r_xy: {observed_r_xy}\n\n"
            f"CI for mean (x): {observed_mean[0]-delta_x, observed_mean[0]+delta_x}\n"
            f"CI for mean (y): {observed_mean[1]-delta_y, observed_mean[1]+delta_y}\n\n"
            f"CI for variance (x): {val_x}\n"
            f"CI for variance (y): {val_y}\n\n"
            f"{self.format_hypothesis_tests(hyp_tests)}"
        )

        self.hide_canvases()
        self.show_canvases(True, True, False, hist3d=True)

        self.update_wireframe(0, (X, Y, Z1), "Distribution density",  ("X", "Y", "Z"))
        self.update_wireframe(1, (X, Y, Z2), "Distribution function", ("X", "Y", "Z"))
        self.update_wireframe(2, (X, Y, Z3), "f(x, y) - f(x)*f(y)",   ("X", "Y", "Z"))
        self.update_histogram(0, x_sample, x_list, f_x, "Histogram X", ("X", "F"))
        self.update_histogram(1, y_sample, y_list, f_y, "Histogram Y", ("Y", "F"))

        H, xedges, yedges = hist3d_data
        x1, x2, y1, y2 = irv_bounds

        Xp, Yp = np.meshgrid(xedges[:-1], yedges[:-1], indexing='ij')
        dx = xedges[1] - xedges[0]
        dy = yedges[1] - yedges[0]

        gx = np.linspace(x1, x2, 40)
        gy = np.linspace(y1, y2, 40)
        GX, GY = np.meshgrid(gx, gy)
        GZ = func(GX, GY)

        self.update_hist3d(
            0, (Xp.ravel(), Yp.ravel()), H.ravel(), dx, dy,
            title="2D density histogram (3D)",
            labels=("X", "Y", "Density"),
            surface=(GX, GY, GZ),
        )

    def handle_task_2(self):
        (M_x, M_y, D_x, D_y, r_xy, r, X, Y, p_x, p_y, P_indep, p_x_imp, p_y_imp,
        x_l, y_l, M_f, D_f, p_xy_imp, hyp_tests, p_xi, p_yi) = run_task2()

        self.output.setText(
            f"f(x)*f(y): {P_indep}\n"
            f"f(x | y): {p_xi}\n"
            f"f(y | x): {p_yi}\n\n"
            f"Theoretical:\n"
            f"M[x]: {M_x}\nM[y]: {M_y}\nD[x]: {D_x}\nD[y]: {D_y}\nr[xy]: {r_xy}\n\n"
            f"Imperical:\n"
            f"M[x]: {M_f(X, p_x_imp)}\nM[y]: {M_f(Y, p_y_imp)}\n"
            f"D[x]: {D_f(X, p_x_imp)}\nD[y]: {D_f(Y, p_y_imp)}\nr: {r}\n\n"
            f"{self.format_hypothesis_tests(hyp_tests)}"
        )

        self.hide_canvases()
        self.show_canvases(False, True, True, hist3d=True)

        self.update_plot(0, X, p_x, p_x_imp, "X 'Histogram'")
        self.update_plot(1, Y, p_y, p_y_imp, "Y 'Histogram'")
        self.update_histogram(0, x_l, None, None, "Histogram X", ("Value", "Frequency"), bins=20)
        self.update_histogram(1, y_l, None, None, "Histogram Y", ("Value", "Frequency"), bins=20)

        xs = np.arange(len(X))
        ys = np.arange(len(Y))
        Xp, Yp = np.meshgrid(xs, ys, indexing='ij')
        self.update_hist3d(
            0, (Xp.ravel(), Yp.ravel()), np.asarray(p_xy_imp).ravel(), 0.8, 0.8,
            title="2D DSV distribution (3D)",
            labels=("X", "Y", "P"),
            xticks=(xs + 0.4, X),
            yticks=(ys + 0.4, Y),
        )