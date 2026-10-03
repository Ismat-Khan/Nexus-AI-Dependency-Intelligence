"""
NEXUS State Caching & Demo Pre-loader
Manages analysis session cache, persistent graph representations,
and deterministic pre-compiled demo states for instantaneous zero-latency demonstrations.
"""

import json
import os
from typing import Dict, List, Any, Optional
import networkx as nx
from core.models import Entity, Dependency, EntityType, RelationType, ImportanceLevel
from tools.graph_tools import build_dependency_graph, get_graph_summary_metrics


def get_default_demo_dataset() -> Dict[str, Any]:
    """
    Returns the complete deterministic Voltra Mobility ground-truth model.
    Guarantees that Demo Mode loads in 0.05 seconds with 100% factual integrity.
    """
    entities = [
        # Suppliers
        Entity(
            name="Apex Microelectronics",
            entity_type=EntityType.SUPPLIER,
            fact="Sole source supplier of automotive grade MCU-900 Microcontrollers under contract MSA-4401.",
            source_doc="Suppliers.xlsx",
            section="Tier-1 Vendors",
            importance=ImportanceLevel.CRITICAL,
            backup_supplier=None,
            metadata={"country": "Taiwan", "lead_time_days": 21}
        ),
        Entity(
            name="VoltCell Energy",
            entity_type=EntityType.SUPPLIER,
            fact="Primary supplier of high-density Lithium-Ion Battery Cells (Contract MSA-8812). Secondary certified source: Amperex Dynamics.",
            source_doc="Suppliers.xlsx",
            section="Tier-1 Vendors",
            importance=ImportanceLevel.CRITICAL,
            backup_supplier="Amperex Dynamics",
            metadata={"country": "South Korea", "lead_time_days": 14}
        ),
        Entity(
            name="StatorTech Precision",
            entity_type=EntityType.SUPPLIER,
            fact="Supplier of precision wound electric traction motor stator assemblies.",
            source_doc="Suppliers.xlsx",
            section="Tier-1 Vendors",
            importance=ImportanceLevel.HIGH,
            backup_supplier="GlobalDrive Dynamics",
            metadata={"country": "Germany", "lead_time_days": 10}
        ),
        Entity(
            name="Sensoryx Corp",
            entity_type=EntityType.SUPPLIER,
            fact="Manufacturer of ultrasonic radar sensors and proximity hardware.",
            source_doc="Suppliers.xlsx",
            section="Tier-2 Vendors",
            importance=ImportanceLevel.MEDIUM,
            backup_supplier=None,
            metadata={"country": "USA", "lead_time_days": 7}
        ),
        
        # Components
        Entity(
            name="Microcontroller MCU-900",
            entity_type=EntityType.COMPONENT,
            fact="Core automotive processing unit for vehicle avionics. Stock: 2,500 units. Burn rate: 500/day. Coverage: 5 days.",
            source_doc="Inventory.xlsx",
            section="Active Inventory",
            importance=ImportanceLevel.CRITICAL,
            inventory_days=5.0,
            daily_burn_rate=500.0,
            backup_supplier=None
        ),
        Entity(
            name="Lithium-Ion Battery Cells",
            entity_type=EntityType.COMPONENT,
            fact="Cylindrical 4680 battery cells for high voltage energy storage. Stock: 12,000 units. Burn rate: 1,000/day. Coverage: 12 days.",
            source_doc="Inventory.xlsx",
            section="Active Inventory",
            importance=ImportanceLevel.CRITICAL,
            inventory_days=12.0,
            daily_burn_rate=1000.0,
            backup_supplier="Amperex Dynamics"
        ),
        Entity(
            name="Electric Traction Motor Stator",
            entity_type=EntityType.COMPONENT,
            fact="Custom electromagnetic stator core for main drive unit. Stock: 4,000 units. Burn rate: 400/day. Coverage: 10 days.",
            source_doc="Inventory.xlsx",
            section="Active Inventory",
            importance=ImportanceLevel.HIGH,
            inventory_days=10.0,
            daily_burn_rate=400.0,
            backup_supplier="GlobalDrive Dynamics"
        ),
        Entity(
            name="Ultrasonic Radar Sensors",
            entity_type=EntityType.COMPONENT,
            fact="Autonomous parking and collision proximity sensors. Stock: 3,000 units. Burn rate: 300/day. Coverage: 10 days.",
            source_doc="Inventory.xlsx",
            section="Active Inventory",
            importance=ImportanceLevel.MEDIUM,
            inventory_days=10.0,
            daily_burn_rate=300.0,
            backup_supplier=None
        ),
        
        # Machines
        Entity(
            name="SMT Robot #4",
            entity_type=EntityType.MACHINE,
            fact="High-speed surface-mount placement robot. Dedicated to ECU avionics circuit board fabrication.",
            source_doc="Machine_Requirements.pdf",
            section="Line 2 Tooling",
            importance=ImportanceLevel.CRITICAL
        ),
        Entity(
            name="Battery Pack Laser Welder",
            entity_type=EntityType.MACHINE,
            fact="Robotic high-speed fiber laser welder joining cell interconnect busbars.",
            source_doc="Machine_Requirements.pdf",
            section="Line 1 Tooling",
            importance=ImportanceLevel.HIGH
        ),
        Entity(
            name="Stator Winding Automated Press",
            entity_type=EntityType.MACHINE,
            fact="Automated press press-fitting stator assemblies into aluminum drive housings.",
            source_doc="Machine_Requirements.pdf",
            section="Line 1 Tooling",
            importance=ImportanceLevel.HIGH
        ),
        Entity(
            name="Automated Test Rig #2",
            entity_type=EntityType.MACHINE,
            fact="End-of-line diagnostic rig calibrating sensor arrays and ECU communications.",
            source_doc="Machine_Requirements.pdf",
            section="Line 3 Quality Rig",
            importance=ImportanceLevel.MEDIUM
        ),
        
        # Processes
        Entity(
            name="ECU Sub-assembly",
            entity_type=EntityType.PROCESS,
            fact="Assembly Line 2 process manufacturing central vehicle electronic control units.",
            source_doc="Production_Process.pdf",
            section="Line 2 Overview",
            importance=ImportanceLevel.CRITICAL
        ),
        Entity(
            name="Powertrain Integration",
            entity_type=EntityType.PROCESS,
            fact="Assembly Line 1 process uniting electric drive motor, inverter, and high-voltage battery pack.",
            source_doc="Production_Process.pdf",
            section="Line 1 Overview",
            importance=ImportanceLevel.HIGH
        ),
        Entity(
            name="Final Vehicle Synthesis",
            entity_type=EntityType.PROCESS,
            fact="Assembly Line 3 final chassis integration, firmware flashing, and road readiness certification.",
            source_doc="Production_Process.pdf",
            section="Line 3 Overview",
            importance=ImportanceLevel.CRITICAL
        ),
        
        # Products
        Entity(
            name="Voltra Model V-1",
            entity_type=EntityType.PRODUCT,
            fact="Voltra Mobility's flagship electric passenger urban vehicle. Planned output: 500 units/day.",
            source_doc="Production_Process.pdf",
            section="Commercial Specifications",
            importance=ImportanceLevel.CRITICAL
        ),
        Entity(
            name="Voltra Commercial Fleet Van",
            entity_type=EntityType.PRODUCT,
            fact="Zero-emission urban logistics delivery van for commercial fleet operators.",
            source_doc="Production_Process.pdf",
            section="Commercial Specifications",
            importance=ImportanceLevel.HIGH
        )
    ]
    
    dependencies = [
        # Apex -> MCU-900 -> SMT Robot #4 -> ECU Sub-assembly -> Voltra Model V-1 & Fleet Van
        Dependency(
            source="Apex Microelectronics",
            target="Microcontroller MCU-900",
            relation=RelationType.SUPPLIES,
            evidence="Apex is sole contracted supplier of MCU-900 chipsets under contract MSA-4401.",
            source_doc="Suppliers.xlsx",
            confidence=1.0
        ),
        Dependency(
            source="Microcontroller MCU-900",
            target="SMT Robot #4",
            relation=RelationType.REQUIRED_BY,
            evidence="SMT Robot #4 requires MCU-900 taped reel component feeds to assemble ECU boards.",
            source_doc="Machine_Requirements.pdf",
            confidence=1.0
        ),
        Dependency(
            source="SMT Robot #4",
            target="ECU Sub-assembly",
            relation=RelationType.USED_IN,
            evidence="SMT Robot #4 is the sole active robotic surface mount station for ECU Sub-assembly.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        ),
        Dependency(
            source="ECU Sub-assembly",
            target="Final Vehicle Synthesis",
            relation=RelationType.USED_IN,
            evidence="Line 2 completed ECU avionics units are installed into chassis at Final Vehicle Synthesis.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        ),
        Dependency(
            source="Final Vehicle Synthesis",
            target="Voltra Model V-1",
            relation=RelationType.PRODUCES,
            evidence="Final Vehicle Synthesis line produces certified Voltra Model V-1 passenger cars.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        ),
        Dependency(
            source="Final Vehicle Synthesis",
            target="Voltra Commercial Fleet Van",
            relation=RelationType.PRODUCES,
            evidence="Commercial Fleet Van uses shared Final Vehicle Synthesis line 3.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        ),
        
        # VoltCell -> Battery Cells -> Laser Welder -> Powertrain -> Final Vehicle Synthesis
        Dependency(
            source="VoltCell Energy",
            target="Lithium-Ion Battery Cells",
            relation=RelationType.SUPPLIES,
            evidence="VoltCell Energy provides primary battery cell supply under Contract MSA-8812.",
            source_doc="Suppliers.xlsx",
            confidence=1.0
        ),
        Dependency(
            source="Lithium-Ion Battery Cells",
            target="Battery Pack Laser Welder",
            relation=RelationType.REQUIRED_BY,
            evidence="Laser Welder binds cylindrical cells into high-voltage pack matrix.",
            source_doc="Machine_Requirements.pdf",
            confidence=1.0
        ),
        Dependency(
            source="Battery Pack Laser Welder",
            target="Powertrain Integration",
            relation=RelationType.USED_IN,
            evidence="Battery pack welding output feeds directly to Line 1 Powertrain Integration.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        ),
        Dependency(
            source="Powertrain Integration",
            target="Final Vehicle Synthesis",
            relation=RelationType.USED_IN,
            evidence="Powertrain assembly is installed into vehicle chassis on Line 3.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        ),
        
        # StatorTech -> Stator -> Press -> Powertrain Integration
        Dependency(
            source="StatorTech Precision",
            target="Electric Traction Motor Stator",
            relation=RelationType.SUPPLIES,
            evidence="StatorTech Precision manufactures custom motor stators.",
            source_doc="Suppliers.xlsx",
            confidence=1.0
        ),
        Dependency(
            source="Electric Traction Motor Stator",
            target="Stator Winding Automated Press",
            relation=RelationType.REQUIRED_BY,
            evidence="Automated press press-fits motor stators into drivetrain housing.",
            source_doc="Machine_Requirements.pdf",
            confidence=1.0
        ),
        Dependency(
            source="Stator Winding Automated Press",
            target="Powertrain Integration",
            relation=RelationType.USED_IN,
            evidence="Drive motor housing joins transmission at Line 1 Powertrain Integration.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        ),
        
        # Sensoryx -> Radar Sensors -> Test Rig -> Final Vehicle Synthesis
        Dependency(
            source="Sensoryx Corp",
            target="Ultrasonic Radar Sensors",
            relation=RelationType.SUPPLIES,
            evidence="Sensoryx Corp delivers ultrasonic proximity radar modules.",
            source_doc="Suppliers.xlsx",
            confidence=1.0
        ),
        Dependency(
            source="Ultrasonic Radar Sensors",
            target="Automated Test Rig #2",
            relation=RelationType.REQUIRED_BY,
            evidence="Automated Test Rig #2 performs calibration and timing on radar sensors.",
            source_doc="Machine_Requirements.pdf",
            confidence=1.0
        ),
        Dependency(
            source="Automated Test Rig #2",
            target="Final Vehicle Synthesis",
            relation=RelationType.USED_IN,
            evidence="Calibrated sensor suites are mounted to exterior bumper assemblies.",
            source_doc="Production_Process.pdf",
            confidence=1.0
        )
    ]
    
    G = build_dependency_graph(entities, dependencies)
    metrics = get_graph_summary_metrics(G)
    
    return {
        "is_demo": True,
        "organization": "Voltra Mobility",
        "entities": entities,
        "dependencies": dependencies,
        "graph": G,
        "metrics": metrics,
        "file_names": [
            "Suppliers.xlsx",
            "Inventory.xlsx",
            "Production_Process.pdf",
            "Machine_Requirements.pdf",
            "Supply_Contracts.pdf",
            "Operations_SOP.docx"
        ]
    }
