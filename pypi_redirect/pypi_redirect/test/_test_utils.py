import os


def read_index(filename):
    index_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'resources', filename)

    with open(index_path) as f:
        return f.read()
