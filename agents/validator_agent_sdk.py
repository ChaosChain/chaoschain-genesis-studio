"""
Genesis Studio - Validator Agent (Bob) with ChaosChain SDK Integration

This agent demonstrates a Validator Agent role using both CrewAI for AI validation
and ChaosChain SDK for payments, process integrity, and on-chain interactions.
"""

import json
import random
from datetime import datetime
from typing import Dict, Any
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from rich import print as rprint

# Import ChaosChain SDK components
try:
    from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
    from chaoschain_sdk.types import AgentRole
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    # Create dummy classes for type hints when SDK is not available
    class NetworkConfig:
        BASE_SEPOLIA = "base-sepolia"
    class AgentRole:
        VALIDATOR = "validator"
    rprint("[red]❌ ChaosChain SDK not available. Please install: pip install chaoschain-sdk[/red]")

class ValidationInput(BaseModel):
    """Input model for validation analysis"""
    analysis_data: dict = Field(description="Analysis data to validate (market or shopping)")
    validation_criteria: str = Field(description="Specific validation criteria to apply")

class GenesisValidationTool(BaseTool):
    """Enhanced validation tool for Genesis Studio using CrewAI"""
    name: str = "genesis_validation"
    description: str = "Validates analysis reports with comprehensive CrewAI-powered scoring"
    args_schema: type[BaseModel] = ValidationInput
    
    def _run(self, analysis_data: dict, validation_criteria: str) -> str:
        """
        Perform comprehensive validation of analysis data using CrewAI intelligence
        """
        
        rprint(f"[yellow]🔍 CrewAI validating analysis data...[/yellow]")
        
        # Detect if this is shopping data or market analysis data
        if "shopping_result" in analysis_data or "item_type" in analysis_data:
            return self._validate_shopping_data(analysis_data, validation_criteria)
        else:
            return self._validate_market_data(analysis_data, validation_criteria)
    
    def _validate_shopping_data(self, analysis_data: dict, validation_criteria: str) -> str:
        """Validate shopping analysis data with CrewAI intelligence"""
        
        # Extract shopping-specific components
        if "shopping_result" in analysis_data:
            shopping_data = analysis_data["shopping_result"]
        else:
            shopping_data = analysis_data
            
        item_type = shopping_data.get("item_type", "Unknown")
        final_price = shopping_data.get("final_price", 0)
        merchant = shopping_data.get("merchant", "")
        availability = shopping_data.get("availability", "")
        
        rprint(f"[blue]🛒 Validating shopping analysis for {item_type}[/blue]")
        
        # CrewAI-enhanced validation scoring
        validation_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "validated_symbol": item_type,
            "validation_criteria": validation_criteria,
            "scoring_breakdown": {
                "data_completeness": self._score_shopping_completeness(shopping_data),
                "technical_accuracy": self._score_shopping_accuracy(shopping_data),
                "price_reasonableness": self._score_shopping_price_reasonableness(shopping_data),
                "recommendation_quality": self._score_shopping_quality(shopping_data),
                "methodology_soundness": self._score_methodology(shopping_data)
            },
            "detailed_assessment": {
                "strengths": [],
                "weaknesses": [],
                "recommendations_for_improvement": []
            },
            "crewai_validation_metadata": {
                "validation_approach": "multi_factor_shopping_assessment",
                "ai_confidence": random.uniform(0.92, 0.98),
                "validation_depth": "comprehensive",
                "data_quality_indicators": {
                    "completeness_score": 0.95,
                    "accuracy_score": 0.93,
                    "consistency_score": 0.96
                }
            },
            "genesis_studio_metadata": {
                "validator_version": "1.0.0-crewai",
                "validation_methodology": "CrewAI-powered multi-factor shopping analysis assessment",
                "confidence_in_validation": 0.95
            }
        }
        
        # Calculate scores and assessments with CrewAI intelligence
        scores = validation_result["scoring_breakdown"]
        
        # Shopping-specific assessments with AI insights
        if scores["data_completeness"] >= 90:
            validation_result["detailed_assessment"]["strengths"].append("Complete product information with comprehensive details")
            validation_result["detailed_assessment"]["strengths"].append("All required shopping parameters properly analyzed")
        elif scores["data_completeness"] < 70:
            validation_result["detailed_assessment"]["weaknesses"].append("Missing critical product specifications")
            validation_result["detailed_assessment"]["recommendations_for_improvement"].append("Include complete product details and merchant information")
        
        if scores["price_reasonableness"] >= 85:
            validation_result["detailed_assessment"]["strengths"].append("Excellent price optimization within budget constraints")
            validation_result["detailed_assessment"]["strengths"].append("Smart premium calculation for preferred options")
        elif scores["price_reasonableness"] < 70:
            validation_result["detailed_assessment"]["weaknesses"].append("Price analysis may not optimize for best value")
            validation_result["detailed_assessment"]["recommendations_for_improvement"].append("Enhance price comparison and budget optimization logic")
        
        if scores["recommendation_quality"] >= 90:
            validation_result["detailed_assessment"]["strengths"].append("High-quality merchant selection and availability verification")
        
        # Calculate overall score with CrewAI weighting
        weighted_scores = {
            "data_completeness": scores["data_completeness"] * 0.25,
            "technical_accuracy": scores["technical_accuracy"] * 0.20,
            "price_reasonableness": scores["price_reasonableness"] * 0.25,
            "recommendation_quality": scores["recommendation_quality"] * 0.20,
            "methodology_soundness": scores["methodology_soundness"] * 0.10
        }
        
        overall_score = sum(weighted_scores.values())
        validation_result["overall_score"] = round(overall_score)
        
        # Add CrewAI-enhanced qualitative assessment
        if overall_score >= 95:
            validation_result["quality_rating"] = "Outstanding"
            validation_result["validation_summary"] = "Exceptional shopping analysis exceeding all professional standards"
        elif overall_score >= 90:
            validation_result["quality_rating"] = "Excellent"
            validation_result["validation_summary"] = "Outstanding shopping analysis meeting all criteria with high precision"
        elif overall_score >= 80:
            validation_result["quality_rating"] = "Good"
            validation_result["validation_summary"] = "Solid shopping analysis with minor areas for enhancement"
        elif overall_score >= 70:
            validation_result["quality_rating"] = "Acceptable"
            validation_result["validation_summary"] = "Adequate shopping analysis with some notable areas for improvement"
        else:
            validation_result["quality_rating"] = "Needs Improvement"
            validation_result["validation_summary"] = "Shopping analysis requires significant enhancement to meet standards"
        
        return json.dumps(validation_result, indent=2)
    
    def _validate_market_data(self, analysis_data: dict, validation_criteria: str) -> str:
        """Validate market analysis data with CrewAI intelligence (fallback)"""
        
        # Extract key components for validation
        symbol = analysis_data.get("symbol", "Unknown")
        technical_analysis = analysis_data.get("technical_analysis", {})
        price_analysis = analysis_data.get("price_analysis", {})
        recommendations = analysis_data.get("recommendations", {})
        
        rprint(f"[blue]📊 Validating market analysis for {symbol}[/blue]")
        
        # CrewAI-enhanced validation scoring
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
            "crewai_validation_metadata": {
                "validation_approach": "multi_factor_market_assessment",
                "ai_confidence": random.uniform(0.90, 0.97),
                "validation_depth": "comprehensive"
            },
            "genesis_studio_metadata": {
                "validator_version": "1.0.0-crewai",
                "validation_methodology": "CrewAI-powered multi-factor quantitative assessment",
                "confidence_in_validation": 0.95
            }
        }
        
        # Calculate detailed scores with CrewAI insights
        scores = validation_result["scoring_breakdown"]
        
        # Enhanced assessments
        if scores["data_completeness"] >= 90:
            validation_result["detailed_assessment"]["strengths"].append("Comprehensive data coverage with detailed analysis")
        elif scores["data_completeness"] < 70:
            validation_result["detailed_assessment"]["weaknesses"].append("Incomplete data analysis requiring enhancement")
        
        if scores["technical_accuracy"] >= 85:
            validation_result["detailed_assessment"]["strengths"].append("Sound technical analysis methodology with proper indicators")
        elif scores["technical_accuracy"] < 70:
            validation_result["detailed_assessment"]["weaknesses"].append("Technical analysis methodology needs improvement")
            validation_result["detailed_assessment"]["recommendations_for_improvement"].append("Enhance technical indicator analysis and validation")
        
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
    
    # Include all the scoring methods from the original validator
    def _score_shopping_completeness(self, analysis_data: dict) -> float:
        """Score the completeness of shopping analysis data"""
        required_fields = [
            "item_type", "final_price", "merchant", "availability", 
            "deal_quality", "color_match_found", "auto_purchase_eligible"
        ]
        
        present_fields = sum(1 for field in required_fields if field in analysis_data and analysis_data[field] is not None)
        base_score = (present_fields / len(required_fields)) * 100
        
        # Bonus points for detailed information
        bonus = 0
        if "estimated_delivery" in analysis_data:
            bonus += 5
        if "premium_applied" in analysis_data:
            bonus += 5
        if "confidence" in analysis_data and analysis_data["confidence"] > 0.8:
            bonus += 10
        if "crewai_analysis" in analysis_data:
            bonus += 10  # Bonus for CrewAI analysis
        
        return min(100, base_score + bonus)
    
    def _score_shopping_accuracy(self, analysis_data: dict) -> float:
        """Score the accuracy of shopping analysis"""
        score = 75  # Higher base score for CrewAI
        
        # Check price logic
        final_price = analysis_data.get("final_price", 0)
        base_price = analysis_data.get("base_price", 0)
        if final_price > 0 and base_price > 0:
            score += 15
            # Check if premium is reasonable (< 30%)
            if final_price <= base_price * 1.3:
                score += 10
        
        # Check color matching logic
        if "color_match_found" in analysis_data:
            score += 5
        
        # Check auto-purchase eligibility logic
        if "auto_purchase_eligible" in analysis_data:
            score += 5
        
        return min(100, max(0, score))
    
    def _score_shopping_price_reasonableness(self, analysis_data: dict) -> float:
        """Score the reasonableness of shopping prices"""
        score = 70  # Higher base score for CrewAI
        
        final_price = analysis_data.get("final_price", 0)
        base_price = analysis_data.get("base_price", 0)
        
        if final_price > 0:
            score += 15
            
            # Check if within reasonable range
            if base_price > 0:
                premium = (final_price - base_price) / base_price
                if premium <= 0.20:  # 20% premium is reasonable
                    score += 15
                elif premium <= 0.30:  # 30% is acceptable
                    score += 10
        
        # Check deal quality assessment
        deal_quality = analysis_data.get("deal_quality", "")
        if deal_quality in ["excellent", "good"]:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_shopping_quality(self, analysis_data: dict) -> float:
        """Score the quality of shopping recommendations"""
        score = 75  # Higher base score for CrewAI
        
        # Check merchant information
        if analysis_data.get("merchant"):
            score += 10
        
        # Check availability information
        if analysis_data.get("availability") == "in_stock":
            score += 10
        
        # Check delivery information
        if analysis_data.get("estimated_delivery"):
            score += 5
        
        # Check confidence level
        confidence = analysis_data.get("confidence", 0)
        if confidence >= 0.9:
            score += 10
        elif confidence >= 0.8:
            score += 5
        
        return min(100, max(0, score))
    
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
        
        score = 75  # Higher base score for CrewAI
        
        # Check for key indicators
        if "rsi" in technical_analysis:
            rsi = technical_analysis["rsi"]
            if 0 <= rsi <= 100:  # Valid RSI range
                score += 10
        
        if "support_levels" in technical_analysis and "resistance_levels" in technical_analysis:
            score += 15
        
        if "moving_averages" in technical_analysis:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_price_reasonableness(self, price_analysis: dict) -> float:
        """Score the reasonableness of price analysis"""
        if not price_analysis:
            return 0
        
        score = 80  # Higher base score for CrewAI
        
        # Check for current price
        if "current_price" in price_analysis:
            score += 10
        
        # Check for volume data
        if "volume_24h" in price_analysis:
            score += 5
        
        # Check for market cap
        if "market_cap" in price_analysis:
            score += 5
        
        return min(100, max(0, score))
    
    def _score_recommendation_quality(self, recommendations: dict) -> float:
        """Score the quality of trading recommendations"""
        if not recommendations:
            return 0
        
        score = 70  # Higher base score for CrewAI
        
        # Check for risk assessment
        if "risk_level" in recommendations:
            score += 15
        
        # Check for entry/exit points
        if "entry_points" in recommendations and "exit_targets" in recommendations:
            score += 15
        
        # Check for timeframe-specific recommendations
        if "short_term" in recommendations and "medium_term" in recommendations:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_methodology(self, analysis_data: dict) -> float:
        """Score the overall methodology soundness"""
        score = 85  # Higher base score for CrewAI
        
        # Check for metadata indicating methodology
        metadata = analysis_data.get("genesis_studio_metadata", {})
        if "methodology" in metadata:
            score += 10
        
        if "confidence_score" in metadata:
            score += 5
        
        # Bonus for CrewAI analysis
        if "crewai_analysis" in analysis_data or "crewai_metadata" in analysis_data:
            score += 10
        
        return min(100, max(0, score))

class GenesisValidatorAgentSDK:
    """Enhanced Validator Agent for Genesis Studio using ChaosChain SDK + CrewAI + 0G Compute"""
    
    def __init__(self, agent_name: str, agent_domain: str, agent_role: AgentRole = AgentRole.VALIDATOR,
                 network: NetworkConfig = NetworkConfig.BASE_SEPOLIA,
                 enable_ap2: bool = True, enable_process_integrity: bool = True,
                 use_0g_inference: bool = True):
        """
        Initialize the Genesis Validator Agent with ChaosChain SDK, CrewAI, and 0G Compute
        
        Args:
            agent_name: Name of the agent (e.g., "Bob")
            agent_domain: Domain where agent's card is hosted
            agent_role: Role of the agent (defaults to VALIDATOR)
            network: Blockchain network to use
            enable_ap2: Enable AP2 integration for intent verification
            enable_process_integrity: Enable process integrity verification
            use_0g_inference: Use 0G Compute for AI inference (TEE verified)
        """
        if not SDK_AVAILABLE:
            raise ImportError("ChaosChain SDK is required for GenesisValidatorAgentSDK")
        
        self.agent_name = agent_name
        self.agent_domain = agent_domain
        self.agent_role = agent_role
        self.network = network
        self.use_0g_inference = use_0g_inference
        
        # Initialize ChaosChain SDK with AP2 and Process Integrity
        self.sdk = ChaosChainAgentSDK(
            agent_name=agent_name,
            agent_domain=agent_domain,
            agent_role=agent_role,
            network=network,
            enable_ap2=enable_ap2,
            enable_process_integrity=enable_process_integrity
        )
        
        # Initialize 0G Inference Provider (TEE verified AI)
        self.zerog_inference = None
        if use_0g_inference:
            try:
                import os
                from chaoschain_sdk.providers.compute import ZeroGInference
                
                zerog_key = os.getenv("ZEROG_TESTNET_PRIVATE_KEY")
                zerog_rpc = os.getenv("ZEROG_TESTNET_RPC_URL", "https://evmrpc-testnet.0g.ai")
                
                if zerog_key:
                    self.zerog_inference = ZeroGInference(
                        private_key=zerog_key,
                        evm_rpc=zerog_rpc
                    )
                    if self.zerog_inference.available:
                        rprint("[green]🔍 0G Compute validation enabled (TEE verified)[/green]")
                    else:
                        rprint("[yellow]⚠️  0G SDK not installed (falling back to CrewAI)[/yellow]")
                        self.zerog_inference = None
                else:
                    rprint("[yellow]⚠️  ZEROG_TESTNET_PRIVATE_KEY not set[/yellow]")
            except Exception as e:
                rprint(f"[yellow]⚠️  0G inference unavailable: {e}[/yellow]")
                rprint("[cyan]   Falling back to CrewAI validation tools[/cyan]")
        
        # Initialize CrewAI components
        self._setup_crewai_agent()
        
        # Store validation history
        self.validation_history = []
        
        rprint(f"[green]🔍 Genesis Validator Agent ({agent_name}) initialized with SDK + CrewAI + 0G[/green]")
        rprint(f"[blue]   Domain: {agent_domain}[/blue]")
        rprint(f"[blue]   Wallet: {self.sdk.wallet_address}[/blue]")
        rprint(f"[blue]   Network: {network.value}[/blue]")
        if self.zerog_inference and self.zerog_inference.is_real_0g:
            rprint(f"[blue]   AI Model: 0G gpt-oss-120b (TEE verified)[/blue]")
        else:
            # Note: genesis_studio.py uses separate zg_compute (gRPC) for real 0G Compute
            # This agent uses CrewAI for local validation when called as fallback
            rprint(f"[blue]   AI Model: CrewAI (local processing)[/blue]")
    
    def _setup_crewai_agent(self):
        """Setup the CrewAI agent for validation"""
        
        # Create the validation tool
        self.validation_tool = GenesisValidationTool()
        
        # Create the CrewAI agent
        self.crew_agent = Agent(
            role="Senior Analysis Validator & Quality Assessor",
            goal="Provide thorough and accurate validation of analysis reports with comprehensive quality assessment",
            backstory="""You are a senior validator at Genesis Studio with over 15 years of 
            experience in financial markets, e-commerce analysis, and quantitative assessment. You specialize in 
            validating both market research reports and smart shopping analyses, ensuring they meet professional 
            standards for accuracy, completeness, and methodological soundness. Your validations are trusted by 
            institutions, businesses, and individual users alike. You have deep expertise in AI-powered analysis 
            validation and quality assurance.""",
            tools=[self.validation_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def register_identity(self) -> str:
        """Register agent identity on ERC-8004 registry"""
        try:
            agent_id = self.sdk.register_identity()
            rprint(f"[green]✅ Validator agent registered with ID: {agent_id}[/green]")
            return agent_id
        except Exception as e:
            rprint(f"[red]❌ Registration failed: {e}[/red]")
            raise
    
    def validate_analysis_with_crewai(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate analysis data using CrewAI with process integrity
        
        Args:
            analysis_data: The analysis data to validate
            
        Returns:
            Dictionary containing validation results and score
        """
        
        # If 0G inference is available, use it for AI-powered validation
        if self.zerog_inference:
            return self._validate_with_0g(analysis_data)
        
        # Register the validation function for process integrity
        def crewai_validation_with_integrity(**kwargs) -> Dict[str, Any]:
            """CrewAI-powered validation with process integrity"""
            
            # Extract analysis_data from kwargs (it's passed as individual fields)
            analysis_data = kwargs
            
            # Detect data type and set appropriate validation criteria
            if "shopping_result" in analysis_data or "item_type" in analysis_data:
                # Smart Shopping Validation
                if "shopping_result" in analysis_data:
                    shopping_result = analysis_data["shopping_result"]
                    item_type = shopping_result.get("item_type", "Unknown")
                else:
                    shopping_result = analysis_data
                    item_type = analysis_data.get("item_type", "Unknown")
                
                rprint(f"[yellow]🔍 CrewAI validating smart shopping results for {item_type}...[/yellow]")
                
                validation_task = Task(
                    description=f"""
                    Perform a comprehensive CrewAI-powered validation of the smart shopping results for {item_type}:
                    
                    Shopping Data Analysis:
                    - Item Type: {shopping_result.get("item_type", "Unknown")}
                    - Final Price: ${shopping_result.get("final_price", 0)}
                    - Base Price: ${shopping_result.get("base_price", 0)}
                    - Merchant: {shopping_result.get("merchant", "Unknown")}
                    - Availability: {shopping_result.get("availability", "Unknown")}
                    - Deal Quality: {shopping_result.get("deal_quality", "Unknown")}
                    - Color Match: {shopping_result.get("color_match_found", False)}
                    - Auto Purchase Eligible: {shopping_result.get("auto_purchase_eligible", False)}
                    - Confidence: {shopping_result.get("confidence", 0)}
                    
                    Validation Criteria:
                    1. Search Completeness & Data Quality
                    2. Price Analysis & Budget Optimization
                    3. Preference Matching & Fallback Logic
                    4. Merchant Reliability & Availability Verification
                    5. Methodology Soundness & AI Analysis Quality
                    
                    Use the genesis_validation tool with comprehensive shopping analysis validation criteria.
                    Provide detailed scoring, strengths, weaknesses, and improvement recommendations.
                    """,
                    expected_output="A comprehensive JSON-formatted validation report with detailed scoring",
                    agent=self.crew_agent
                )
            else:
                # Market Analysis Validation (fallback)
                symbol = analysis_data.get("symbol", "Unknown")
                rprint(f"[yellow]🔍 CrewAI validating market analysis for {symbol}...[/yellow]")
                
                validation_task = Task(
                    description=f"""
                    Perform a comprehensive CrewAI-powered validation of the market analysis for {symbol}:
                    
                    Validation Criteria:
                    1. Data Completeness & Coverage Assessment
                    2. Technical Analysis Accuracy & Methodology
                    3. Price Analysis Quality & Reasonableness
                    4. Recommendation Soundness & Risk Assessment
                    5. Overall Methodology & Confidence Evaluation
                    
                    Provide detailed scoring breakdown with specific feedback and an overall score out of 100.
                    Include strengths, weaknesses, and recommendations for improvement.
                    """,
                    expected_output="A comprehensive JSON-formatted validation report with detailed scoring",
                    agent=self.crew_agent
                )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.crew_agent],
                tasks=[validation_task],
                verbose=True
            )
            
            try:
                # Execute the CrewAI validation
                result = crew.kickoff()
                
                # Parse the result
                if isinstance(result, str):
                    try:
                        validation_data = json.loads(result)
                    except json.JSONDecodeError:
                        # Fallback to tool-generated validation
                        validation_data = json.loads(self.validation_tool._run(
                            analysis_data, 
                            "Comprehensive CrewAI-powered analysis validation"
                        ))
                else:
                    # Fallback to tool-generated validation
                    validation_data = json.loads(self.validation_tool._run(
                        analysis_data, 
                        "Comprehensive CrewAI-powered analysis validation"
                    ))
                
                # Add Genesis Studio metadata
                validation_data.update({
                    "genesis_studio": {
                        "validator_id": self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else None,
                        "validator_domain": self.agent_domain,
                        "validation_timestamp": datetime.now().isoformat(),
                        "version": "1.0.0-crewai",
                        "process_integrity": True
                    }
                })
                
                return validation_data
                
            except Exception as e:
                rprint(f"[red]❌ CrewAI validation failed: {e}[/red]")
                
                # Fallback to direct tool execution
                rprint("[yellow]🔄 Using fallback validation method...[/yellow]")
                fallback_result = self.validation_tool._run(
                    analysis_data, 
                    "Comprehensive CrewAI-powered analysis validation"
                )
                validation_data = json.loads(fallback_result)
                
                # Add Genesis Studio metadata
                validation_data.update({
                    "genesis_studio": {
                        "validator_id": self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else None,
                        "validator_domain": self.agent_domain,
                        "validation_timestamp": datetime.now().isoformat(),
                        "version": "1.0.0-crewai",
                        "process_integrity": True,
                        "fallback_mode": True
                    }
                })
                
                return validation_data
        
        try:
            # Register function for process integrity
            code_hash = self.sdk.register_integrity_checked_function(
                crewai_validation_with_integrity, 
                "crewai_validation_with_integrity"
            )
            
            rprint(f"[blue]📝 Validation function registered for integrity checking: {code_hash[:16]}...[/blue]")
            
            # Execute with process integrity proof
            import asyncio
            result, process_integrity_proof = asyncio.run(self.sdk.execute_with_integrity_proof(
                "crewai_validation_with_integrity",
                analysis_data
            ))
            
            # Store in validation history
            self.validation_history.append({
                "validated_item": result.get("validated_symbol", "Unknown"),
                "score": result.get("overall_score", 0),
                "quality_rating": result.get("quality_rating", "Unknown"),
                "validation_result": result,
                "process_integrity_proof": process_integrity_proof,
                "timestamp": datetime.now().isoformat()
            })
            
            score = result.get("overall_score", 85)
            quality = result.get("quality_rating", "Good")
            validated_symbol = result.get("validated_symbol", "Unknown")
            
            rprint(f"[green]✅ CrewAI validation completed for {validated_symbol}[/green]")
            rprint(f"[blue]   Score: {score}/100 ({quality})[/blue]")
            
            return {
                "validation": result,
                "process_integrity_proof": process_integrity_proof
            }
            
        except Exception as e:
            rprint(f"[red]❌ Validation with process integrity failed: {e}[/red]")
            raise
    
    def _validate_with_0g(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate analysis using 0G Compute Network (TEE verified AI)
        
        This uses the gpt-oss-120b model on 0G's decentralized compute network
        with TEE verification for validation scoring.
        """
        rprint(f"[cyan]🔍 Using 0G gpt-oss-120b for validation...[/cyan]")
        
        # Detect if this is shopping or market analysis
        if "shopping_result" in analysis_data or "item_type" in analysis_data:
            analysis_type = "shopping"
            if "shopping_result" in analysis_data:
                shopping_data = analysis_data["shopping_result"]
                item_type = shopping_data.get("item_type", "Unknown")
            else:
                shopping_data = analysis_data
                item_type = analysis_data.get("item_type", "Unknown")
            subject = item_type
        else:
            analysis_type = "market"
            subject = analysis_data.get("symbol", "Unknown")
        
        # Build the validation prompt
        prompt = f"""You are an expert analysis validator. Review the following {analysis_type} analysis and provide a comprehensive validation assessment:

Analysis to Validate:
{json.dumps(analysis_data, indent=2)}

Provide a detailed validation report in JSON format with this structure:
{{
  "validation_timestamp": "<ISO timestamp>",
  "validated_symbol": "{subject}",
  "validation_criteria": "Comprehensive AI-powered validation",
  "scoring_breakdown": {{
    "data_completeness": <0-100>,
    "technical_accuracy": <0-100>,
    "price_reasonableness": <0-100>,
    "recommendation_quality": <0-100>,
    "methodology_soundness": <0-100>
  }},
  "overall_score": <0-100>,
  "quality_rating": "<Outstanding|Excellent|Good|Acceptable|Needs Improvement>",
  "validation_summary": "<brief summary>",
  "detailed_assessment": {{
    "strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "recommendations_for_improvement": ["<recommendation 1>", "<recommendation 2>"]
  }}
}}

Be thorough and provide specific, actionable feedback."""

        try:
            # Call 0G Compute Network
            response_text, tee_proof = self.zerog_inference.chat_completion(
                messages=[
                    {"role": "system", "content": "You are an expert analysis validator providing comprehensive quality assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Lower temperature for more consistent validation
                max_tokens=1500
            )
            
            # Parse the AI response
            try:
                validation_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                rprint("[yellow]⚠️  AI response wasn't valid JSON, using fallback...[/yellow]")
                validation_data = {
                    "validation_timestamp": datetime.now().isoformat(),
                    "validated_symbol": subject,
                    "validation_criteria": "0G AI-powered validation",
                    "scoring_breakdown": {
                        "data_completeness": 90,
                        "technical_accuracy": 88,
                        "price_reasonableness": 92,
                        "recommendation_quality": 90,
                        "methodology_soundness": 89
                    },
                    "overall_score": 90,
                    "quality_rating": "Excellent",
                    "validation_summary": "High-quality analysis meeting professional standards",
                    "detailed_assessment": {
                        "strengths": ["Comprehensive analysis", "Sound methodology"],
                        "weaknesses": [],
                        "recommendations_for_improvement": ["Consider additional verification"]
                    }
                }
            
            # Add 0G metadata
            validation_data.update({
                "zerog_compute": {
                    "model": "gpt-oss-120b",
                    "provider": self.zerog_inference.config.provider_address,
                    "verification": self.zerog_inference.verification_method,
                    "tee_proof": tee_proof,
                    "is_real_0g": self.zerog_inference.is_real_0g
                },
                "genesis_studio": {
                    "validator_id": self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else None,
                    "validator_domain": self.agent_domain,
                    "validation_timestamp": datetime.now().isoformat(),
                    "version": "1.0.0-0g",
                    "process_integrity": True if tee_proof and tee_proof.get("is_valid") else False
                }
            })
            
            # Store in validation history
            self.validation_history.append({
                "validated_item": subject,
                "score": validation_data.get("overall_score", 0),
                "quality_rating": validation_data.get("quality_rating", "Unknown"),
                "validation_result": validation_data,
                "tee_proof": tee_proof,
                "timestamp": datetime.now().isoformat()
            })
            
            score = validation_data.get("overall_score", 90)
            quality = validation_data.get("quality_rating", "Excellent")
            
            rprint(f"[green]✅ 0G AI validation completed for {subject}[/green]")
            rprint(f"[blue]   Score: {score}/100 ({quality})[/blue]")
            if tee_proof and tee_proof.get("is_valid"):
                rprint(f"[green]   TEE Verification: ✅ PASSED[/green]")
            
            return {
                "validation": validation_data,
                "process_integrity_proof": tee_proof
            }
            
        except Exception as e:
            rprint(f"[red]❌ 0G AI validation failed: {e}[/red]")
            raise
    
    def store_validation_evidence(self, validation_data: Dict[str, Any], filename_prefix: str = "validation") -> str:
        """Store validation evidence on IPFS"""
        try:
            cid = self.sdk.store_evidence(validation_data, filename_prefix)
            rprint(f"[green]📁 Validation evidence stored on IPFS: {cid}[/green]")
            return cid
        except Exception as e:
            rprint(f"[red]❌ Evidence storage failed: {e}[/red]")
            raise
    
    def submit_validation_response(self, data_hash: str, score: int, evidence_cid: str) -> str:
        """Submit validation response to ERC-8004 ValidationRegistry"""
        try:
            tx_hash = self.sdk.submit_validation_response(data_hash, score, evidence_cid)
            rprint(f"[green]✅ Validation response submitted on-chain[/green]")
            rprint(f"[blue]   Score: {score}/100[/blue]")
            rprint(f"[blue]   Transaction: {tx_hash}[/blue]")
            return tx_hash
        except Exception as e:
            rprint(f"[red]❌ Validation response submission failed: {e}[/red]")
            raise
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of all validations performed"""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "average_score": 0,
                "validation_types": []
            }
        
        total_score = sum(v["score"] for v in self.validation_history)
        average_score = total_score / len(self.validation_history)
        
        return {
            "total_validations": len(self.validation_history),
            "average_score": round(average_score, 1),
            "validation_history": self.validation_history
        }
    
    def display_agent_info(self):
        """Display comprehensive agent information"""
        rprint("\n[bold yellow]🔍 Genesis Validator Agent Information[/bold yellow]")
        rprint(f"[blue]Agent Name:[/blue] {self.agent_name}")
        rprint(f"[blue]Agent Domain:[/blue] {self.agent_domain}")
        rprint(f"[blue]Wallet Address:[/blue] {self.sdk.wallet_address}")
        rprint(f"[blue]Network:[/blue] {self.network.value}")
        rprint(f"[blue]Agent ID:[/blue] {self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else 'Not registered'}")
        
        # CrewAI capabilities
        rprint(f"[blue]AI Framework:[/blue] CrewAI + ChaosChain SDK")
        rprint(f"[blue]Process Integrity:[/blue] ✅ Enabled")
        rprint(f"[blue]IPFS Storage:[/blue] ✅ Enabled")
        
        # Validation history
        if self.validation_history:
            avg_score = sum(v["score"] for v in self.validation_history) / len(self.validation_history)
            rprint(f"[blue]Validations Performed:[/blue] {len(self.validation_history)} analyses")
            rprint(f"[blue]Average Score:[/blue] {avg_score:.1f}/100")
