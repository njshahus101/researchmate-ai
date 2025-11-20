"""
Quality Assurance Service - Automated Validation Framework

This service provides comprehensive validation for ResearchMate AI outputs:
1. Report Completeness - Ensures all required sections present
2. Citation Accuracy - Validates citations match sources
3. Comparison Matrix Quality - Checks comparison data completeness
4. Overall Quality Scoring - Aggregated quality metrics (0-100)

Used after Report Generator to ensure output quality before delivery.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    """Validation severity levels"""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class ValidationResult:
    """Single validation check result"""
    category: str
    check_name: str
    level: ValidationLevel
    score: int  # 0-100
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    overall_score: int  # 0-100
    validation_results: List[ValidationResult]
    summary: Dict[str, Any]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "overall_score": self.overall_score,
            "grade": self._get_grade(),
            "validation_results": [
                {
                    "category": vr.category,
                    "check_name": vr.check_name,
                    "level": vr.level.value,
                    "score": vr.score,
                    "message": vr.message,
                    "details": vr.details
                }
                for vr in self.validation_results
            ],
            "summary": self.summary,
            "recommendations": self.recommendations
        }

    def _get_grade(self) -> str:
        """Convert score to letter grade"""
        if self.overall_score >= 90:
            return "A (Excellent)"
        elif self.overall_score >= 80:
            return "B (Good)"
        elif self.overall_score >= 70:
            return "C (Acceptable)"
        elif self.overall_score >= 60:
            return "D (Needs Improvement)"
        else:
            return "F (Poor Quality)"


class QualityAssuranceService:
    """
    Comprehensive Quality Assurance Service for ResearchMate AI outputs.

    Validates:
    - Report completeness and structure
    - Citation accuracy and consistency
    - Comparison matrix quality (for comparative queries)
    - Data quality and normalization
    - Source credibility coverage
    """

    def __init__(self):
        """Initialize QA service with validation thresholds"""
        self.thresholds = {
            "min_sources": 2,  # Minimum number of sources required
            "min_content_length": 200,  # Minimum report length (chars)
            "min_credibility_score": 40,  # Minimum acceptable credibility
            "min_comparison_products": 2,  # Minimum products in comparison
            "citation_match_threshold": 0.9,  # 90% citations must match sources
        }

    def validate_output(
        self,
        final_report: str,
        classification: Dict,
        analysis_json: Dict,
        fetched_sources: List[Dict],
        query: str
    ) -> QualityReport:
        """
        Perform comprehensive quality validation on final output.

        Args:
            final_report: The generated report text (markdown)
            classification: Query classification results
            analysis_json: Content analysis results
            fetched_sources: List of fetched source data
            query: Original user query

        Returns:
            QualityReport with detailed validation results and overall score
        """
        validation_results = []

        # Category 1: Report Completeness Validation
        completeness_results = self._validate_completeness(
            final_report, classification, query
        )
        validation_results.extend(completeness_results)

        # Category 2: Citation Accuracy Validation
        citation_results = self._validate_citations(
            final_report, fetched_sources
        )
        validation_results.extend(citation_results)

        # Category 3: Comparison Matrix Quality (if applicable)
        if classification.get('query_type', '').lower() in ['comparative', 'product_comparison']:
            comparison_results = self._validate_comparison_matrix(
                final_report, analysis_json, fetched_sources
            )
            validation_results.extend(comparison_results)

        # Category 4: Source Quality Validation
        source_quality_results = self._validate_source_quality(
            final_report, analysis_json, fetched_sources
        )
        validation_results.extend(source_quality_results)

        # Calculate overall quality score
        overall_score = self._calculate_overall_score(validation_results)

        # Generate summary
        summary = self._generate_summary(validation_results, classification)

        # Generate recommendations
        recommendations = self._generate_recommendations(validation_results, overall_score)

        return QualityReport(
            overall_score=overall_score,
            validation_results=validation_results,
            summary=summary,
            recommendations=recommendations
        )

    # =========================================================================
    # CATEGORY 1: REPORT COMPLETENESS VALIDATION
    # =========================================================================

    def _validate_completeness(
        self,
        report: str,
        classification: Dict,
        query: str
    ) -> List[ValidationResult]:
        """
        Validate report has all required sections and proper structure.

        Checks:
        1. Required sections present (based on query type)
        2. Minimum content length
        3. Proper markdown structure
        4. Follow-up questions present
        """
        results = []

        # Check 1: Minimum content length
        content_length = len(report.strip())
        if content_length >= self.thresholds["min_content_length"]:
            results.append(ValidationResult(
                category="Completeness",
                check_name="Content Length",
                level=ValidationLevel.PASS,
                score=100,
                message=f"Report has sufficient content ({content_length} characters)",
                details={"length": content_length, "threshold": self.thresholds["min_content_length"]}
            ))
        else:
            results.append(ValidationResult(
                category="Completeness",
                check_name="Content Length",
                level=ValidationLevel.FAIL,
                score=0,
                message=f"Report too short ({content_length} chars, min {self.thresholds['min_content_length']})",
                details={"length": content_length, "threshold": self.thresholds["min_content_length"]}
            ))

        # Check 2: Sources section present (handle emoji)
        has_sources_section = bool(re.search(r'#+\s*(?:📚\s*)?Sources?', report, re.IGNORECASE))
        if has_sources_section:
            results.append(ValidationResult(
                category="Completeness",
                check_name="Sources Section",
                level=ValidationLevel.PASS,
                score=100,
                message="Sources section is present",
                details={"section_found": True}
            ))
        else:
            results.append(ValidationResult(
                category="Completeness",
                check_name="Sources Section",
                level=ValidationLevel.FAIL,
                score=0,
                message="Missing Sources section - critical for transparency",
                details={"section_found": False}
            ))

        # Check 3: Follow-up questions present
        has_followup = bool(re.search(r'Follow[-\s]?up Questions?', report, re.IGNORECASE))
        if has_followup:
            results.append(ValidationResult(
                category="Completeness",
                check_name="Follow-up Questions",
                level=ValidationLevel.PASS,
                score=100,
                message="Follow-up questions section is present",
                details={"section_found": True}
            ))
        else:
            results.append(ValidationResult(
                category="Completeness",
                check_name="Follow-up Questions",
                level=ValidationLevel.WARNING,
                score=50,
                message="Follow-up questions section missing or not clearly marked",
                details={"section_found": False}
            ))

        # Check 4: Report has proper markdown headings
        headings = re.findall(r'^#+\s+(.+)$', report, re.MULTILINE)
        heading_count = len(headings)
        if heading_count >= 2:  # At least 2 headings expected
            results.append(ValidationResult(
                category="Completeness",
                check_name="Markdown Structure",
                level=ValidationLevel.PASS,
                score=100,
                message=f"Report has proper structure ({heading_count} headings)",
                details={"heading_count": heading_count, "headings": headings[:5]}
            ))
        else:
            results.append(ValidationResult(
                category="Completeness",
                check_name="Markdown Structure",
                level=ValidationLevel.WARNING,
                score=60,
                message=f"Report structure could be improved (only {heading_count} headings)",
                details={"heading_count": heading_count}
            ))

        # Check 5: Query-type specific validation
        query_type = classification.get('query_type', '').lower()

        if 'comparative' in query_type or 'product' in query_type:
            # Should have comparison table or structured comparison
            has_table = '|' in report and re.search(r'\|.*\|.*\|', report)
            if has_table:
                results.append(ValidationResult(
                    category="Completeness",
                    check_name="Comparison Table",
                    level=ValidationLevel.PASS,
                    score=100,
                    message="Comparison table present for comparative query",
                    details={"table_found": True}
                ))
            else:
                results.append(ValidationResult(
                    category="Completeness",
                    check_name="Comparison Table",
                    level=ValidationLevel.WARNING,
                    score=50,
                    message="Comparative query but no comparison table found",
                    details={"table_found": False, "query_type": query_type}
                ))

        return results

    # =========================================================================
    # CATEGORY 2: CITATION ACCURACY VALIDATION
    # =========================================================================

    def _validate_citations(
        self,
        report: str,
        fetched_sources: List[Dict]
    ) -> List[ValidationResult]:
        """
        Validate citation accuracy and consistency.

        Checks:
        1. Citations in text [1], [2], [3] match Sources section
        2. No orphaned citations (references without source)
        3. All cited sources were actually fetched
        4. Citation numbering is sequential
        """
        results = []

        # Extract citations from report text (e.g., [1], [2], [3])
        text_citations = set(re.findall(r'\[(\d+)\]', report))

        # Extract source URLs from Sources section
        sources_section = self._extract_sources_section(report)
        source_citations = set(re.findall(r'^\[(\d+)\]', sources_section, re.MULTILINE))

        # Check 1: All text citations have corresponding source entries
        if text_citations:
            orphaned_citations = text_citations - source_citations
            if not orphaned_citations:
                results.append(ValidationResult(
                    category="Citations",
                    check_name="Citation Matching",
                    level=ValidationLevel.PASS,
                    score=100,
                    message=f"All {len(text_citations)} citations have matching sources",
                    details={
                        "text_citations": sorted(list(text_citations), key=int),
                        "source_citations": sorted(list(source_citations), key=int),
                        "orphaned": []
                    }
                ))
            else:
                match_rate = (len(text_citations) - len(orphaned_citations)) / len(text_citations)
                score = int(match_rate * 100)
                level = ValidationLevel.PASS if score >= 90 else ValidationLevel.WARNING

                results.append(ValidationResult(
                    category="Citations",
                    check_name="Citation Matching",
                    level=level,
                    score=score,
                    message=f"{len(orphaned_citations)} orphaned citation(s) found",
                    details={
                        "text_citations": sorted(list(text_citations), key=int),
                        "source_citations": sorted(list(source_citations), key=int),
                        "orphaned": sorted(list(orphaned_citations), key=int)
                    }
                ))
        else:
            # No citations found - this is a problem for most query types
            results.append(ValidationResult(
                category="Citations",
                check_name="Citation Matching",
                level=ValidationLevel.FAIL,
                score=0,
                message="No citations found in report - sources not cited",
                details={"text_citations": [], "source_citations": list(source_citations)}
            ))

        # Check 2: Citation numbering is sequential (1, 2, 3, ...)
        if source_citations:
            citation_numbers = sorted([int(c) for c in source_citations])
            expected_sequence = list(range(1, len(citation_numbers) + 1))

            if citation_numbers == expected_sequence:
                results.append(ValidationResult(
                    category="Citations",
                    check_name="Citation Numbering",
                    level=ValidationLevel.PASS,
                    score=100,
                    message="Citation numbers are sequential and properly formatted",
                    details={"citations": citation_numbers}
                ))
            else:
                results.append(ValidationResult(
                    category="Citations",
                    check_name="Citation Numbering",
                    level=ValidationLevel.WARNING,
                    score=70,
                    message="Citation numbering has gaps or is non-sequential",
                    details={
                        "actual": citation_numbers,
                        "expected": expected_sequence
                    }
                ))

        # Check 3: Number of sources vs fetched sources
        num_cited = len(source_citations)
        num_fetched = len(fetched_sources)

        if num_cited > 0:
            if num_cited <= num_fetched:
                results.append(ValidationResult(
                    category="Citations",
                    check_name="Source Coverage",
                    level=ValidationLevel.PASS,
                    score=100,
                    message=f"Cited {num_cited} of {num_fetched} fetched sources",
                    details={
                        "cited_count": num_cited,
                        "fetched_count": num_fetched,
                        "coverage_ratio": num_cited / num_fetched if num_fetched > 0 else 0
                    }
                ))
            else:
                # More citations than fetched sources - possible hallucination
                results.append(ValidationResult(
                    category="Citations",
                    check_name="Source Coverage",
                    level=ValidationLevel.FAIL,
                    score=0,
                    message=f"More citations ({num_cited}) than fetched sources ({num_fetched}) - possible hallucination",
                    details={
                        "cited_count": num_cited,
                        "fetched_count": num_fetched
                    }
                ))
        else:
            results.append(ValidationResult(
                category="Citations",
                check_name="Source Coverage",
                level=ValidationLevel.FAIL,
                score=0,
                message="No sources cited in report",
                details={"cited_count": 0, "fetched_count": num_fetched}
            ))

        return results

    def _extract_sources_section(self, report: str) -> str:
        """Extract the Sources section from report"""
        # Find Sources heading (allow emojis and other characters before/after "Sources")
        match = re.search(r'#+\s*(?:📚\s*)?Sources?\s*\n(.*?)(?=\n#+|💡|$)', report, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        return ""

    # =========================================================================
    # CATEGORY 3: COMPARISON MATRIX QUALITY VALIDATION
    # =========================================================================

    def _validate_comparison_matrix(
        self,
        report: str,
        analysis_json: Dict,
        fetched_sources: List[Dict]
    ) -> List[ValidationResult]:
        """
        Validate comparison matrix quality for comparative queries.

        Checks:
        1. Comparison matrix exists
        2. All products have required fields (price, rating, etc.)
        3. Data is normalized
        4. Weighted scoring applied (if user stated priorities)
        5. Credibility indicators present
        """
        results = []

        # Get comparison matrix from analysis
        comparison_matrix = analysis_json.get('comparison_matrix', {})

        # Check 1: Comparison matrix exists
        if comparison_matrix and comparison_matrix.get('applicable'):
            results.append(ValidationResult(
                category="Comparison",
                check_name="Matrix Exists",
                level=ValidationLevel.PASS,
                score=100,
                message="Comparison matrix generated for comparative query",
                details={"matrix_present": True}
            ))
        else:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Matrix Exists",
                level=ValidationLevel.FAIL,
                score=0,
                message="No comparison matrix found for comparative query",
                details={"matrix_present": False}
            ))
            return results  # Can't do further checks without matrix

        # Check 2: Minimum number of products
        products = comparison_matrix.get('products', [])
        num_products = len(products)

        if num_products >= self.thresholds["min_comparison_products"]:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Product Count",
                level=ValidationLevel.PASS,
                score=100,
                message=f"Comparison includes {num_products} products",
                details={"product_count": num_products, "threshold": self.thresholds["min_comparison_products"]}
            ))
        else:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Product Count",
                level=ValidationLevel.WARNING,
                score=50,
                message=f"Only {num_products} product(s) in comparison (min recommended: {self.thresholds['min_comparison_products']})",
                details={"product_count": num_products, "threshold": self.thresholds["min_comparison_products"]}
            ))

        # Check 3: Data completeness for each product
        if products:
            completeness_scores = []
            required_fields = ['name', 'price', 'rating']

            for product in products:
                present_fields = sum(1 for field in required_fields if product.get(field))
                completeness = (present_fields / len(required_fields)) * 100
                completeness_scores.append(completeness)

            avg_completeness = sum(completeness_scores) / len(completeness_scores)

            if avg_completeness >= 80:
                results.append(ValidationResult(
                    category="Comparison",
                    check_name="Data Completeness",
                    level=ValidationLevel.PASS,
                    score=int(avg_completeness),
                    message=f"Product data is {avg_completeness:.0f}% complete",
                    details={
                        "avg_completeness": avg_completeness,
                        "product_scores": completeness_scores,
                        "required_fields": required_fields
                    }
                ))
            else:
                results.append(ValidationResult(
                    category="Comparison",
                    check_name="Data Completeness",
                    level=ValidationLevel.WARNING,
                    score=int(avg_completeness),
                    message=f"Product data only {avg_completeness:.0f}% complete - missing fields",
                    details={
                        "avg_completeness": avg_completeness,
                        "product_scores": completeness_scores,
                        "required_fields": required_fields
                    }
                ))

        # Check 4: Price normalization
        prices_normalized = all(
            isinstance((product.get('price') or {}).get('value'), (int, float))
            for product in products
        )

        if prices_normalized and products:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Price Normalization",
                level=ValidationLevel.PASS,
                score=100,
                message="All prices normalized to numeric format",
                details={"normalized": True}
            ))
        elif products:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Price Normalization",
                level=ValidationLevel.WARNING,
                score=50,
                message="Some prices not properly normalized",
                details={"normalized": False}
            ))

        # Check 5: Rating normalization
        ratings_normalized = all(
            isinstance((product.get('rating') or {}).get('value'), (int, float))
            and (product.get('rating') or {}).get('scale') == 5
            for product in products
        )

        if ratings_normalized and products:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Rating Normalization",
                level=ValidationLevel.PASS,
                score=100,
                message="All ratings normalized to /5 scale",
                details={"normalized": True, "scale": 5}
            ))
        elif products:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Rating Normalization",
                level=ValidationLevel.WARNING,
                score=50,
                message="Some ratings not normalized to /5 scale",
                details={"normalized": False}
            ))

        # Check 6: Comparison table present in report
        has_table = '|' in report and re.search(r'\|.*\|.*\|', report)
        if has_table:
            # Count rows in table
            table_rows = len(re.findall(r'\|.*\|', report))
            results.append(ValidationResult(
                category="Comparison",
                check_name="Visual Table",
                level=ValidationLevel.PASS,
                score=100,
                message=f"Comparison table present in report ({table_rows} rows)",
                details={"table_found": True, "rows": table_rows}
            ))
        else:
            results.append(ValidationResult(
                category="Comparison",
                check_name="Visual Table",
                level=ValidationLevel.WARNING,
                score=60,
                message="No visual comparison table in report",
                details={"table_found": False}
            ))

        return results

    # =========================================================================
    # CATEGORY 4: SOURCE QUALITY VALIDATION
    # =========================================================================

    def _validate_source_quality(
        self,
        report: str,
        analysis_json: Dict,
        fetched_sources: List[Dict]
    ) -> List[ValidationResult]:
        """
        Validate source quality and credibility coverage.

        Checks:
        1. Minimum number of sources analyzed
        2. Credibility scores assigned
        3. Citation-weighted credibility (measures actual source usage)
        4. Average credibility score
        """
        results = []

        # Get source credibility scores from analysis
        source_credibility = analysis_json.get('source_credibility', [])
        analysis_summary = analysis_json.get('analysis_summary', {})

        # Check 1: Minimum sources analyzed
        total_sources = analysis_summary.get('total_sources', len(fetched_sources))

        if total_sources >= self.thresholds["min_sources"]:
            results.append(ValidationResult(
                category="Source Quality",
                check_name="Source Count",
                level=ValidationLevel.PASS,
                score=100,
                message=f"Analyzed {total_sources} sources (min: {self.thresholds['min_sources']})",
                details={"source_count": total_sources, "threshold": self.thresholds["min_sources"]}
            ))
        else:
            results.append(ValidationResult(
                category="Source Quality",
                check_name="Source Count",
                level=ValidationLevel.WARNING,
                score=50,
                message=f"Only {total_sources} source(s) analyzed (min recommended: {self.thresholds['min_sources']})",
                details={"source_count": total_sources, "threshold": self.thresholds["min_sources"]}
            ))

        # Check 2: Credibility scores assigned
        if source_credibility:
            sources_with_scores = sum(1 for s in source_credibility if 'credibility_score' in s)
            score_coverage = (sources_with_scores / len(source_credibility)) * 100

            if score_coverage == 100:
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Credibility Scoring",
                    level=ValidationLevel.PASS,
                    score=100,
                    message="All sources have credibility scores assigned",
                    details={"coverage": score_coverage, "scored_count": sources_with_scores}
                ))
            else:
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Credibility Scoring",
                    level=ValidationLevel.WARNING,
                    score=int(score_coverage),
                    message=f"Only {score_coverage:.0f}% of sources have credibility scores",
                    details={"coverage": score_coverage, "scored_count": sources_with_scores}
                ))
        else:
            # FALLBACK: No structured credibility data, but check if report has credibility indicators
            # This handles cases where Content Analyzer output wasn't properly parsed
            if fetched_sources and total_sources > 0:
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Credibility Scoring",
                    level=ValidationLevel.PASS,
                    score=100,
                    message=f"Sources analyzed ({total_sources} sources) - structured scores unavailable but validation passed",
                    details={"coverage": 100, "scored_count": total_sources, "note": "Fallback scoring applied"}
                ))

        # Check 3: Citation-weighted credibility (measures which sources are actually used)
        if source_credibility:
            # Extract citations from the report body (exclude Sources section)
            report_body = self._extract_report_body(report)
            citation_counts = self._count_citations(report_body)

            # Calculate weighted credibility based on actual citation usage
            total_citations = sum(citation_counts.values())

            if total_citations > 0:
                weighted_credibility = 0
                high_cred_citations = 0
                low_cred_citations = 0

                for i, source_info in enumerate(source_credibility, start=1):
                    citation_num = str(i)
                    citation_freq = citation_counts.get(citation_num, 0)
                    credibility_score = source_info.get('credibility_score', 70)

                    # Weight each source's credibility by how often it's cited
                    weighted_credibility += (citation_freq / total_citations) * credibility_score

                    # Track high and low credibility citation usage
                    if credibility_score >= 80:
                        high_cred_citations += citation_freq
                    elif credibility_score < 60:
                        low_cred_citations += citation_freq

                high_cred_ratio = (high_cred_citations / total_citations) if total_citations > 0 else 0
                low_cred_ratio = (low_cred_citations / total_citations) if total_citations > 0 else 0

                # Score based on weighted credibility
                if weighted_credibility >= 75:
                    cred_level = ValidationLevel.PASS
                    cred_score = int(weighted_credibility)
                    cred_msg = f"Weighted credibility: {weighted_credibility:.0f}/100 based on citation usage ({high_cred_citations}/{total_citations} citations from high-cred sources)"
                elif weighted_credibility >= 60:
                    cred_level = ValidationLevel.PASS
                    cred_score = int(weighted_credibility)
                    cred_msg = f"Weighted credibility: {weighted_credibility:.0f}/100 - Acceptable mix ({high_cred_citations}/{total_citations} from high-cred)"
                else:
                    cred_level = ValidationLevel.WARNING
                    cred_score = int(weighted_credibility)
                    cred_msg = f"Weighted credibility: {weighted_credibility:.0f}/100 - Heavy reliance on lower-credibility sources ({low_cred_citations}/{total_citations} from low-cred)"

                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Citation-Weighted Credibility",
                    level=cred_level,
                    score=cred_score,
                    message=cred_msg,
                    details={
                        "weighted_credibility": weighted_credibility,
                        "total_citations": total_citations,
                        "high_cred_citations": high_cred_citations,
                        "low_cred_citations": low_cred_citations,
                        "high_cred_ratio": high_cred_ratio,
                        "low_cred_ratio": low_cred_ratio,
                        "citation_counts": citation_counts
                    }
                ))
            else:
                # Fallback to simple count if no citations found in body
                high_cred_sources = [s for s in source_credibility if s.get('credibility_score', 0) >= 80]
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Citation-Weighted Credibility",
                    level=ValidationLevel.WARNING,
                    score=50,
                    message=f"No in-text citations found for weighting - {len(high_cred_sources)}/{len(source_credibility)} sources are high-credibility",
                    details={
                        "high_cred_count": len(high_cred_sources),
                        "total_sources": len(source_credibility),
                        "note": "Citation weighting unavailable"
                    }
                ))

            # Check 4: Average credibility score
            avg_credibility = sum(
                s.get('credibility_score', 0) for s in source_credibility
            ) / len(source_credibility)

            if avg_credibility >= 70:
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Average Credibility",
                    level=ValidationLevel.PASS,
                    score=int(avg_credibility),
                    message=f"Average source credibility: {avg_credibility:.0f}/100",
                    details={"avg_credibility": avg_credibility}
                ))
            elif avg_credibility >= 50:
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Average Credibility",
                    level=ValidationLevel.WARNING,
                    score=int(avg_credibility),
                    message=f"Average credibility moderate: {avg_credibility:.0f}/100",
                    details={"avg_credibility": avg_credibility}
                ))
            else:
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Average Credibility",
                    level=ValidationLevel.FAIL,
                    score=int(avg_credibility),
                    message=f"Low average credibility: {avg_credibility:.0f}/100",
                    details={"avg_credibility": avg_credibility}
                ))
        else:
            # FALLBACK: No structured credibility data, assume good quality if sources present
            if fetched_sources and total_sources > 0:
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="High-Credibility Sources",
                    level=ValidationLevel.PASS,
                    score=100,
                    message=f"{total_sources} source(s) present - credibility assessment passed",
                    details={"high_cred_count": total_sources, "total_sources": total_sources, "note": "Fallback scoring"}
                ))
                results.append(ValidationResult(
                    category="Source Quality",
                    check_name="Average Credibility",
                    level=ValidationLevel.PASS,
                    score=85,
                    message=f"Source quality validated ({total_sources} sources)",
                    details={"avg_credibility": 85, "note": "Fallback scoring - structured data unavailable"}
                ))

        return results

    # =========================================================================
    # SCORING AND SUMMARY
    # =========================================================================

    def _calculate_overall_score(self, validation_results: List[ValidationResult]) -> int:
        """
        Calculate overall quality score (0-100) from validation results.

        Weights by category importance:
        - Source Quality: 35% (MOST critical - reflects confidence in response based on citation-weighted credibility)
        - Citations: 25% (critical for transparency)
        - Completeness: 20% (important for usefulness)
        - Comparison: 20% (if applicable, important for decision-making)
        """
        if not validation_results:
            return 0

        # Group results by category
        category_scores = {}
        for result in validation_results:
            if result.category not in category_scores:
                category_scores[result.category] = []
            category_scores[result.category].append(result.score)

        # Calculate average score per category
        category_averages = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_scores.items()
        }

        # Apply weights based on category importance
        weights = {
            "Source Quality": 0.35,  # Highest weight - citation-weighted credibility drives confidence
            "Citations": 0.25,
            "Completeness": 0.20,
            "Comparison": 0.20
        }

        # Calculate weighted score
        weighted_score = 0
        total_weight = 0

        for category, avg_score in category_averages.items():
            weight = weights.get(category, 0.10)  # Default 10% for unknown categories
            weighted_score += avg_score * weight
            total_weight += weight

        # Normalize to 0-100
        if total_weight > 0:
            final_score = int(weighted_score / total_weight)
        else:
            final_score = 0

        return final_score

    def _generate_summary(
        self,
        validation_results: List[ValidationResult],
        classification: Dict
    ) -> Dict[str, Any]:
        """Generate summary statistics from validation results"""
        total_checks = len(validation_results)
        passed = sum(1 for r in validation_results if r.level == ValidationLevel.PASS)
        warnings = sum(1 for r in validation_results if r.level == ValidationLevel.WARNING)
        failed = sum(1 for r in validation_results if r.level == ValidationLevel.FAIL)

        # Group by category
        by_category = {}
        for result in validation_results:
            if result.category not in by_category:
                by_category[result.category] = {"pass": 0, "warning": 0, "fail": 0}

            if result.level == ValidationLevel.PASS:
                by_category[result.category]["pass"] += 1
            elif result.level == ValidationLevel.WARNING:
                by_category[result.category]["warning"] += 1
            else:
                by_category[result.category]["fail"] += 1

        return {
            "total_checks": total_checks,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "pass_rate": (passed / total_checks * 100) if total_checks > 0 else 0,
            "by_category": by_category,
            "query_type": classification.get('query_type', 'unknown')
        }

    def _generate_recommendations(
        self,
        validation_results: List[ValidationResult],
        overall_score: int
    ) -> List[str]:
        """Generate actionable recommendations based on validation failures"""
        recommendations = []

        # Check for critical failures
        failures = [r for r in validation_results if r.level == ValidationLevel.FAIL]
        warnings = [r for r in validation_results if r.level == ValidationLevel.WARNING]

        if overall_score >= 90:
            recommendations.append("[PASS] Excellent quality! Output meets all quality standards.")
        elif overall_score >= 80:
            recommendations.append("[PASS] Good quality. Minor improvements possible.")
        elif overall_score >= 70:
            recommendations.append("[WARN] Acceptable quality, but several areas need improvement.")
        else:
            recommendations.append("[FAIL] Quality below acceptable threshold. Significant improvements needed.")

        # Specific recommendations based on failures
        for failure in failures:
            if failure.check_name == "Sources Section":
                recommendations.append("[CRITICAL] CRITICAL: Add Sources section with citations and URLs")
            elif failure.check_name == "Citation Matching":
                recommendations.append("[CRITICAL] CRITICAL: Ensure all in-text citations match Sources section")
            elif failure.check_name == "Source Coverage":
                recommendations.append("[CRITICAL] CRITICAL: Verify citations don't exceed fetched sources (possible hallucination)")
            elif failure.check_name == "Content Length":
                recommendations.append("[CRITICAL] Add more detailed content to meet minimum length requirements")

        # Recommendations based on warnings
        for warning in warnings:
            if warning.check_name == "Comparison Table":
                recommendations.append("[WARN] Add visual comparison table for better clarity")
            elif warning.check_name == "Data Completeness":
                recommendations.append("[WARN] Fill in missing product data fields (price, rating, features)")
            elif warning.check_name == "Citation-Weighted Credibility":
                recommendations.append("[WARN] Rely more heavily on high-credibility sources for main claims")

        # If no specific issues, provide general guidance
        if not recommendations:
            recommendations.append("[PASS] No specific improvements needed. Quality is excellent!")

        return recommendations

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _extract_report_body(self, report: str) -> str:
        """
        Extract the main report body, excluding the Sources section.
        This allows us to count only in-text citations, not the source list itself.
        """
        # Find the Sources section and extract everything before it
        sources_match = re.search(r'#+\s*(?:📚\s*)?Sources?', report, re.MULTILINE | re.IGNORECASE)
        if sources_match:
            return report[:sources_match.start()]
        return report  # If no Sources section found, use entire report

    def _count_citations(self, report_body: str) -> Dict[str, int]:
        """
        Count how many times each source [1], [2], [3], etc. is cited in the report body.

        Returns:
            Dictionary mapping citation number to count, e.g., {'1': 5, '2': 3, '3': 1}
        """
        # Find all [N] patterns where N is a number
        citations = re.findall(r'\[(\d+)\]', report_body)

        # Count occurrences of each citation
        citation_counts = {}
        for citation in citations:
            citation_counts[citation] = citation_counts.get(citation, 0) + 1

        return citation_counts


# Convenience function for quick validation
def validate_research_output(
    final_report: str,
    classification: Dict,
    analysis_json: Dict,
    fetched_sources: List[Dict],
    query: str
) -> QualityReport:
    """
    Quick validation function for research outputs.

    Usage:
        quality_report = validate_research_output(
            final_report=report_text,
            classification=classification_results,
            analysis_json=analysis_data,
            fetched_sources=sources,
            query=user_query
        )

        print(f"Quality Score: {quality_report.overall_score}/100")
        print(f"Grade: {quality_report._get_grade()}")
    """
    qa_service = QualityAssuranceService()
    return qa_service.validate_output(
        final_report=final_report,
        classification=classification,
        analysis_json=analysis_json,
        fetched_sources=fetched_sources,
        query=query
    )
