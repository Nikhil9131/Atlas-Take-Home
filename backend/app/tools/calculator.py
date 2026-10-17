"""Deterministic Market Research Calculator Tool.
Performs exact Python mathematical calculations without relying on LLM arithmetic.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CalculationResult:
    metric: str
    formula: str
    inputs: Dict[str, Any]
    assumptions: str
    result_value: float
    result_text: str
    is_derived: bool = True
    scope_note: Optional[str] = None


class MarketCalculator:
    """Provides deterministic financial and market research projections."""

    @staticmethod
    def calculate_cagr_projection(
        base_value: float,
        base_year: int,
        target_year: int,
        cagr_percent: float,
        metric_name: str = "Market Size Projection",
        unit: str = "USD Billion"
    ) -> CalculationResult:
        """
        Compound Annual Growth Rate Projection:
        FV = PV * (1 + r)^n
        """
        years = target_year - base_year
        if years < 0:
            raise ValueError(f"Target year ({target_year}) cannot be earlier than base year ({base_year})")

        rate = cagr_percent / 100.0
        future_value = base_value * ((1.0 + rate) ** years)
        future_value_rounded = round(future_value, 2)

        formula = f"Future Value = Base Value × (1 + CAGR)^n = {base_value} × (1 + {rate:.3f})^{years}"
        inputs = {
            "base_value": base_value,
            "base_year": base_year,
            "target_year": target_year,
            "cagr_percent": cagr_percent,
            "compounding_periods": years,
            "unit": unit
        }
        assumptions = (
            f"Assumes steady annual compound growth of {cagr_percent}% over {years} annual periods "
            f"from baseline year {base_year} to {target_year}."
        )

        return CalculationResult(
            metric=metric_name,
            formula=formula,
            inputs=inputs,
            assumptions=assumptions,
            result_value=future_value_rounded,
            result_text=f"{unit} {future_value_rounded:.2f}" if unit.startswith("USD") else f"{future_value_rounded:.2f} {unit}",
            is_derived=True
        )

    @staticmethod
    def calculate_regional_projection(
        global_base_value: float,
        base_year: int,
        target_year: int,
        cagr_percent: float,
        regional_share_percent: float,
        region_name: str = "APAC",
        unit: str = "USD Billion"
    ) -> CalculationResult:
        """
        Calculates projected regional market value by projecting global market size and applying regional share.
        Handles base-year vs forecast window ambiguity explicitly.
        """
        years = target_year - base_year
        rate = cagr_percent / 100.0
        projected_global = global_base_value * ((1.0 + rate) ** years)
        share_ratio = regional_share_percent / 100.0
        projected_regional = projected_global * share_ratio
        projected_regional_rounded = round(projected_regional, 2)

        formula = (
            f"Global FV = {global_base_value} × (1 + {rate:.3f})^{years} = {round(projected_global, 2)} {unit}; "
            f"Regional Value = Global FV × {regional_share_percent}% = {projected_regional_rounded} {unit}"
        )

        inputs = {
            "global_base_value": global_base_value,
            "base_year": base_year,
            "target_year": target_year,
            "cagr_percent": cagr_percent,
            "compounding_periods": years,
            "regional_share_percent": regional_share_percent,
            "region": region_name,
            "unit": unit
        }

        assumptions = (
            f"1. Extrapolates the stated 2025–2030 CAGR ({cagr_percent}%) over {years} compounding periods "
            f"starting from the 2024 base value ({unit} {global_base_value}B), noting the methodological ambiguity "
            f"between the 2024 reported baseline and the 2025-2030 growth horizon.\n"
            f"2. Assumes {region_name}'s regional revenue share remains constant at {regional_share_percent}% "
            f"through {target_year}."
        )

        return CalculationResult(
            metric=f"{region_name} Market Size in {target_year} (Derived Estimate)",
            formula=formula,
            inputs=inputs,
            assumptions=assumptions,
            result_value=projected_regional_rounded,
            result_text=f"{unit} {projected_regional_rounded:.2f}" if unit.startswith("USD") else f"{projected_regional_rounded:.2f} {unit}",
            is_derived=True,
            scope_note="Derived projection. Stated report does not provide a directly quoted 2030 APAC figure."
        )
