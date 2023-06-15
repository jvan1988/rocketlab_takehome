class Plotter:
    def __init__(self, figure, canvas):
        self.figure = figure
        self.canvas = canvas
        self.x_data = []
        self.y_data = []
        self.z_data = []

    def plot_data(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(self.x_data, self.y_data, label='MV')
        ax.plot(self.x_data, self.z_data, label='MA', linestyle='dashed')

        ax.legend()

        ax.set_xlabel('Time(seconds)')

        self.canvas.draw()

    def update_data(self, x, y, z):
        self.x_data.append(x)
        self.y_data.append(y)
        self.z_data.append(z)
        self.plot_data()

    def clear_data(self):
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.plot_data()
