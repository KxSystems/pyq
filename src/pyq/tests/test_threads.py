import threading
from pyq import _k


def test_m9_in_thread():
    def call_m9():
        _k.m9()

    thread = threading.Thread(target=call_m9)
    thread.start()
    thread.join()
