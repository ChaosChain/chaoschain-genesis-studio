"""
Genesis Studio - Validator Agent (Bob)

This agent demonstrates a Validator Agent role in the ERC-8004 ecosystem.
It validates market analysis reports and provides scoring through the
Genesis Studio validation framework.
"""

import json
import random
from datetime import datetime
from typing import Dict, Any
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from rich import print as rprint

from .base_agent_genesis import GenesisBaseAgent

class ValidationInput(BaseModel):
    """Input model for validation analysis"""
    analysis_data: dict = Field(description="Market analysis data to validate")
    validation_criteria: str = Field(description="Specific validation criteria to apply")

class GenesisValidationTool(BaseTool):
    """Enhanced validation tool for Genesis Studio"""
    name: str = "genesis_validation"
    description: str = "Validates market analysis reports with comprehensive scoring"
    args_schema: type[BaseModel] = ValidationInput
    
    def _run(self, analysis_data: dict, validation_criteria: str) -> str:
        """
        Perform comprehensive validation of market analysis
        """
        
        # Extract key components for validation
        symbol = analysis_data.get("symbol", "Unknown")
        technical_analysis = analysis_data.get("technical_analysis", {})
        price_analysis = analysis_data.get("price_analysis", {})
        recommendations = analysis_data.get("recommendations", {})
        
        # Validation scoring components
        validation_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "validated_symbol": symbol,
            "validation_criteria": validation_criteria,
            "scoring_breakdown": {
                "data_completeness": self._score_data_completeness(analysis_data),
                "technical_accuracy": self._score_technical_accuracy(technical_analysis),
                "price_reasonableness": self._score_price_reasonableness(price_analysis),
                "recommendation_quality": self._score_recommendation_quality(recommendations),
                "methodology_soundness": self._score_methodology(analysis_data)
            },
            "detailed_assessment": {
                "strengths": [],
                "weaknesses": [],
                "recommendations_for_improvement": []
            },
            "genesis_studio_metadata": {
                "validator_version": "1.0.0",
                "validation_methodology": "Multi-factor quantitative assessment",
                "confidence_in_validation": 0.95
            }
        }
        
        # Calculate detailed scores
        scores = validation_result["scoring_breakdown"]
        
        # Data completeness assessment
        if scores["data_completeness"] >= 90:
            validation_result["detailed_assessment"]["strengths"].append("Comprehensive data coverage")
        elif scores["data_completeness"] < 70:
            validation_result["detailed_assessment"]["weaknesses"].append("Incomplete data analysis")
        
        # Technical accuracy assessment
        if scores["technical_accuracy"] >= 85:
            validation_result["detailed_assessment"]["strengths"].append("Sound technical analysis methodology")
        elif scores["technical_accuracy"] < 70:
            validation_result["detailed_assessment"]["weaknesses"].append("Technical analysis needs improvement")
            validation_result["detailed_assessment"]["recommendations_for_improvement"].append("Enhance technical indicator analysis")
        
        # Price reasonableness assessment
        if scores["price_reasonableness"] >= 80:
            validation_result["detailed_assessment"]["strengths"].append("Realistic price projections")
        elif scores["price_reasonableness"] < 60:
            validation_result["detailed_assessment"]["weaknesses"].append("Price projections may be unrealistic")
            validation_result["detailed_assessment"]["recommendations_for_improvement"].append("Calibrate price targets with market conditions")
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        validation_result["overall_score"] = round(overall_score)
        
        # Add qualitative assessment
        if overall_score >= 90:
            validation_result["quality_rating"] = "Excellent"
            validation_result["validation_summary"] = "High-quality analysis meeting professional standards"
        elif overall_score >= 80:
            validation_result["quality_rating"] = "Good"
            validation_result["validation_summary"] = "Solid analysis with minor areas for improvement"
        elif overall_score >= 70:
            validation_result["quality_rating"] = "Acceptable"
            validation_result["validation_summary"] = "Adequate analysis with some notable weaknesses"
        else:
            validation_result["quality_rating"] = "Needs Improvement"
            validation_result["validation_summary"] = "Analysis requires significant enhancement"
        
        return json.dumps(validation_result, indent=2)
    
    def _score_data_completeness(self, analysis_data: dict) -> float:
        """Score the completeness of the analysis data"""
        
        required_sections = [
            "price_analysis", "technical_analysis", "sentiment_analysis", 
            "recommendations", "genesis_studio_metadata"
        ]
        
        present_sections = sum(1 for section in required_sections if section in analysis_data)
        base_score = (present_sections / len(required_sections)) * 100
        
        # Bonus points for detailed subsections
        bonus = 0
        if "technical_analysis" in analysis_data:
            tech_analysis = analysis_data["technical_analysis"]
            if "support_levels" in tech_analysis and "resistance_levels" in tech_analysis:
                bonus += 5
            if "moving_averages" in tech_analysis:
                bonus += 3
        
        return min(100, base_score + bonus)
    
    def _score_technical_accuracy(self, technical_analysis: dict) -> float:
        """Score the technical analysis accuracy"""
        
        if not technical_analysis:
            return 0
        
        score = 70  # Base score for having technical analysis
        
        # Check for key indicators
        if "rsi" in technical_analysis:
            rsi = technical_analysis["rsi"]
            if 0 <= rsi <= 100:  # Valid RSI range
                score += 10
        
        if "support_levels" in technical_analysis and "resistance_levels" in technical_analysis:
            score += 15
        
        if "moving_averages" in technical_analysis:
            score += 10
        
        # Randomize slightly to simulate real validation variance
        score += random.uniform(-5, 5)
        
        return min(100, max(0, score))
    
    def _score_price_reasonableness(self, price_analysis: dict) -> float:
        """Score the reasonableness of price analysis"""
        
        if not price_analysis:
            return 0
        
        score = 75  # Base score
        
        # Check for current price
        if "current_price" in price_analysis:
            score += 10
        
        # Check for volume data
        if "volume_24h" in price_analysis:
            score += 8
        
        # Check for market cap
        if "market_cap" in price_analysis:
            score += 7
        
        # Randomize slightly
        score += random.uniform(-3, 3)
        
        return min(100, max(0, score))
    
    def _score_recommendation_quality(self, recommendations: dict) -> float:
        """Score the quality of trading recommendations"""
        
        if not recommendations:
            return 0
        
        score = 60  # Base score
        
        # Check for risk assessment
        if "risk_level" in recommendations:
            score += 15
        
        # Check for entry/exit points
        if "entry_points" in recommendations and "exit_targets" in recommendations:
            score += 20
        
        # Check for timeframe-specific recommendations
        if "short_term" in recommendations and "medium_term" in recommendations:
            score += 10
        
        # Randomize slightly
        score += random.uniform(-2, 2)
        
        return min(100, max(0, score))
    
    def _score_methodology(self, analysis_data: dict) -> float:
        """Score the overall methodology soundness"""
        
        score = 80  # Base score for structured approach
        
        # Check for metadata indicating methodology
        metadata = analysis_data.get("genesis_studio_metadata", {})
        if "methodology" in metadata:
            score += 10
        
        if "confidence_score" in metadata:
            score += 5
        
        if "data_sources" in metadata:
            score += 5
        
        # Randomize slightly
        score += random.uniform(-3, 3)
        
        return min(100, max(0, score))

class GenesisValidatorAgent(GenesisBaseAgent):
    """Enhanced Validator Agent for Genesis Studio"""
    
    def __init__(self, agent_domain: str, wallet_address: str, wallet_manager=None):
        super().__init__(agent_domain, wallet_address, wallet_manager)
        
        # Initialize CrewAI components
        self._setup_crewai_agent()
        
        rprint(f"[green]🔍 Genesis Validator Agent (Bob) initialized[/green]")
        rprint(f"[blue]   Domain: {self.agent_domain}[/blue]")
        rprint(f"[blue]   Wallet: {self.address}[/blue]")
    
    def _setup_crewai_agent(self):
        """Setup the CrewAI agent for validation"""
        
        # Create the validation tool
        self.validation_tool = GenesisValidationTool()
        
        # Create the CrewAI agent
        self.crew_agent = Agent(
            role="Senior Market Analysis Validator",
            goal="Provide thorough and accurate validation of market analysis reports",
            backstory="""You are a senior validator at Genesis Studio with over 15 years of 
            experience in financial markets and quantitative analysis. You specialize in 
            validating market research reports, ensuring they meet professional standards 
            for accuracy, completeness, and methodological soundness. Your validations are 
            trusted by institutions and individual traders alike.""",
            tools=[self.validation_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def validate_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate analysis data using CrewAI (supports both market analysis and smart shopping)
        
        Args:
            analysis_data: The analysis data to validate
            
        Returns:
            Dictionary containing validation results and score
        """
        
        # Detect data type and set appropriate validation criteria
        if "shopping_result" in analysis_data:
            # Smart Shopping Validation
            item_type = analysis_data.get("shopping_result", {}).get("item_type", "Unknown")
            validated_item = item_type  # Set this for consistent variable naming
            rprint(f"[yellow]🔍 Validating smart shopping results for {item_type}...[/yellow]")
            
            validation_task = Task(
                description=f"""
                Perform a comprehensive validation of the smart shopping results for {item_type} with the following criteria:
                
                1. Search Completeness:
                   - Verify all required product information is present
                   - Check for comprehensive coverage of user requirements
                   
                2. Price Accuracy:
                   - Validate price calculations and premium logic
                   - Assess base price vs final price reasonableness
                   - Review premium tolerance adherence
                   
                3. Preference Matching:
                   - Evaluate color preference handling
                   - Assess fallback options when preferences unavailable
                   - Review auto-purchase eligibility logic
                   
                4. Merchant Information:
                   - Verify merchant details completeness
                   - Assess availability and delivery information
                   - Review deal quality assessment
                   
                5. Methodology Assessment:
                   - Review overall shopping algorithm approach
                   - Assess search methodology and decision logic
                   - Evaluate transparency and user constraint adherence
                   
                Provide a detailed scoring breakdown with specific feedback and an overall score out of 100.
                """,
                expected_output="A comprehensive JSON-formatted validation report with scoring",
                agent=self.crew_agent
            )
        else:
            # Market Analysis Validation (fallback)
            symbol = analysis_data.get("symbol", "Unknown")
            validated_item = symbol  # Set this for consistent variable naming
            rprint(f"[yellow]🔍 Validating market analysis for {symbol}...[/yellow]")
            
            validation_task = Task(
                description=f"""
                Perform a comprehensive validation of the market analysis for {symbol} with the following criteria:
                
                1. Data Completeness:
                   - Verify all required sections are present
                   - Check for comprehensive coverage of market factors
                   
                2. Technical Accuracy:
                   - Validate technical indicator calculations
                   - Assess support/resistance level reasonableness
                   - Review moving average analysis
                   
                3. Price Analysis Quality:
                   - Evaluate current price data accuracy
                   - Assess volume and market cap information
                   - Review price change calculations
                   
                4. Recommendation Soundness:
                   - Evaluate risk assessment quality
                   - Review entry/exit point recommendations
                   - Assess timeframe-specific guidance
                   
                5. Methodology Assessment:
                   - Review overall analytical approach
                   - Assess confidence scores and data sources
                   - Evaluate transparency and reproducibility
                   
                Provide a detailed scoring breakdown with specific feedback and an overall score out of 100.
                """,
                expected_output="A comprehensive JSON-formatted validation report with scoring",
                agent=self.crew_agent
            )
        
        # Create crew and execute
        crew = Crew(
            agents=[self.crew_agent],
            tasks=[validation_task],
            verbose=True
        )
        
        try:
            # Execute the validation
            result = crew.kickoff()
            
            # Parse the result
            if isinstance(result, str):
                try:
                    validation_data = json.loads(result)
                except json.JSONDecodeError:
                    # Fallback to tool-generated validation
                    validation_data = json.loads(self.validation_tool._run(
                        analysis_data, 
                        "Comprehensive market analysis validation"
                    ))
            else:
                # Fallback to tool-generated validation
                validation_data = json.loads(self.validation_tool._run(
                    analysis_data, 
                    "Comprehensive market analysis validation"
                ))
            
            # Add Genesis Studio metadata
            validation_data.update({
                "genesis_studio": {
                    "validator_id": self.agent_id,
                    "validator_domain": self.agent_domain,
                    "validation_timestamp": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            })
            
            score = validation_data.get("overall_score", 85)
            quality = validation_data.get("quality_rating", "Good")
            
            rprint(f"[green]✅ Validation completed for {symbol}[/green]")
            rprint(f"[blue]   Score: {score}/100 ({quality})[/blue]")
            
            return validation_data
            
        except Exception as e:
            rprint(f"[red]❌ Validation failed: {e}[/red]")
            
            # Fallback to direct tool execution
            rprint("[yellow]🔄 Using fallback validation method...[/yellow]")
            fallback_result = self.validation_tool._run(
                analysis_data, 
                "Comprehensive market analysis validation"
            )
            validation_data = json.loads(fallback_result)
            
            # Add Genesis Studio metadata
            validation_data.update({
                "genesis_studio": {
                    "validator_id": self.agent_id,
                    "validator_domain": self.agent_domain,
                    "validation_timestamp": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "fallback_mode": True
                }
            })
            
            return validation_data
    
    def get_validation_summary(self, validation_data: Dict[str, Any]) -> str:
        """Get a human-readable summary of the validation"""
        
        score = validation_data.get("overall_score", "Unknown")
        quality = validation_data.get("quality_rating", "Unknown")
        validated_item = validation_data.get("validated_symbol", "Unknown")
        
        return f"{validated_item} Validation: {score}/100 ({quality})"
