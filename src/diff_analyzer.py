import re
from typing import Dict, List, Tuple

class DiffAnalyzer:
    def __init__(self):
        self.high_risk_patterns = [
            r'password',
            r'secret',
            r'token',
            r'api[_]?key',
            r'credential',
            r'auth',
        ]
        
        self.critical_file_patterns = [
            r'.*dockerfile.*',
            r'.*\.env.*',
            r'.*/config/.*',
            r'.*/settings/.*',
            r'.*security.*',
            r'.*auth.*'
        ]

    def calculate_impact_score(self, diff_text: str, filepath: str) -> Tuple[float, List[str]]:
        """
        Analyzes a diff and returns an impact score (0-10) and list of concerns
        """
        score = 0.0
        concerns = []

        # Check for critical file patterns
        for pattern in self.critical_file_patterns:
            if re.match(pattern, filepath.lower()):
                score += 2.0
                concerns.append(f'Critical file pattern match: {pattern}')
                break

        # Analyze diff content
        lines = diff_text.split('\
')
        added_lines = [line[1:] for line in lines if line.startswith('+')]
        removed_lines = [line[1:] for line in lines if line.startswith('-')]

        # Check for sensitive patterns in added/removed lines
        for pattern in self.high_risk_patterns:
            for line in added_lines:
                if re.search(pattern, line.lower()):
                    score += 3.0
                    concerns.append(f'Added sensitive pattern: {pattern}')
            for line in removed_lines:
                if re.search(pattern, line.lower()):
                    score += 2.0
                    concerns.append(f'Removed sensitive pattern: {pattern}')

        # Calculate complexity impact
        complexity_score = min(3.0, (len(added_lines) + len(removed_lines)) / 50.0)
        score += complexity_score
        
        if complexity_score > 1.5:
            concerns.append('High complexity changes detected')

        # Cap final score at 10
        score = min(10.0, score)
        
        return score, concerns

    def highlight_critical_diffs(self, diff_text: str) -> Dict[int, str]:
        """
        Returns a mapping of line numbers to highlighted concerns in the diff
        """
        highlights = {}
        lines = diff_text.split('\
')
        
        for idx, line in enumerate(lines, 1):
            if not line.startswith(('+', '-')):
                continue
                
            content = line[1:]
            matches = []
            
            # Check for sensitive patterns
            for pattern in self.high_risk_patterns:
                if re.search(pattern, content.lower()):
                    matches.append(f'Contains sensitive pattern: {pattern}')
            
            # Check for potentially dangerous code patterns
            if re.search(r'exec\\s*\\(', content):
                matches.append('Contains code execution')
            if re.search(r'eval\\s*\\(', content):
                matches.append('Contains eval statement')
            if re.search(r'subprocess', content):
                matches.append('Contains subprocess usage')
            
            if matches:
                highlights[idx] = ' | '.join(matches)
        
        return highlights

    def analyze_diff(self, diff_text: str, filepath: str) -> Dict:
        """
        Performs comprehensive diff analysis and returns results
        """
        impact_score, concerns = self.calculate_impact_score(diff_text, filepath)
        highlights = self.highlight_critical_diffs(diff_text)
        
        return {
            'impact_score': impact_score,
            'risk_level': 'HIGH' if impact_score >= 7 else 'MEDIUM' if impact_score >= 4 else 'LOW',
            'concerns': concerns,
            'highlights': highlights
        }