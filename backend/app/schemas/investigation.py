from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class InvestigationStep(BaseModel):
    step_number: int
    title: str
    description: str
    status: str  # "completed", "in_progress", "pending"
    count: Optional[int] = None

class InvestigationOverviewResponse(BaseModel):
    case_id: int
    steps: List[InvestigationStep]

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}

class GraphLink(BaseModel):
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = {}

class GraphDataResponse(BaseModel):
    case_id: int
    nodes: List[GraphNode]
    links: List[GraphLink]
    total_nodes: int
    total_links: int
