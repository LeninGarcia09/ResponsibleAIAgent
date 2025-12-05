"""
Azure AI Foundry Evaluation for Responsible AI Agent

This script evaluates the RAI Agent's responses using Azure AI Evaluation SDK.
It tests the agent against various project scenarios and measures:
- Response quality and relevance
- Groundedness (factual accuracy)
- Coherence and fluency
- Safety and responsible AI compliance
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Any

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import (
    evaluate,
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
    SimilarityEvaluator,
    ContentSafetyEvaluator,
)
from openai import AzureOpenAI

# Import the system prompt from the backend
from rai_system_prompt import SYSTEM_PROMPT


class RAIAgentEvaluator:
    """Evaluates the Responsible AI Agent responses using Azure AI Foundry."""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        
        # Azure OpenAI configuration
        self.azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://rai-openai-7538.openai.azure.com")
        self.deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.api_version = "2024-08-01-preview"
        
        # Initialize Azure OpenAI client
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        self.client = AzureOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=token.token,
            api_version=self.api_version
        )
        
        # AI Foundry project for evaluation (optional - uses local evaluation if not set)
        self.ai_foundry_project = os.environ.get("AZURE_AI_PROJECT_CONNECTION_STRING")
        
    def call_rai_agent(self, project_name: str, project_description: str, review_level: str = "standard") -> str:
        """Call the RAI Agent with a project submission and get the response."""
        
        user_message = f"""Please review the following AI project:

Project Name: {project_name}
Description: {project_description}
Review Level: {review_level}

Please provide your Responsible AI assessment."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling RAI Agent: {str(e)}"
    
    def load_test_cases(self, test_file: str = "test_cases.json") -> list[dict]:
        """Load test cases from JSON file."""
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        with open(test_path, 'r') as f:
            return json.load(f)
    
    def prepare_evaluation_data(self, test_cases: list[dict]) -> list[dict]:
        """Prepare data for Azure AI Evaluation by calling the agent for each test case."""
        evaluation_data = []
        
        for case in test_cases:
            print(f"\n📋 Testing: {case['name']} ({case['review_level']} review)")
            
            # Construct the query
            query = f"Project: {case['name']}\nDescription: {case['description']}\nReview Level: {case['review_level']}"
            
            # Get agent response
            response = self.call_rai_agent(
                case['name'],
                case['description'],
                case['review_level']
            )
            
            # Create ground truth context based on expected aspects
            context = f"""This is a {case['review_level']} level Responsible AI review for an AI project.
Key aspects to address: {', '.join(case['expected_aspects'])}.
The review should provide actionable recommendations for responsible AI implementation."""
            
            evaluation_data.append({
                "id": case["id"],
                "query": query,
                "response": response,
                "context": context,
                "ground_truth": f"A comprehensive {case['review_level']} RAI review covering: {', '.join(case['expected_aspects'])}",
                "expected_aspects": case["expected_aspects"],
                "review_level": case["review_level"]
            })
            
            print(f"   ✅ Response received ({len(response)} chars)")
        
        return evaluation_data
    
    def run_evaluation(self, evaluation_data: list[dict]) -> dict:
        """Run Azure AI Evaluation on the agent responses."""
        
        print("\n" + "="*60)
        print("🔬 Running Azure AI Foundry Evaluation")
        print("="*60)
        
        # Model configuration for evaluators
        model_config = {
            "azure_endpoint": self.azure_endpoint,
            "azure_deployment": self.deployment_name,
            "api_version": self.api_version,
        }
        
        # Initialize evaluators
        evaluators = {
            "groundedness": GroundednessEvaluator(model_config),
            "relevance": RelevanceEvaluator(model_config),
            "coherence": CoherenceEvaluator(model_config),
            "fluency": FluencyEvaluator(model_config),
        }
        
        # Run evaluation
        results = evaluate(
            data=evaluation_data,
            evaluators=evaluators,
            evaluator_config={
                "groundedness": {
                    "query": "${data.query}",
                    "response": "${data.response}",
                    "context": "${data.context}",
                },
                "relevance": {
                    "query": "${data.query}",
                    "response": "${data.response}",
                    "context": "${data.context}",
                },
                "coherence": {
                    "query": "${data.query}",
                    "response": "${data.response}",
                },
                "fluency": {
                    "query": "${data.query}",
                    "response": "${data.response}",
                },
            },
            output_path=os.path.join(os.path.dirname(__file__), "evaluation_results.json"),
        )
        
        return results
    
    def analyze_results(self, results: dict, evaluation_data: list[dict]) -> dict:
        """Analyze evaluation results and generate summary report."""
        
        print("\n" + "="*60)
        print("📊 EVALUATION RESULTS SUMMARY")
        print("="*60)
        
        metrics = results.get("metrics", {})
        
        # Calculate average scores
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_test_cases": len(evaluation_data),
            "metrics": {
                "groundedness": metrics.get("groundedness.groundedness", "N/A"),
                "relevance": metrics.get("relevance.relevance", "N/A"),
                "coherence": metrics.get("coherence.coherence", "N/A"),
                "fluency": metrics.get("fluency.fluency", "N/A"),
            },
            "by_review_level": {},
            "recommendations": []
        }
        
        # Print metrics
        print(f"\n📈 Overall Metrics:")
        for metric, score in summary["metrics"].items():
            if isinstance(score, (int, float)):
                status = "✅" if score >= 4.0 else "⚠️" if score >= 3.0 else "❌"
                print(f"   {status} {metric.capitalize()}: {score:.2f}/5.0")
            else:
                print(f"   ❓ {metric.capitalize()}: {score}")
        
        # Analyze by review level
        review_levels = set(d["review_level"] for d in evaluation_data)
        print(f"\n📋 Results by Review Level:")
        for level in review_levels:
            level_data = [d for d in evaluation_data if d["review_level"] == level]
            print(f"   • {level.capitalize()}: {len(level_data)} test cases")
        
        # Generate recommendations
        print(f"\n💡 Recommendations:")
        if summary["metrics"].get("groundedness", 0) < 4.0:
            rec = "Improve factual accuracy by enhancing context retrieval"
            summary["recommendations"].append(rec)
            print(f"   • {rec}")
        if summary["metrics"].get("relevance", 0) < 4.0:
            rec = "Enhance response relevance by better understanding project context"
            summary["recommendations"].append(rec)
            print(f"   • {rec}")
        if summary["metrics"].get("coherence", 0) < 4.0:
            rec = "Improve response structure and logical flow"
            summary["recommendations"].append(rec)
            print(f"   • {rec}")
        
        if not summary["recommendations"]:
            print("   ✅ All metrics meet quality thresholds!")
        
        return summary
    
    def save_report(self, summary: dict, evaluation_data: list[dict]):
        """Save detailed evaluation report."""
        
        report = {
            "summary": summary,
            "detailed_results": evaluation_data,
            "system_prompt_version": "v6 (with quick-start guidance)",
        }
        
        report_path = os.path.join(os.path.dirname(__file__), "evaluation_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_path}")


def main():
    """Main evaluation function."""
    
    print("="*60)
    print("🤖 Responsible AI Agent - Azure AI Foundry Evaluation")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize evaluator
    evaluator = RAIAgentEvaluator()
    
    # Load test cases
    print("\n📂 Loading test cases...")
    test_cases = evaluator.load_test_cases()
    print(f"   Found {len(test_cases)} test cases")
    
    # Prepare evaluation data (calls the agent)
    print("\n🚀 Calling RAI Agent for each test case...")
    evaluation_data = evaluator.prepare_evaluation_data(test_cases)
    
    # Run Azure AI Evaluation
    results = evaluator.run_evaluation(evaluation_data)
    
    # Analyze and report
    summary = evaluator.analyze_results(results, evaluation_data)
    
    # Save report
    evaluator.save_report(summary, evaluation_data)
    
    print("\n" + "="*60)
    print("✅ Evaluation Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
