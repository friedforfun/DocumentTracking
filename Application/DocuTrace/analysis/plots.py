from matplotlib import pyplot as plt
import numpy as np


class Plots:
    """Class with functions to aid plotting charts

        Args:
            n_rows (int, optional): Number of rows in the figure. Defaults to 1.
            n_cols (int, optional): Number of columns in the figure. Defaults to 1.
            figsize (tuple, optional): The size of the figure being plotted. Defaults to (15, 10).
            bar_gap (int, optional): The space between the bars. Defaults to 1.
            x_tick_rotation (int, optional): The rotation of the x_tick labels. Defaults to 45.
        """
    def __init__(self, n_rows=1, n_cols=1, figsize=(15, 10), bar_gap=1, x_tick_rotation=45, **kwargs):
        self.fig, self.axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=figsize, **kwargs)
        self.ax = self.axes.ravel()
        self.bar_gap = bar_gap
        self.x_tick_rotation = x_tick_rotation

    def ax_bar_from_dict(self, ax, data_dict, title=None, y_label=None, x_label=None):
        """Create a matplotlib ax from a dictionary

        Args:
            ax (matplotlib.pyplot.Axes): The axes to plot on.
            data_dict (dict): A dictionary of integers.
            title (str, optional): Title for the ax. Defaults to None.
            y_label (str, optional): y-axis label. Defaults to None.
            x_label (str, optional): x-axis label. Defaults to None.

        Returns:
            matplotlib.pyplot.Axes: The axes with bar plotted on it.
        """
        x_pos = np.arange(0, self.bar_gap*len(data_dict), self.bar_gap)
        ax.bar(x_pos, data_dict.values())
        ax.set_xticks(x_pos)
        ax.set_xticklabels(data_dict.keys(), rotation=self.x_tick_rotation)
        if title is not None:
            ax.set_title(title)
        if y_label is not None:
            ax.set_ylabel(y_label)
        if x_label is not None:
            ax.set_xlabel(x_label)
        return ax

    def histogram(self, data, titles=None, y_labels=None, x_labels=None):
        """Create a histogram plot using a list of dictionaries

        Args:
            data (list(dict)): A list of dictionaries
            titles (list(str)), optional): A list of titles. Defaults to None.
            y_labels (list(str)), optional): A list of y axis labels. Defaults to None.
            x_labels (list(str)), optional): A list of x axis labels. Defaults to None.

        Raises:
            ValueError: When the lists dont have a consistent length
        """
        if titles is None:
            titles = ['' for _ in range(len(data))]
        if y_labels is None:
            y_labels = ['' for _ in range(len(data))]
        if x_labels is None:
            x_labels = ['' for _ in range(len(data))]


        if not all(len(l) == len(data) for l in iter([titles, y_labels, x_labels])):
            raise ValueError('Label lists must all be the same length')

        for i, data_dict in enumerate(data):
            self.ax[i] = self.ax_bar_from_dict(self.ax[i], data_dict, titles[i], y_labels[i], x_labels[i])

        self.fig.tight_layout()
        plt.show()


