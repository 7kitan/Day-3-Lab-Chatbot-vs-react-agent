import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}

        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        Observation: result of the tool call.
        ... (repeat Thought/Action/Observation if needed)
        Final Answer: your final response.
        """

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            # 1. Generate LLM response
            response_dict = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            result = response_dict.get("content", "")
            
            # 2. Check for Final Answer
            if "Final Answer:" in result:
                final_answer = result.split("Final Answer:")[-1].strip()
                logger.log_event("AGENT_END", {"steps": steps + 1, "success": True})
                return final_answer
                
            # 3. Parse Thought/Action from result
            action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\((.*?)\)", result)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                # Call tool
                observation = self._execute_tool(tool_name, tool_args)
                
                # Append Observation to the prompt for the next iteration
                current_prompt += f"\n{result}\nObservation: {observation}"
            else:
                # If no Action and no Final Answer, guide the LLM back to format
                current_prompt += f"\n{result}\nObservation: Error - Could not find Action or Final Answer. Please follow the correct format."

            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps, "success": False})
        return "Max steps reached without Final Answer."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # Call the corresponding function dynamically if 'func' exists
                func = tool.get('func')
                if callable(func):
                    try:
                        return str(func(args))
                    except Exception as e:
                        return f"Error executing {tool_name}: {str(e)}"
                else:
                    return f"Tool {tool_name} is defined but missing a callable 'func'."
        return f"Tool {tool_name} not found."
