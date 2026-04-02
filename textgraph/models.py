from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class SyntaxComparison:
    token: str
    original_role: str
    edited_role: Optional[str]
    is_preserved: bool


@dataclass
class EvolutionFrame:
    frame_number: int
    timestamp: str
    description: str
    nodes: Set[str]
    edges: Set[Tuple[str, str]]
    statistics: Dict[str, int]


@dataclass
class AnalysisArtifacts:
    folder: str
    original_tokens: List[str]
    edited_tokens: List[str]
    frames: List[EvolutionFrame]
