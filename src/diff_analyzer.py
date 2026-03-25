"""Analyzes code diffs to determine impact and risk of changes."""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re

@dataclass
class DiffMetrics:
    lines_added: int
    lines_removed: int 
    files_changed: int
    risk_score: float
    impacted_components: List[str]

class DiffAnalyzer:
    def __init__(self):
        self.high_risk_patterns = [
            r'(?i)security',
            r'(?i)authentication', 
            r'(?i)authorization',
            r'(?i)crypto',
            r'(?i)password'
        ]

        self.core_components = [
            'governance',
            'consensus',
            'networking',
            'storage'
        ]

    def analyze_diff(self, diff_content: str) -> DiffMetrics:
        """Analyzes a git diff and returns key metrics about the changes."""
        lines_added = len(re.findall(r'\
\\+[^+]', diff_content))
        lines_removed = len(re.findall(r'\
-[^-]', diff_content))
        files = set(re.findall(r'diff --git a/(.*?) b/', diff_content))

        # Calculate risk score
        risk_score = self._calculate_risk_score(diff_content)
        
        # Identify impacted components
        impacted = self._identify_impacted_components(diff_content)

        return DiffMetrics(
            lines_added=lines_added,
            lines_removed=lines_removed,
            files_changed=len(files),
            risk_score=risk_score,
            impacted_components=impacted
        )

    def _calculate_risk_score(self, content: str) -> float:
        """Calculate a risk score from 0-1 based on various factors."""
        score = 0.0
        
        # Check for high risk patterns
        for pattern in self.high_risk_patterns:
            if re.search(pattern, content):
                score += 0.2 # Each risk pattern adds 0.2
                
        # Factor in size of change
        lines_changed = len(re.findall(r'\
[+-][^+-]', content))
        if lines_changed > 500:
            score += 0.3
        elif lines_changed > 100:
            score += 0.1
            
        # Cap at 1.0
        return min(1.0, score)

    def _identify_impacted_components(self, content: str) -> List[str]:
        """Identifies which core components are impacted by changes."""
        impacted = []
        for component in self.core_components:
            if re.search(f'(?i){component}', content):
                impacted.append(component)
        return impacted

    def get_review_recommendation(self, metrics: DiffMetrics) -> str:
        """Provides a review recommendation based on diff metrics."""
        if metrics.risk_score >= 0.7:
            return 'HIGH_RISK: Requires senior review and security audit'
        elif metrics.risk_score >= 0.4:
            return 'MEDIUM_RISK: Requires standard peer review'
        else:
            return 'LOW_RISK: Standard review process'

    def generate_impact_report(self, metrics: DiffMetrics) -> Dict:
        """Generates a detailed impact report from the metrics."""
        return {
            'summary': {
                'files_changed': metrics.files_changed,
                'total_lines_changed': metrics.lines_added + metrics.lines_removed,
                'risk_level': self.get_review_recommendation(metrics)
            },
            'risk_analysis': {
                'risk_score': metrics.risk_score,
                'impacted_components': metrics.impacted_components
            },
            'change_magnitude': {
                'lines_added': metrics.lines_added,
                'lines_removed': metrics.lines_removed
            }
        }
