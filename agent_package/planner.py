import json
import os
from openai import OpenAI
from typing import Dict, Any, List

class Planner:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def create_plan(self, task: str) -> Dict[str, Any]:
        """
        Analyzes the prompt to generate a structured multi-agent configuration.
        Follows a pattern similar to professional agent generators.
        """
        system_prompt = """
        You are an expert at designing Advanced Agentic Flows.
        Based on the task, you must:
        1. Dynamically select the best Framework (Agno, LangGraph, AutoGen, CrewAI).
        2. Plan a team of specialized, functional agents.

        Framework Selection Guide:
        - Agno: Perfect for tool-heavy, fast interactive agents with clear states.
        - LangGraph: Best for complex, cyclic/graphical workflows with state management.
        - AutoGen: Ideal for highly autonomous, conversational multi-agent systems.
        - CrewAI: Best for structured, process-driven role-based execution.

        Format your response as JSON:
        {
            "mission": "Automation objective",
            "framework": "Agno | LangGraph | AutoGen | CrewAI",
            "execution_strategy": "A professional justification for the chosen framework and the multi-agent logic.",
            "agents": [
                {
                    "name": "agent_name",
                    "role": "Functional operator",
                    "goal": "What data it produces",
                    "tools": ["tool_v1"]
                }
            ],
            "tasks": [
                {
                    "step": 1,
                    "name": "Task Name",
                    "description": "Functional transformation description",
                    "agent": "agent_name",
                    "tools": ["tool_v1"]
                }
            ]
        }
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ],
            response_format={"type": "json_object"}
        )

        plan = json.loads(response.choices[0].message.content)
        return plan
