import json
import os
from typing import Dict, Any, List
from agno.agent import Agent

class MCPMissionDiscovery:
    """Simulates an MCP Server that provides 'Strategic Blueprints' for missions."""
    def get_mission_patterns(self, mission_type: str) -> str:
        """Returns the 'Strategic Blueprint' for a given mission type."""
        blueprints = {
            "flight": "Step 1: Discover sites. Step 2: Map parameters. Step 3: Compare results.",
            "research": "Step 1: Scrape data. Step 2: Extract findings. Step 3: Summarize report.",
            "automation": "Step 1: Identify triggers. Step 2: Run loop. Step 3: Format output."
        }
        return blueprints.get(mission_type.lower(), "Design a robust, multi-agent operational flow.")

class Planner:
    def __init__(self, api_key: str):
        # Ensure key is available for the Strategy Architect
        os.environ["OPENAI_API_KEY"] = api_key

        # THE STRATEGY ARCHITECT: A highly technical mission designer.
        self.strategy_agent = Agent(
            name="Strategy-Architect",
            role="Expert Multi-Agent Workflow Architect",
            description="""
            You design deep, functional automation blueprints. 
            DO NOT provide generic or short descriptions.
            Each task's 'description' must technically detail how data is being transformed and what logic is applied. 
            Tools names must be precise and functional (e.g. 'mmt_expedia_search_aggregator').
            Always aim for production-grade technical detail.
            """,
            tools=[MCPMissionDiscovery().get_mission_patterns],
            markdown=True
        )

    def create_plan(self, task: str) -> Dict[str, Any]:
        """Designs a structured multi-agent configuration using an agentic loop."""
        
        agent_mission = f"""
        Objective: {task}
        
        Design a detailed mission plan.
        Output MUST be a valid JSON with:
        {{
            "mission": "String",
            "framework": "String",
            "execution_strategy": "String",
            "agents": [
                {{"name": "String", "role": "String", "goal": "String", "tools": ["List of strings"]}}
            ],
            "tasks": [
                {{"step": 1, "name": "String", "agent": "String", "description": "Technical field", "tools": ["List"]}}
            ]
        }}
        """

        # Autonomous execution
        res = self.strategy_agent.run(agent_mission)
        
        # Robust JSON extraction and recovery
        content = res.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        data = json.loads(content[json_start:json_end], strict=False)
        
        # Recovery
        if isinstance(data, str):
            data = json.loads(data, strict=False)
        return data
