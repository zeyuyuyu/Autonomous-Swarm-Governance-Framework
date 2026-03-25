#!/usr/bin/env python3

from typing import Dict, List, Tuple, Optional
import difflib
import json

class DiffAnalyzer:
    def __init__(self):
        self.conflict_strategies = {
            'merge': self._merge_changes,
            'latest_wins': self._take_latest,
            'consensus': self._reach_consensus
        }

    def analyze_diffs(self, original: str, variants: List[str]) -> Tuple[str, Dict]:
        """Analyze differences between original and multiple variant versions"""
        diffs = []
        conflict_zones = []

        for variant in variants:
            diff = list(difflib.ndiff(original.splitlines(), variant.splitlines()))
            diffs.append(diff)
            
            # Identify conflict zones
            conflicts = self._find_conflicts(diff)
            if conflicts:
                conflict_zones.extend(conflicts)

        # Generate analysis report
        report = {
            'num_variants': len(variants),
            'conflict_zones': conflict_zones,
            'similarity_scores': self._calculate_similarities(original, variants),
            'recommended_strategy': self._suggest_strategy(conflict_zones)
        }

        # Apply recommended resolution strategy
        resolved = self._resolve_conflicts(original, variants, report['recommended_strategy'])

        return resolved, report

    def _find_conflicts(self, diff: List[str]) -> List[Dict]:
        """Identify zones of conflict in diff"""
        conflicts = []
        current_conflict = None
        
        for i, line in enumerate(diff):
            if line.startswith('- ') and i < len(diff)-1 and diff[i+1].startswith('+ '):
                if not current_conflict:
                    current_conflict = {
                        'start_line': i,
                        'changes': []
                    }
                current_conflict['changes'].append({
                    'removed': line[2:],
                    'added': diff[i+1][2:]
                })
            elif current_conflict and not line.startswith('?'):
                current_conflict['end_line'] = i
                conflicts.append(current_conflict)
                current_conflict = None
                
        return conflicts

    def _calculate_similarities(self, original: str, variants: List[str]) -> List[float]:
        """Calculate similarity scores between original and variants"""
        scores = []
        for variant in variants:
            matcher = difflib.SequenceMatcher(None, original, variant)
            scores.append(round(matcher.ratio(), 3))
        return scores

    def _suggest_strategy(self, conflict_zones: List[Dict]) -> str:
        """Suggest conflict resolution strategy based on analysis"""
        if not conflict_zones:
            return 'merge'
        elif len(conflict_zones) > 5:
            return 'consensus'
        else:
            return 'latest_wins'

    def _resolve_conflicts(self, original: str, variants: List[str], strategy: str) -> str:
        """Apply selected conflict resolution strategy"""
        resolver = self.conflict_strategies.get(strategy, self._merge_changes)
        return resolver(original, variants)

    def _merge_changes(self, original: str, variants: List[str]) -> str:
        """Merge non-conflicting changes"""
        result = original
        for variant in variants:
            d = difflib.unified_diff(result.splitlines(), variant.splitlines())
            # Apply non-conflicting changes
            for line in d:
                if line.startswith('+') and not any(l.startswith('-') for l in d):
                    result += line[1:] + '\
'
        return result

    def _take_latest(self, original: str, variants: List[str]) -> str:
        """Take the latest version in conflicts"""
        return variants[-1]

    def _reach_consensus(self, original: str, variants: List[str]) -> str:
        """Use most common version in conflicts"""
        from collections import Counter
        versions = [original] + variants
        count = Counter(versions)
        return count.most_common(1)[0][0]

    def export_report(self, report: Dict, filepath: str) -> None:
        """Export analysis report to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
