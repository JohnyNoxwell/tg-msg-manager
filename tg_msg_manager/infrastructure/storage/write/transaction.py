from contextlib import contextmanager


class StorageTransactionCoordinator:
    def __init__(self, *, connection, lock):
        self.connection = connection
        self.lock = lock

    @contextmanager
    def write_transaction(self):
        with self.lock:
            with self.connection:
                yield self.connection
