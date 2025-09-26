import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date
import logging
from dataclasses import dataclass
from statistics import mean, stdev
from schemas.financial_data import FinancialStatement, FinancialProjection

logger = logging.getLogger(__name__)

@dataclass
class ProjectionAssumptions:
    """Assumptions used for financial projections"""
    base_year: int
    projection_years: int = 5
    
    # Growth assumptions
    revenue_growth_method: str = "trend_analysis"  # trend_analysis, industry_average, manual
    manual_revenue_growth: Optional[List[float]] = None
    
    # Margin assumptions
    maintain_margins: bool = True
    improve_efficiency: bool = False
    efficiency_improvement_rate: float = 0.01  # 1% per year
    
    # Market assumptions
    market_growth_rate: Optional[float] = None
    market_share_change: Optional[float] = None
    
    # Constraints
    max_revenue_growth: float = 0.50  # 50% max growth per year
    min_revenue_growth: float = -0.20  # -20% max decline per year
    
    # Risk factors
    economic_cycle_adjustment: bool = True
    volatility_adjustment: bool = True
    
class FinancialProjectionEngine:
    def __init__(self):
        self.confidence_thresholds = {
            'high': {'min_years': 4, 'max_volatility': 0.15, 'min_trend_strength': 0.7},
            'medium': {'min_years': 3, 'max_volatility': 0.30, 'min_trend_strength': 0.5},
            'low': {'min_years': 2, 'max_volatility': 1.0, 'min_trend_strength': 0.0}
        }

    def _calculate_growth_rates(self, values: List[float]) -> Dict[str, float]:
        """Calculate various growth rate metrics"""
        if len(values) < 2:
            return {'compound_growth': 0.0, 'average_growth': 0.0, 'volatility': 0.0}
        
        # Remove zeros and None values
        clean_values = [v for v in values if v and v != 0]
        if len(clean_values) < 2:
            return {'compound_growth': 0.0, 'average_growth': 0.0, 'volatility': 0.0}
        
        # Calculate year-over-year growth rates
        growth_rates = []
        for i in range(1, len(clean_values)):
            if clean_values[i-1] != 0:
                growth_rate = (clean_values[i] - clean_values[i-1]) / abs(clean_values[i-1])
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return {'compound_growth': 0.0, 'average_growth': 0.0, 'volatility': 0.0}
        
        # Compound Annual Growth Rate (CAGR)
        years = len(clean_values) - 1
        if years > 0 and clean_values[0] != 0:
            cagr = (clean_values[-1] / abs(clean_values[0])) ** (1/years) - 1
        else:
            cagr = 0.0
        
        # Average growth rate
        avg_growth = mean(growth_rates)
        
        # Volatility (standard deviation of growth rates)
        volatility = stdev(growth_rates) if len(growth_rates) > 1 else 0.0
        
        return {
            'compound_growth': cagr,
            'average_growth': avg_growth,
            'volatility': volatility,
            'trend_strength': abs(cagr) / (volatility + 0.001)  # Avoid division by zero
        }

    def _apply_constraints(self, growth_rate: float, assumptions: ProjectionAssumptions) -> float:
        """Apply growth rate constraints"""
        return max(assumptions.min_revenue_growth, 
                  min(assumptions.max_revenue_growth, growth_rate))

    def _calculate_trend_based_growth(self, 
                                    historical_data: List[FinancialStatement], 
                                    assumptions: ProjectionAssumptions) -> List[float]:
        """Calculate growth rates based on historical trends"""
        
        if len(historical_data) < 2:
            return [0.05] * assumptions.projection_years  # Default 5% growth
        
        # Extract revenue data
        revenue_data = []
        for stmt in sorted(historical_data, key=lambda x: x.year):
            if stmt.revenue:
                revenue_data.append(float(stmt.revenue))
        
        if len(revenue_data) < 2:
            return [0.05] * assumptions.projection_years
        
        # Calculate growth metrics
        growth_metrics = self._calculate_growth_rates(revenue_data)
        
        # Choose growth rate based on trend strength and volatility
        if growth_metrics['trend_strength'] > 0.7 and growth_metrics['volatility'] < 0.15:
            # Strong, stable trend - use CAGR
            base_growth = growth_metrics['compound_growth']
        elif growth_metrics['volatility'] < 0.30:
            # Moderate volatility - use average
            base_growth = growth_metrics['average_growth']
        else:
            # High volatility - use conservative estimate
            base_growth = min(growth_metrics['compound_growth'], growth_metrics['average_growth'])
        
        # Apply economic cycle adjustments
        if assumptions.economic_cycle_adjustment:
            # Assume moderate economic cycles (reduce growth in later years)
            cycle_adjustments = [1.0, 0.95, 0.90, 0.90, 0.85]
        else:
            cycle_adjustments = [1.0] * assumptions.projection_years
        
        # Generate growth rates for each year
        growth_rates = []
        for i in range(assumptions.projection_years):
            # Gradually revert to market average (assume 3% long-term GDP growth)
            reversion_factor = 0.03 * (i / assumptions.projection_years)
            adjusted_growth = base_growth * (1 - reversion_factor) + 0.03 * reversion_factor
            
            # Apply cycle adjustment
            adjusted_growth *= cycle_adjustments[i]
            
            # Apply constraints
            adjusted_growth = self._apply_constraints(adjusted_growth, assumptions)
            
            growth_rates.append(adjusted_growth)
        
        return growth_rates

    def _project_income_statement(self, 
                                 base_statement: FinancialStatement,
                                 revenue_growth: float,
                                 assumptions: ProjectionAssumptions,
                                 year_index: int) -> Dict[str, Decimal]:
        """Project income statement items based on base year and growth assumptions"""
        
        projected = {}
        
        # Revenue
        if base_statement.revenue:
            projected['revenue'] = base_statement.revenue * Decimal(str(1 + revenue_growth))
        
        # Cost ratios (maintain or improve based on assumptions)
        if base_statement.revenue and projected.get('revenue'):
            base_revenue = float(base_statement.revenue)
            
            # Cost of goods sold ratio
            if base_statement.cost_of_goods_sold and base_revenue > 0:
                cogs_ratio = float(base_statement.cost_of_goods_sold) / base_revenue
                if assumptions.improve_efficiency:
                    cogs_ratio *= (1 - assumptions.efficiency_improvement_rate * year_index)
                projected['cost_of_goods_sold'] = projected['revenue'] * Decimal(str(cogs_ratio))
            
            # Operating expenses ratio
            if base_statement.operating_expenses and base_revenue > 0:
                opex_ratio = float(base_statement.operating_expenses) / base_revenue
                if assumptions.improve_efficiency:
                    opex_ratio *= (1 - assumptions.efficiency_improvement_rate * year_index * 0.5)  # Slower improvement
                projected['operating_expenses'] = projected['revenue'] * Decimal(str(opex_ratio))
            
            # Calculate gross profit
            if projected.get('revenue') and projected.get('cost_of_goods_sold'):
                projected['gross_profit'] = projected['revenue'] - projected['cost_of_goods_sold']
            
            # Calculate EBIT
            if projected.get('gross_profit') and projected.get('operating_expenses'):
                projected['ebit'] = projected['gross_profit'] - projected['operating_expenses']
            elif projected.get('revenue'):
                # Alternative calculation if we have EBIT margin
                if base_statement.ebit and base_revenue > 0:
                    ebit_margin = float(base_statement.ebit) / base_revenue
                    projected['ebit'] = projected['revenue'] * Decimal(str(ebit_margin))
            
            # Depreciation (assume constant rate of fixed assets)
            if base_statement.depreciation:
                depreciation_growth = revenue_growth * 0.7  # Depreciation grows slower than revenue
                projected['depreciation'] = base_statement.depreciation * Decimal(str(1 + depreciation_growth))
            
            # EBITDA
            if projected.get('ebit') and projected.get('depreciation'):
                projected['ebitda'] = projected['ebit'] + projected['depreciation']
            elif projected.get('ebit'):
                projected['ebitda'] = projected['ebit']
            
            # Financial items (assume constant)
            if base_statement.financial_income:
                projected['financial_income'] = base_statement.financial_income
            if base_statement.financial_expenses:
                projected['financial_expenses'] = base_statement.financial_expenses
            
            # Profit before tax
            financial_result = Decimal('0')
            if projected.get('financial_income'):
                financial_result += projected['financial_income']
            if projected.get('financial_expenses'):
                financial_result -= projected['financial_expenses']
            
            if projected.get('ebit'):
                projected['profit_before_tax'] = projected['ebit'] + financial_result
            
            # Tax (assume constant rate)
            if projected.get('profit_before_tax') and base_statement.profit_before_tax and base_statement.tax_expense:
                if base_statement.profit_before_tax > 0:
                    tax_rate = float(base_statement.tax_expense) / float(base_statement.profit_before_tax)
                    projected['tax_expense'] = projected['profit_before_tax'] * Decimal(str(tax_rate))
                else:
                    projected['tax_expense'] = Decimal('0')
            
            # Net profit
            if projected.get('profit_before_tax') and projected.get('tax_expense'):
                projected['net_profit'] = projected['profit_before_tax'] - projected['tax_expense']
        
        return projected

    def _project_balance_sheet(self, 
                              base_statement: FinancialStatement,
                              income_projection: Dict[str, Decimal],
                              revenue_growth: float,
                              year_index: int) -> Dict[str, Decimal]:
        """Project balance sheet items"""
        
        projected = {}
        
        # Assets generally grow with revenue
        asset_growth = revenue_growth
        
        if base_statement.current_assets:
            projected['current_assets'] = base_statement.current_assets * Decimal(str(1 + asset_growth))
        
        if base_statement.fixed_assets:
            # Fixed assets grow slower than revenue
            fixed_asset_growth = revenue_growth * 0.6
            projected['fixed_assets'] = base_statement.fixed_assets * Decimal(str(1 + fixed_asset_growth))
        
        # Total assets
        if projected.get('current_assets') and projected.get('fixed_assets'):
            projected['total_assets'] = projected['current_assets'] + projected['fixed_assets']
        elif projected.get('current_assets'):
            projected['total_assets'] = projected['current_assets']
        elif projected.get('fixed_assets'):
            projected['total_assets'] = projected['fixed_assets']
        
        # Liabilities
        if base_statement.current_liabilities:
            # Current liabilities grow with revenue (working capital needs)
            projected['current_liabilities'] = base_statement.current_liabilities * Decimal(str(1 + revenue_growth))
        
        if base_statement.long_term_liabilities:
            # Long-term liabilities grow slower
            lt_liability_growth = revenue_growth * 0.3
            projected['long_term_liabilities'] = base_statement.long_term_liabilities * Decimal(str(1 + lt_liability_growth))
        
        # Total liabilities
        if projected.get('current_liabilities') and projected.get('long_term_liabilities'):
            projected['total_liabilities'] = projected['current_liabilities'] + projected['long_term_liabilities']
        
        # Equity (balancing item)
        if projected.get('total_assets') and projected.get('total_liabilities'):
            projected['equity'] = projected['total_assets'] - projected['total_liabilities']
        elif base_statement.equity and income_projection.get('net_profit'):
            # Alternative: add retained earnings to equity
            projected['equity'] = base_statement.equity + income_projection['net_profit']
        
        return projected

    def _determine_confidence_level(self, 
                                  historical_data: List[FinancialStatement],
                                  growth_metrics: Dict[str, float]) -> str:
        """Determine confidence level for projections"""
        
        num_years = len(historical_data)
        volatility = growth_metrics.get('volatility', 1.0)
        trend_strength = growth_metrics.get('trend_strength', 0.0)
        
        # Check against thresholds
        for level in ['high', 'medium', 'low']:
            thresholds = self.confidence_thresholds[level]
            if (num_years >= thresholds['min_years'] and 
                volatility <= thresholds['max_volatility'] and 
                trend_strength >= thresholds['min_trend_strength']):
                return level
        
        return 'low'

    async def generate_projections(self, 
                                 historical_data: List[FinancialStatement],
                                 assumptions: ProjectionAssumptions) -> List[FinancialProjection]:
        """Generate financial projections based on historical data"""
        
        if not historical_data:
            raise ValueError("No historical data provided")
        
        # Sort historical data by year
        historical_data.sort(key=lambda x: x.year)
        base_statement = historical_data[-1]  # Most recent year
        
        # Calculate growth rates
        if assumptions.manual_revenue_growth:
            growth_rates = assumptions.manual_revenue_growth[:assumptions.projection_years]
            # Pad with last value if needed
            while len(growth_rates) < assumptions.projection_years:
                growth_rates.append(growth_rates[-1] if growth_rates else 0.05)
        else:
            growth_rates = self._calculate_trend_based_growth(historical_data, assumptions)
        
        # Calculate growth metrics for confidence assessment
        revenue_values = [float(stmt.revenue) for stmt in historical_data if stmt.revenue]
        growth_metrics = self._calculate_growth_rates(revenue_values)
        confidence_level = self._determine_confidence_level(historical_data, growth_metrics)
        
        # Generate projections for each year
        projections = []
        current_statement = base_statement
        
        for i in range(assumptions.projection_years):
            projection_year = assumptions.base_year + i + 1
            revenue_growth = growth_rates[i]
            
            # Project income statement
            income_projection = self._project_income_statement(
                current_statement, revenue_growth, assumptions, i
            )
            
            # Project balance sheet
            balance_projection = self._project_balance_sheet(
                current_statement, income_projection, revenue_growth, i
            )
            
            # Combine projections
            all_projections = {**income_projection, **balance_projection}
            
            # Create projection object
            projection = FinancialProjection(
                year=projection_year,
                revenue_growth=Decimal(str(revenue_growth)),
                projected_revenue=all_projections.get('revenue'),
                projected_ebitda=all_projections.get('ebitda'),
                projected_net_profit=all_projections.get('net_profit'),
                margin_assumptions={
                    'revenue_growth': revenue_growth,
                    'maintain_margins': assumptions.maintain_margins,
                    'efficiency_improvement': assumptions.efficiency_improvement_rate if assumptions.improve_efficiency else 0
                },
                assumptions=[
                    f"Revenue growth: {revenue_growth:.1%}",
                    f"Growth method: {assumptions.revenue_growth_method}",
                    f"Margin assumptions: {'maintained' if assumptions.maintain_margins else 'variable'}",
                    f"Based on {len(historical_data)} years of historical data"
                ],
                confidence_level=confidence_level
            )
            
            projections.append(projection)
            
            # Create a temporary statement for next iteration
            current_statement = FinancialStatement(
                year=projection_year,
                period_start=date(projection_year, 1, 1),
                period_end=date(projection_year, 12, 31),
                source="projection",
                **{k: v for k, v in all_projections.items() if v is not None}
            )
        
        return projections

    def calculate_key_metrics(self, 
                            historical_data: List[FinancialStatement],
                            projections: List[FinancialProjection]) -> Dict[str, Any]:
        """Calculate key financial metrics and ratios"""
        
        metrics = {}
        
        if historical_data:
            latest = historical_data[-1]
            
            # Historical metrics
            if latest.revenue and latest.revenue > 0:
                revenue = float(latest.revenue)
                
                if latest.net_profit:
                    metrics['current_net_margin'] = float(latest.net_profit) / revenue
                
                if latest.ebitda:
                    metrics['current_ebitda_margin'] = float(latest.ebitda) / revenue
                
                if latest.total_assets:
                    metrics['asset_turnover'] = revenue / float(latest.total_assets)
                
                if latest.equity:
                    metrics['roe'] = float(latest.net_profit) / float(latest.equity) if latest.net_profit else 0
        
        # Projection metrics
        if projections:
            revenue_growth_rates = [float(p.revenue_growth) for p in projections if p.revenue_growth]
            if revenue_growth_rates:
                metrics['avg_projected_growth'] = mean(revenue_growth_rates)
                metrics['growth_volatility'] = stdev(revenue_growth_rates) if len(revenue_growth_rates) > 1 else 0
            
            # Calculate projected metrics for final year
            final_projection = projections[-1]
            if final_projection.projected_revenue and final_projection.projected_revenue > 0:
                final_revenue = float(final_projection.projected_revenue)
                
                if final_projection.projected_net_profit:
                    metrics['projected_net_margin'] = float(final_projection.projected_net_profit) / final_revenue
                
                if final_projection.projected_ebitda:
                    metrics['projected_ebitda_margin'] = float(final_projection.projected_ebitda) / final_revenue
        
        return metrics


# Utility function for API endpoints
async def create_financial_projections(
    historical_data: List[FinancialStatement],
    assumptions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create financial projections with default assumptions"""
    
    if not historical_data:
        return {
            'success': False,
            'error': 'No historical data provided',
            'projections': []
        }
    
    try:
        # Create assumptions object
        base_year = max(stmt.year for stmt in historical_data)
        projection_assumptions = ProjectionAssumptions(
            base_year=base_year,
            **(assumptions or {})
        )
        
        # Generate projections
        engine = FinancialProjectionEngine()
        projections = await engine.generate_projections(historical_data, projection_assumptions)
        
        # Calculate key metrics
        key_metrics = engine.calculate_key_metrics(historical_data, projections)
        
        return {
            'success': True,
            'projections': [proj.model_dump(mode="json") for proj in projections],
            'key_metrics': key_metrics,
            'assumptions': projection_assumptions.__dict__,
            'confidence_level': projections[0].confidence_level if projections else 'low'
        }
        
    except Exception as e:
        logger.error(f"Error creating financial projections: {e}")
        return {
            'success': False,
            'error': str(e),
            'projections': []
        }
