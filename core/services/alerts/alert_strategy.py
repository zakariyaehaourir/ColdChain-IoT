from abc import ABC, abstractmethod

class AlertStrategy(ABC):
    @abstractmethod
    def sendAlert(self, temperature: float) -> None:
        pass