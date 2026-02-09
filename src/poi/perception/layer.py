import logging
from abc import ABC, abstractmethod
from typing import List
from poi.perception.semantic_model import SemanticEnvironmentModel

logger = logging.getLogger("POI_Perception")

class PerceptionAdapter(ABC):
    """Base class for environment-specific observers (Desktop, Browser, etc.)"""
    @abstractmethod
    def observe(self) -> SemanticEnvironmentModel:
        pass

class PerceptionLayer:
    """
    Orchestrator for environment observation.
    Responsibility:
    1. Manage and poll perception adapters.
    2. Consolidate raw observation data into a unified Semantic Model.
    """
    def __init__(self):
        self.adapters: List[PerceptionAdapter] = []
        self.logger = logging.getLogger("PerceptionLayer")

    def add_adapter(self, adapter: PerceptionAdapter):
        self.adapters.append(adapter)

    def capture_environment(self) -> SemanticEnvironmentModel:
        """Polls all adapters and returns a consolidated view."""
        self.logger.info("CAPTURING_ENVIRONMENT | Starting observation sweep")
        # For Phase 2, we assume a single primary adapter for simplicity
        if not self.adapters:
            self.logger.warning("NO_ADAPTERS | Perception is blind")
            return SemanticEnvironmentModel()
        
        # Consolidation logic (placeholder for multi-adapter merging)
        return self.adapters[0].observe()
