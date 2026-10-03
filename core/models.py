"""
NEXUS Core Data Models
Structured data schemas for entities, dependencies, failure scenarios, and impact results.
Enforces deterministic factual integrity throughout the multi-agent pipeline.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    SUPPLIER = "supplier"
    COMPONENT = "component"
    MACHINE = "machine"
    PROCESS = "process"
    PRODUCT = "product"
    SYSTEM = "system"
    SERVICE = "service"


class RelationType(str, Enum):
    SUPPLIES = "supplies"
    REQUIRED_BY = "required_by"
    USED_IN = "used_in"
    PRODUCES = "produces"
    DEPENDS_ON = "depends_on"
    BACKS_UP = "backs_up"
    CONNECTS_TO = "connects_to"


class ImportanceLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceCitation(BaseModel):
    source_file: str
    section: Optional[str] = "General"
    row_or_page: Optional[str] = None
    exact_fact: str
    confidence: float = 1.0


class Entity(BaseModel):
    name: str
    entity_type: EntityType
    fact: str
    source_doc: str
    section: Optional[str] = "General"
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    inventory_days: Optional[float] = None
    daily_burn_rate: Optional[float] = None
    backup_supplier: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Dependency(BaseModel):
    source: str
    target: str
    relation: RelationType = RelationType.DEPENDS_ON
    evidence: str
    source_doc: str
    confidence: float = 1.0


class FailureScenario(BaseModel):
    target_node: str
    outage_duration_days: float = 7.0
    scenario_type: str = "supplier_outage"
    raw_query: str = ""


class TimeBufferComparison(BaseModel):
    duration_days: float
    coverage_days: float
    gap_days: float
    status: str
    production_impact: str


class ImpactResult(BaseModel):
    failed_node: str
    outage_duration_days: float
    direct_impact: List[str] = Field(default_factory=list)
    indirect_impact: List[str] = Field(default_factory=list)
    all_affected_nodes: List[str] = Field(default_factory=list)
    terminal_products: List[str] = Field(default_factory=list)
    impact_chains: List[List[str]] = Field(default_factory=list)
    
    # Deterministic inventory metrics
    inventory_coverage_days: float = 0.0
    inventory_gap_days: float = 0.0
    daily_burn_rate: float = 0.0
    buffer_status: str = "Unknown"
    multi_day_comparison: List[TimeBufferComparison] = Field(default_factory=list)
    
    # Risk attributes
    is_single_point_of_failure: bool = False
    has_documented_backup: bool = False
    documented_backup_name: Optional[str] = None
    backup_sla_days: Optional[float] = None
    
    # Supporting Evidence
    evidence_citations: List[EvidenceCitation] = Field(default_factory=list)


class RiskAnalysis(BaseModel):
    critical_dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    single_points_of_failure: List[str] = Field(default_factory=list)
    bottlenecks: List[str] = Field(default_factory=list)
    overall_risk_score: int = 0  # 0-100
    risk_level: str = "MODERATE"
    spof_count: int = 0
    total_nodes: int = 0
    total_edges: int = 0


class RecoveryPlan(BaseModel):
    documented_options: List[Dict[str, Any]] = Field(default_factory=list)
    inventory_buffer_advice: Dict[str, Any] = Field(default_factory=dict)
    no_documented_alternative_found: bool = False
    ai_generated_suggestions: List[str] = Field(default_factory=list)
    raw_summary: str = ""


class AgentStatusRecord(BaseModel):
    name: str
    display_title: str
    status: str = "waiting"  # "waiting", "running", "completed", "error"
    detail: str = "Standing by"
    elapsed_time: float = 0.0
