"""
NEXUS Evidence & Verification Tools
Preserves strict factual integrity by tracking verbatim citations, file origins,
and enforcing clear labels: Documented Fact vs AI-Generated Suggestion.
"""

from typing import Dict, List, Any, Optional
from core.models import EvidenceCitation


class EvidenceStore:
    """In-memory verifiable fact registry maintaining source coordinates."""
    
    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.facts: List[Dict[str, Any]] = []
        
    def add_document(self, file_name: str, file_type: str, content: str, sections: Optional[List[Dict[str, Any]]] = None):
        self.documents[file_name] = {
            "file_name": file_name,
            "file_type": file_type,
            "content": content,
            "sections": sections or []
        }
        
    def add_fact(self, entity_or_relation: str, fact: str, source_file: str, section: str = "General", confidence: float = 1.0):
        self.facts.append({
            "subject": entity_or_relation,
            "fact": fact,
            "source_file": source_file,
            "section": section,
            "confidence": confidence
        })
        
    def find_evidence_for_entity(self, entity_name: str) -> List[EvidenceCitation]:
        citations = []
        lower_name = entity_name.lower()
        
        # 1. Search indexed facts
        for f in self.facts:
            if lower_name in f["subject"].lower() or lower_name in f["fact"].lower():
                citations.append(EvidenceCitation(
                    source_file=f["source_file"],
                    section=f.get("section", "General"),
                    exact_fact=f["fact"],
                    confidence=f.get("confidence", 1.0)
                ))
                
        # 2. Search document text snippets if fewer than 2 citations
        if len(citations) < 2:
            for fname, doc in self.documents.items():
                content = doc.get("content", "")
                if lower_name in content.lower():
                    # Extract 1-2 sentence window
                    lines = content.splitlines()
                    for line in lines:
                        if lower_name in line.lower() and len(line.strip()) > 15:
                            citations.append(EvidenceCitation(
                                source_file=fname,
                                section="Body Excerpt",
                                exact_fact=line.strip(),
                                confidence=0.9
                            ))
                            if len(citations) >= 3:
                                break
                                
        return citations[:4]


def format_fact_tag(fact_type: str) -> str:
    """Returns standardized UI badge/tag text for strict factual integrity."""
    if fact_type.upper() == "DOCUMENTED_FACT":
        return "📘 DOCUMENTED FACT"
    elif fact_type.upper() == "AI_EXPLANATION":
        return "🤖 AI-GENERATED EXPLANATION"
    elif fact_type.upper() == "AI_SUGGESTION":
        return "💡 AI-GENERATED SUGGESTION"
    return "ℹ️ SYSTEM FACT"


def get_alternative_status_message(has_backup: bool, backup_name: Optional[str] = None, source_doc: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns strict evidence-backed recovery message.
    Enforces rule: 'No documented alternative was found in the provided data.'
    """
    if has_backup and backup_name:
        return {
            "has_alternative": True,
            "message": f"Documented Alternative: {backup_name}",
            "evidence": f"Found in {source_doc or 'Suppliers / Contracts'}",
            "is_documented": True
        }
    else:
        return {
            "has_alternative": False,
            "message": "No documented alternative was found in the provided data.",
            "evidence": "Comprehensive scan of uploaded contracts, spreadsheets, and SOPs.",
            "is_documented": True
        }
