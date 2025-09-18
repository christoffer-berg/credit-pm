import openai
import json
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import logging
from schemas.financial_data import FinancialStatement, FinancialProjection, FinancialAnalysis
from services.financial_projections import FinancialProjectionEngine, ProjectionAssumptions
from core.config import settings

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        
    def _calculate_financial_ratios(self, statement: FinancialStatement) -> Dict[str, float]:
        """Calculate key financial ratios for a single year"""
        ratios = {}
        
        try:
            if statement.revenue and statement.revenue > 0:
                revenue = float(statement.revenue)
                
                # Profitability ratios
                if statement.gross_profit:
                    ratios['gross_profit_margin'] = float(statement.gross_profit) / revenue
                
                if statement.ebitda:
                    ratios['ebitda_margin'] = float(statement.ebitda) / revenue
                
                if statement.ebit:
                    ratios['ebit_margin'] = float(statement.ebit) / revenue
                
                if statement.net_profit:
                    ratios['net_profit_margin'] = float(statement.net_profit) / revenue
                
                # Efficiency ratios
                if statement.total_assets:
                    ratios['asset_turnover'] = revenue / float(statement.total_assets)
                
                # Return ratios
                if statement.equity and statement.equity > 0:
                    if statement.net_profit:
                        ratios['roe'] = float(statement.net_profit) / float(statement.equity)
                    ratios['equity_ratio'] = float(statement.equity) / float(statement.total_assets) if statement.total_assets else 0
                
                if statement.total_assets and statement.net_profit:
                    ratios['roa'] = float(statement.net_profit) / float(statement.total_assets)
            
            # Liquidity ratios
            if statement.current_assets and statement.current_liabilities and statement.current_liabilities > 0:
                ratios['current_ratio'] = float(statement.current_assets) / float(statement.current_liabilities)
            
            # Leverage ratios
            if statement.total_liabilities and statement.equity and statement.equity > 0:
                ratios['debt_to_equity'] = float(statement.total_liabilities) / float(statement.equity)
            
            if statement.total_assets and statement.total_assets > 0:
                if statement.total_liabilities:
                    ratios['debt_ratio'] = float(statement.total_liabilities) / float(statement.total_assets)
                if statement.equity:
                    ratios['equity_ratio'] = float(statement.equity) / float(statement.total_assets)
            
            # Interest coverage
            if statement.ebit and statement.financial_expenses and statement.financial_expenses > 0:
                ratios['interest_coverage'] = float(statement.ebit) / float(statement.financial_expenses)
            
        except (ZeroDivisionError, TypeError, ValueError) as e:
            logger.warning(f"Error calculating ratios for year {statement.year}: {e}")
        
        return ratios

    def _analyze_trends(self, historical_data: List[FinancialStatement]) -> Dict[str, Any]:
        """Analyze trends in financial data"""
        if len(historical_data) < 2:
            return {'trend_analysis': 'Insufficient data for trend analysis'}
        
        # Sort by year
        data = sorted(historical_data, key=lambda x: x.year)
        
        trends = {}
        
        # Revenue trend
        revenue_values = [float(stmt.revenue) for stmt in data if stmt.revenue and stmt.revenue > 0]
        if len(revenue_values) >= 2:
            revenue_growth = [(revenue_values[i] - revenue_values[i-1]) / revenue_values[i-1] 
                             for i in range(1, len(revenue_values))]
            trends['revenue_growth_trend'] = {
                'average_growth': sum(revenue_growth) / len(revenue_growth),
                'growth_volatility': self._calculate_volatility(revenue_growth),
                'trend_direction': 'increasing' if revenue_growth[-1] > 0 else 'decreasing'
            }
        
        # Profitability trend
        profit_margins = []
        for stmt in data:
            if stmt.revenue and stmt.net_profit and stmt.revenue > 0:
                profit_margins.append(float(stmt.net_profit) / float(stmt.revenue))
        
        if len(profit_margins) >= 2:
            margin_change = profit_margins[-1] - profit_margins[0]
            trends['profitability_trend'] = {
                'margin_change': margin_change,
                'direction': 'improving' if margin_change > 0 else 'deteriorating',
                'current_margin': profit_margins[-1]
            }
        
        # Leverage trend
        debt_ratios = []
        for stmt in data:
            if stmt.total_assets and stmt.total_liabilities and stmt.total_assets > 0:
                debt_ratios.append(float(stmt.total_liabilities) / float(stmt.total_assets))
        
        if len(debt_ratios) >= 2:
            leverage_change = debt_ratios[-1] - debt_ratios[0]
            trends['leverage_trend'] = {
                'change': leverage_change,
                'direction': 'increasing' if leverage_change > 0 else 'decreasing',
                'current_ratio': debt_ratios[-1]
            }
        
        return trends

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation) of a series"""
        if len(values) < 2:
            return 0.0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _assess_financial_strength(self, 
                                 historical_data: List[FinancialStatement],
                                 projections: List[FinancialProjection]) -> Dict[str, Any]:
        """Assess overall financial strength and assign scores"""
        
        if not historical_data:
            return {'score': 0, 'assessment': 'No data available'}
        
        latest = historical_data[-1]
        scores = {}
        
        # Profitability score (0-25 points)
        if latest.revenue and latest.net_profit and latest.revenue > 0:
            net_margin = float(latest.net_profit) / float(latest.revenue)
            if net_margin > 0.15:  # > 15%
                scores['profitability'] = 25
            elif net_margin > 0.10:  # 10-15%
                scores['profitability'] = 20
            elif net_margin > 0.05:  # 5-10%
                scores['profitability'] = 15
            elif net_margin > 0:  # Profitable
                scores['profitability'] = 10
            else:  # Unprofitable
                scores['profitability'] = 0
        else:
            scores['profitability'] = 5  # No data penalty
        
        # Liquidity score (0-25 points)
        if latest.current_assets and latest.current_liabilities and latest.current_liabilities > 0:
            current_ratio = float(latest.current_assets) / float(latest.current_liabilities)
            if current_ratio > 2.0:
                scores['liquidity'] = 25
            elif current_ratio > 1.5:
                scores['liquidity'] = 20
            elif current_ratio > 1.0:
                scores['liquidity'] = 15
            elif current_ratio > 0.8:
                scores['liquidity'] = 10
            else:
                scores['liquidity'] = 0
        else:
            scores['liquidity'] = 10  # Neutral if no data
        
        # Leverage score (0-25 points)
        if latest.total_assets and latest.total_liabilities and latest.total_assets > 0:
            debt_ratio = float(latest.total_liabilities) / float(latest.total_assets)
            if debt_ratio < 0.3:  # Low leverage
                scores['leverage'] = 25
            elif debt_ratio < 0.5:  # Moderate leverage
                scores['leverage'] = 20
            elif debt_ratio < 0.7:  # High leverage
                scores['leverage'] = 15
            elif debt_ratio < 0.8:  # Very high leverage
                scores['leverage'] = 10
            else:  # Excessive leverage
                scores['leverage'] = 0
        else:
            scores['leverage'] = 10
        
        # Growth potential score (0-25 points)
        if len(historical_data) >= 3:
            revenue_values = [float(stmt.revenue) for stmt in historical_data[-3:] if stmt.revenue]
            if len(revenue_values) >= 2:
                avg_growth = sum((revenue_values[i] - revenue_values[i-1]) / revenue_values[i-1] 
                               for i in range(1, len(revenue_values))) / (len(revenue_values) - 1)
                
                if avg_growth > 0.15:  # > 15% growth
                    scores['growth'] = 25
                elif avg_growth > 0.10:  # 10-15% growth
                    scores['growth'] = 20
                elif avg_growth > 0.05:  # 5-10% growth
                    scores['growth'] = 15
                elif avg_growth > 0:  # Positive growth
                    scores['growth'] = 10
                else:  # Declining
                    scores['growth'] = 5
            else:
                scores['growth'] = 10
        else:
            scores['growth'] = 10
        
        total_score = sum(scores.values())
        
        # Assessment categories
        if total_score >= 85:
            assessment = "Excellent"
            risk_level = "Low"
        elif total_score >= 70:
            assessment = "Strong" 
            risk_level = "Low-Medium"
        elif total_score >= 55:
            assessment = "Good"
            risk_level = "Medium"
        elif total_score >= 40:
            assessment = "Fair"
            risk_level = "Medium-High"
        else:
            assessment = "Weak"
            risk_level = "High"
        
        return {
            'total_score': total_score,
            'component_scores': scores,
            'assessment': assessment,
            'risk_level': risk_level,
            'max_score': 100
        }

    async def _generate_ai_analysis(self, 
                                  historical_data: List[FinancialStatement],
                                  projections: List[FinancialProjection],
                                  key_metrics: Dict[str, Any],
                                  trends: Dict[str, Any],
                                  strength_assessment: Dict[str, Any]) -> str:
        """Generate AI-powered financial analysis"""
        
        # Prepare data for AI analysis
        analysis_context = {
            'historical_years': len(historical_data),
            'latest_year': max(stmt.year for stmt in historical_data) if historical_data else None,
            'projection_years': len(projections),
            'key_metrics': key_metrics,
            'trends': trends,
            'financial_strength': strength_assessment,
            'latest_financials': historical_data[-1].dict() if historical_data else None,
            'projections_summary': [p.dict() for p in projections[:3]] if projections else []  # First 3 years
        }
        
        prompt = f"""
Analyze the following financial data and provide a comprehensive financial analysis:

COMPANY FINANCIAL DATA:
{json.dumps(analysis_context, indent=2, default=str)}

Please provide a detailed financial analysis covering:

1. **Financial Performance Overview**
   - Current financial position and key strengths/weaknesses
   - Revenue and profitability trends
   - Operational efficiency assessment

2. **Key Financial Ratios Analysis**
   - Profitability ratios (margins, returns)
   - Liquidity and solvency ratios
   - Leverage and risk indicators
   - Comparison to industry benchmarks where relevant

3. **Trend Analysis**
   - Historical performance trends
   - Growth trajectory assessment
   - Margin development and cost management

4. **Financial Projections Assessment**
   - Projected growth rates and assumptions
   - Revenue and profitability forecasts
   - Key risks and opportunities

5. **Credit Risk Assessment**
   - Overall financial strength rating
   - Debt capacity and repayment ability
   - Cash flow sustainability
   - Risk factors and mitigants

6. **Strategic Recommendations**
   - Areas for improvement
   - Growth opportunities
   - Financial management recommendations
   - Risk mitigation strategies

Format the response in clear, professional language suitable for credit analysis. Use Swedish financial terminology where appropriate, and provide specific numbers and percentages to support your analysis.
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du är en expert finansanalytiker som specialiserar sig på kreditanalys av svenska företag. Ge professionella och detaljerade analyser baserade på finansiell data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return self._generate_fallback_analysis(historical_data, projections, strength_assessment)

    def _generate_fallback_analysis(self, 
                                   historical_data: List[FinancialStatement],
                                   projections: List[FinancialProjection],
                                   strength_assessment: Dict[str, Any]) -> str:
        """Generate basic analysis when AI is unavailable"""
        
        if not historical_data:
            return "Ingen finansiell data tillgänglig för analys."
        
        latest = historical_data[-1]
        analysis_parts = []
        
        analysis_parts.append("## Finansiell Analys")
        analysis_parts.append(f"**Analysperiod:** {historical_data[0].year}-{latest.year}")
        
        # Performance overview
        if latest.revenue:
            revenue_msek = float(latest.revenue) / 1000000
            analysis_parts.append(f"**Senaste omsättning ({latest.year}):** {revenue_msek:.1f} MSEK")
        
        if latest.net_profit:
            profit_msek = float(latest.net_profit) / 1000000
            margin = (float(latest.net_profit) / float(latest.revenue) * 100) if latest.revenue else 0
            analysis_parts.append(f"**Nettoresultat ({latest.year}):** {profit_msek:.1f} MSEK ({margin:.1f}% marginal)")
        
        # Financial strength
        analysis_parts.append(f"\n**Finansiell styrka:** {strength_assessment['assessment']} ({strength_assessment['total_score']}/100 poäng)")
        analysis_parts.append(f"**Riskbedömning:** {strength_assessment['risk_level']}")
        
        # Projections summary
        if projections:
            avg_growth = sum(float(p.revenue_growth) for p in projections if p.revenue_growth) / len(projections)
            analysis_parts.append(f"\n**Prognostiserad tillväxt:** {avg_growth:.1%} per år")
        
        return "\n".join(analysis_parts)

    async def generate_comprehensive_analysis(self,
                                            company_id: str,
                                            historical_data: List[FinancialStatement],
                                            case_id: Optional[str] = None) -> FinancialAnalysis:
        """Generate comprehensive financial analysis"""
        
        if not historical_data:
            raise ValueError("No historical data provided for analysis")
        
        # Generate projections
        base_year = max(stmt.year for stmt in historical_data)
        assumptions = ProjectionAssumptions(base_year=base_year)
        
        projection_engine = FinancialProjectionEngine()
        projections = await projection_engine.generate_projections(historical_data, assumptions)
        
        # Calculate metrics and trends
        key_metrics = projection_engine.calculate_key_metrics(historical_data, projections)
        trends = self._analyze_trends(historical_data)
        strength_assessment = self._assess_financial_strength(historical_data, projections)
        
        # Calculate ratios for all years
        historical_ratios = {}
        for stmt in historical_data:
            historical_ratios[stmt.year] = self._calculate_financial_ratios(stmt)
        
        # Generate AI analysis
        analysis_text = await self._generate_ai_analysis(
            historical_data, projections, key_metrics, trends, strength_assessment
        )
        
        # Compile all metrics
        all_metrics = {
            'key_metrics': key_metrics,
            'trends': trends,
            'strength_assessment': strength_assessment,
            'historical_ratios': historical_ratios,
            'projection_confidence': projections[0].confidence_level if projections else 'low'
        }
        
        # Create analysis object
        analysis = FinancialAnalysis(
            company_id=company_id,
            case_id=case_id,
            historical_data=historical_data,
            projections=projections,
            key_metrics=all_metrics,
            analysis_text=analysis_text,
            generated_at=datetime.now()
        )
        
        return analysis


# Utility function for API endpoints
async def analyze_company_financials(
    company_id: str,
    historical_data: List[Dict[str, Any]],
    case_id: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze company financials and return comprehensive analysis"""
    
    try:
        # Convert dict data to FinancialStatement objects
        statements = []
        for data in historical_data:
            stmt = FinancialStatement(**data)
            statements.append(stmt)
        
        if not statements:
            return {
                'success': False,
                'error': 'No valid financial statements provided'
            }
        
        # Generate analysis
        analyzer = FinancialAnalyzer()
        analysis = await analyzer.generate_comprehensive_analysis(
            company_id=company_id,
            historical_data=statements,
            case_id=case_id
        )
        
        return {
            'success': True,
            'analysis': analysis.dict(),
            'summary': {
                'years_analyzed': len(statements),
                'projection_years': len(analysis.projections),
                'financial_strength': analysis.key_metrics.get('strength_assessment', {}).get('assessment', 'Unknown'),
                'risk_level': analysis.key_metrics.get('strength_assessment', {}).get('risk_level', 'Unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing company financials: {e}")
        return {
            'success': False,
            'error': str(e)
        }