from abc import ABC, abstractmethod
from typing import List

class OperatorEmailProvider(ABC):
    """Interface for retrieving operator email addresses."""
    
    @abstractmethod
    def get_operator_emails(self) -> List[str]:
        pass

class MockOperatorEmailProvider(OperatorEmailProvider):
    """Temporary mock implementation until the operator system is ready."""
    
    def get_operator_emails(self) -> List[str]:
        return ["mbch33255@gmail.com", "chwayhaourir@gmail.com"]