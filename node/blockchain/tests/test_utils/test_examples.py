import os

from node.blockchain.tests.examples import get_example_path, load_example, save_response_as_example


def test_save_and_load():
    file_name = 'testing'
    path = get_example_path(file_name)
    if os.path.exists(path):
        os.remove(path)

    data = {'1': 'one', '2': 'two'}

    @save_response_as_example(file_name)
    def run_any_test():
        return data

    run_any_test()

    assert load_example(file_name) == data

    os.remove(path)
