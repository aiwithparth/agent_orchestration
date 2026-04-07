from orchestrator import Orchestrator

class Controller:
    def __init__(self, api_key):
        self.orch = Orchestrator(api_key)

    def build_agent(self, task):
        return self.orch.architect(task)

    def run_agent(self, inputs):
        return self.orch.execute(inputs)

    def run_tool(self, tool_name, args):
        return self.orch.execute_tool(tool_name, args)
