import json
import os
import inspect
from typing import Dict, Any, List, Optional
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools as DuckDuckGo
from .planner import Planner

class MCPToolDiscovery:
    """Simulates an MCP Server that provides 'Best Practices' for agent tools."""
    def get_tool_definitions(self, task_type: str) -> str:
        """Returns the 'Best Practice' code pattern for a given task type."""
        # This acts as an MCP Resource Provider
        patterns = {
            "search": "Use DDGS to find information. Return structured dictionaries.",
            "compare": "Identify key metrics (price, features) and return a sorted JSON list.",
            "automate": "Use requests to simulate interaction or fetch API data."
        }
        return patterns.get(task_type.lower(), "Write clean, self-contained Python functions.")

class Orchestrator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Ensure the key is available for the Agno Agents
        os.environ["OPENAI_API_KEY"] = api_key
        
        # The ARCHITECT: An autonomous agent instead of just a prompt.
        self.architect_agent = Agent(
            name="Meta-Architect",
            role="Expert Systems Designer & Programmer",
            description="You architect multi-agent systems. You manifest ACTUAL EXECUTABLE PYTHON CODE.",
            instructions=[
                "Use MCPToolDiscovery to find implementation logic.",
                "ALWAYS generate LITERAL Python source code in the 'full_code' field.",
                "DO NOT provide descriptions or summaries. Provide the actual functions and classes.",
                "Strictly follow the JSON schema: {'tools': [{'name': '..', 'code': '..'}], 'full_code': '...', 'ui_schema': []}"
            ],
            tools=[MCPToolDiscovery().get_tool_definitions],
            markdown=True
        )
        self.planner = Planner(api_key)
        self.tools: Dict[str, Any] = {}
        self.ui_schema: List[Dict[str, Any]] = []

    def architect(self, task: str) -> Dict[str, Any]:
        """Architects the tools and UI using an autonomous reasoning loop."""
        # Step 1: Design the Initial Strategy
        plan_data = self.planner.create_plan(task)
        
        # Step 2: The Architect uses its own agentic loop to manifest the manifestation
        # It discovers best practices (MCP) and then generates the JSON
        agent_mission = f"""
        Mission: {plan_data.get('mission')}
        Framework: {plan_data.get('framework')}
        Architecture Strategy: {plan_data.get('execution_strategy')}
        
        Your task is to manifest the tools and the full Python source code for this system.
        Manifest it as a valid JSON object with: 'tools', 'full_code', and 'ui_schema'.
        """
        
        # Autonomous execution instead of static prompt
        res = self.architect_agent.run(agent_mission)
        
        # Robust JSON extraction and recovery
        content = res.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        data = json.loads(content[json_start:json_end], strict=False)
        
        # Recovery: If data is a string (double encoded), parse it again
        if isinstance(data, str):
            data = json.loads(data, strict=False)
        
        self.ui_schema = data["ui_schema"]
        self.full_source_code = data.get("full_code", "# No code generated")

        # Register tools for local execution
        for t in data["tools"]:
            local_env = {}
            try:
                exec(t["code"], local_env)
                self.tools[t["name"]] = local_env[t["name"]]
            except Exception as e:
                print(f"Error compiling tool {t['name']}: {e}")

        return {
            "mission": plan_data.get("mission"),
            "agents": plan_data.get("agents"),
            "tasks": plan_data.get("tasks"),
            "ui_schema": self.ui_schema,
            "full_code": self.full_source_code,
            "framework": plan_data.get("framework")
        }

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the specialized agents sequentially through the tasks."""
        results = {}
        context = inputs.copy()  # Shared memory for agents

        # Sort tasks by step
        sorted_tasks = sorted(self.tasks, key=lambda x: x.get("step", 0))

        for task in sorted_tasks:
            # Each task uses one or more tools owned by its agent
            step_tools = task.get("tools", [])
            task_results = {}
            
            for tool_name in step_tools:
                func = self.tools.get(tool_name)
                if not func:
                    continue
                
                # Automatically extract valid arguments from context
                sig = inspect.signature(func)
                valid_args = {k: v for k, v in context.items() if k in sig.parameters}
                
                try:
                    output = func(**valid_args)
                    task_results[tool_name] = output
                    # Feed output back into context for next agent
                    if isinstance(output, dict):
                        context.update(output)
                    else:
                        context[f"{tool_name}_output"] = str(output)
                except Exception as e:
                    task_results[tool_name] = {"error": str(e)}

            results[task["name"]] = task_results

        return results

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Utility to call a single tool."""
        func = self.tools.get(tool_name)
        if not func:
            return f"Tool {tool_name} not found"
        
        sig = inspect.signature(func)
        valid_args = {k: v for k, v in args.items() if k in sig.parameters}
        return func(**valid_args)
