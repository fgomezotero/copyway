from abc import ABC, abstractmethod


class Protocol(ABC):
    def __init__(self, config=None):
        self.config = config or {}

    @abstractmethod
    def copy(self, source, destination, **options):
        pass

    @abstractmethod
    def validate(self, source, destination):
        pass
