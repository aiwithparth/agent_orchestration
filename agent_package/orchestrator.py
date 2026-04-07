import json
import os
import inspect
from typing import Dict, Any, List, Optional
from openai import OpenAI
from planner import Planner

class Orchestrator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.planner = Planner(api_key)
        self.tools: Dict[str, Any] = {}
        self.ui_schema: List[Dict[str, Any]] = []
        self.mission: str = ""
        self.agents: List[Dict[str, Any]] = []
        self.tasks: List[Dict[str, Any]] = []

    def architect(self, task: str) -> Dict[str, Any]:
        """Architects the tools and UI for a specialized agent team."""
        # Step 1: Design the Multi-Agent Plan (Roles, Goals, Workflow)
        plan_data = self.planner.create_plan(task)
        self.mission = plan_data.get("mission", "Custom Agent Mission")
        self.agents = plan_data.get("agents", [])
        self.tasks = plan_data.get("tasks", [])
        
        # Step 2: Extract all tool names that need creation
        all_tools_needed = set()
        for agent in self.agents:
            all_tools_needed.update(agent.get("tools", []))
        
        # Step 3: Generate logic for all tools and a UI form for the initial step
        prompt = f"""
        Mission: {self.mission}
        Selected Framework: {plan_data.get('framework', 'Agno')}

        Create a 100% FUNCTIONAL, SELF-CONTAINED Python script using ONLY the '{plan_data.get('framework', 'Agno')}' framework.
        
        CRITICAL RULES:
        1. NO MOCK DATA: Use real tools like `duckduckgo_search` or standard libraries (math, json).
        2. IDIOMATIC LINKING: 
           - If AGNO: Assign functions directly to `Agent(tools=[...])`.
           - If CREWAI: Assign agents to `Task(agent=..., context=[...])` to link them.
           - If LANGGRAPH: Define nodes that use `model.bind_tools(...)` or custom tool calling.
        3. COMPLETE FLOW: The script must include a high-level `run_professional_mission(inputs)` function that kicks off the entire team.
        4. SINGLE FRAMEWORK: Do not include code for frameworks other than '{plan_data.get('framework', 'Agno')}'.

        REQUIRED CODE STRUCTURE for {plan_data.get('framework', 'Agno')}:
        - All necessary imports (including `agno` classes or `crewai`).
        - Specialized Tool Definitions (real Python functions).
        - Agent/Team Initialization (linking the tools).
        - Orchestration Logic (handling input -> final report).

        Return JSON:
        {{
          "tools": [
            {{ "name": "...", "code": "def ...(input): ...", "desc": "..." }}
          ],
          "full_code": "A beautiful, complete, {plan_data.get('framework', 'Agno')}-native script.",
          "ui_schema": [
            {{ "label": "Start City", "name": "origin", "type": "text", "tool": "first_tool" }}
          ]
        }}
        """

        res = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a software engineer building real, JIT-coded agent tools."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        data = json.loads(res.choices[0].message.content)
        self.ui_schema = data["ui_schema"]
        self.full_source_code = data.get("full_code", "# No code generated")

        # Register tools for execution
        for t in data["tools"]:
            local_env = {}
            try:
                exec(t["code"], local_env)
                self.tools[t["name"]] = local_env[t["name"]]
            except Exception as e:
                print(f"Error compiling tool {t['name']}: {e}")

        return {
            "mission": self.mission,
            "agents": self.agents,
            "tasks": self.tasks,
            "ui_schema": self.ui_schema,
            "full_code": self.full_source_code,
            "framework": plan_data.get("framework", "Agno")
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
