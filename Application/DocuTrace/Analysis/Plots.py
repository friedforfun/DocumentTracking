from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from graphviz import Digraph, Source
import numpy as np
from decouple import config

from DocuTrace.Utils.Logging import logger, debug

WORK_DIR = config('WORK_DIR')

def get_edges(node_dict):
    """Produces a list of tuples representing the edges described in the node_dict

    Args:
        node_dict (dict(str, list(str))): A dictionary where each key is a node and all the points it connects to are a list of values

    Returns:
        list(str, str): A list of tuples describing the edges between 2 nodes
    """
    edges = []
    for node in node_dict:
        unique = np.unique(node_dict[node])
        node_dict[node] = unique.tolist()
        for neighbour in node_dict[node]:
            edges.append((node[-4:], neighbour[-4:]))
    return edges

class Graphs:
    """Class to produce graphs using graphviz

    Args:
        compute_data (ComputeData): Instance of a ComputeData object
    """
    def __init__(self, compute_data, filename):
        self.compute_data = compute_data
        self.filename = filename


    def save_view_graph(self, graph):
        """Save the graph to the filesystem, used to render a graph on the GUI

        Args:
            graph (graphviz.Digraph): The graph to render and save

        Returns:
            str: The relative path to the saved graph image
        """
        logger.debug('Graph file format: {}'.format(graph.format))
        #path = graph.save(filename=self.filename)
        path = graph.render(filename=self.filename, format=graph.format, cleanup=True, directory=WORK_DIR)
        logger.info('Graph saved at: {}'.format(path))
        return path


    def last_4_chars(self, doc_list):
        """Helper method to truncate a list of strings to only 4 characters

        Args:
            doc_list (list): list of strings to be truncated

        Returns:
            list: list with 4 element string slices
        """
        new_list = []
        for doc in doc_list:
            new_list.append(doc[-4:])
        return new_list

    #@debug
    def also_likes_graph(self, document_id, visitor=None, n=None):
        """Generate the also likes graph

        Args:
            document_id (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.

        Returns:
            graphviz.Digraph: A digraph showing the relationship between the given docuement and other documents by readers
        """
        from DocuTrace.Analysis.ComputeData import top_n_sorted

        _, reader_list = self.compute_data.find_relevant_docs(document_id, visitor)
        reader_list = reader_list.tolist()
        relevant_docs = self.compute_data.also_likes(document_id, visitor, sort_fn=top_n_sorted, n=n)

        logger.debug('Length of relevant docs: {}'.format(len(relevant_docs)))

        self.graph = Digraph(name='Also likes', filename='Also likes', format='png')
        self.graph.attr('graph', ranksep='0.75')

        # Identify connections between nodes and docs
        node_dict = {k: self.compute_data.visitor_documents.get(k, []) for k in reader_list}

        # Remove duplicate entries in node_dict
        for node in node_dict:
            node_dict[node] = np.unique(node_dict[node]).tolist()

        # Get all edges from node_dict
        edges = get_edges(node_dict)


        # Remove edges that point to docs not in relevant docs
        clean_edges = []
        relevant_docs.append(document_id)
        for edge in edges:
            if edge[1] in self.last_4_chars(relevant_docs):
                clean_edges.append(edge)
        edges = clean_edges
        relevant_docs.remove(document_id)

        # Build context subgraph
        with self.graph.subgraph() as context:
            context.attr('node', shape='plaintext', fontsize='16')
            context.edge('Readers', 'Documents')


        # Add reader nodes
        with self.graph.subgraph() as readers:
            readers.attr('node', shape='box', rank='same')
            if visitor is not None:
                readers.node(visitor[-4:], color='.3 .9 .7', style='filled')

            for node in node_dict:
                readers.node(node[-4:])

        
        # Add document nodes
        with self.graph.subgraph() as documents:
            documents.attr('node', shape='circle', rank='same')
            documents.node(document_id[-4:], color='.3 .9 .7', style='filled')

            for doc in relevant_docs:
                if doc != []:
                    documents.node(doc[-4:]) 

        # Make an edge between the visitor and the document
        if visitor is not None:
            self.graph.edge(visitor[-4:], document_id[-4:])
            
        # Add all remaining edges
        for edge in edges:
            self.graph.edge(*edge)

        return self.graph

class Charts:
    """Class with functions to aid plotting charts

        Args:
            n_rows (int, optional): Number of rows in the figure. Defaults to 1.
            n_cols (int, optional): Number of columns in the figure. Defaults to 1.
            figsize (tuple, optional): The size of the figure being plotted. Defaults to (15, 10).
            bar_gap (int, optional): The space between the bars. Defaults to 1.
            x_tick_rotation (int, optional): The rotation of the x_tick labels. Defaults to 45.
        """
    def __init__(self, n_rows=1, n_cols=1, figsize=(15, 10), bar_gap=1, x_tick_rotation=45, **kwargs):
        #super().__init__(self, figsize=figsize, dpi=100)
        self.fig, self.axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=figsize, **kwargs)
        if hasattr(self.axes, 'ravel'):
            self.ax = self.axes.ravel()
        else:
            self.ax = [self.axes]
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
            data (list(dict)): A list of dictionaries.
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

        #self.fig.tight_layout()
        return self.fig

