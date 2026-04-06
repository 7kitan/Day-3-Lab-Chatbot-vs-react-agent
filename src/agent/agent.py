import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.core.movie_api import movie_api
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
        System prompt for ReAct-style agent.
        Instructs agent to follow Thought-Action-Observation format.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""You are an intelligent movie booking assistant. You have access to the following tools:

{tool_descriptions}

Follow this format strictly:
Thought: What do I need to do? What information do I need from the user?
Action: tool_name(argument1, argument2, ...)
Observation: [Result from tool execution]

Use the tools to find movies based on user's preferences (genre, date, etc).
Continue until you have helpful information to answer the user's question.

Final Answer: Provide a clear, helpful response with the movie options found."""

    def run(self, user_input: str) -> str:
        """
        Execute the ReAct loop.
        1. Generate Thought + Action
        2. Parse and execute Action
        3. Append Observation
        4. Repeat until Final Answer
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        self.history = [{"role": "user", "content": user_input}]
        steps = 0
        full_response = ""

        while steps < self.max_steps:
            # Get LLM response with system prompt
            result = self.llm.generate(
                prompt=current_prompt,
                system_prompt=self.get_system_prompt()
            )
            
            response_text = result["content"]
            full_response += response_text
            
            logger.log_event("AGENT_STEP", {
                "step": steps,
                "response_len": len(response_text),
                "tokens_used": result["usage"]["total_tokens"]
            })
            
            # Check if we have Final Answer
            if "Final Answer:" in response_text:
                final_answer = response_text.split("Final Answer:")[-1].strip()
                logger.log_event("AGENT_END", {"steps": steps, "status": "completed"})
                return final_answer
            
            # Parse Action from response
            action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response_text)
            
            if action_match:
                tool_name = action_match.group(1)
                args_str = action_match.group(2)
                
                # Execute tool
                observation = self._execute_tool(tool_name, args_str)
                
                # Append observation to prompt for next iteration
                current_prompt = f"""{full_response}

Observation: {observation}

Continue with your next Thought and Action, or provide a Final Answer."""
            else:
                # No valid action found, ask for clarification
                current_prompt = f"""{full_response}

I couldn't understand the action format. Please follow the format:
Action: tool_name(arguments)

Try again:"""
            
            steps += 1
        
        logger.log_event("AGENT_END", {"steps": steps, "status": "max_steps_reached"})
        return f"I've reached the maximum number of steps ({self.max_steps}). Here's what I found:\n\n{full_response}"

    def _execute_tool(self, tool_name: str, args_str: str) -> str:
        """
        Execute tools by name.
        Supports: search_movies, find_by_genre, get_details
        """
        try:
            # Parse arguments - handle both string and dict formats
            args = args_str.strip().strip("'\"")
            
            if tool_name == "search_movies":
                # Handle: search_movies(query, year=2024)
                # Simple parsing for query and optional year
                parts = [p.strip() for p in args.split(",")]
                query = parts[0].strip("'\"")
                year = None
                
                if len(parts) > 1 and "=" in parts[1]:
                    year_str = parts[1].split("=")[1].strip()
                    try:
                        year = int(year_str)
                    except ValueError:
                        pass
                
                result = movie_api.search_movies(query, year)
                
                if result["status"] == "success":
                    formatted = movie_api.format_search_results(result["results"], limit=5)
                    return f"Found {result['total_results']} movies:\n{formatted}"
                else:
                    return f"Error searching movies: {result.get('message', 'Unknown error')}"
            
            elif tool_name == "find_by_genre":
                # Handle: find_by_genre(genre_id, date)
                parts = [p.strip() for p in args.split(",")]
                try:
                    genre_id = int(parts[0].strip("'\""))
                    date = parts[1].strip("'\"") if len(parts) > 1 else None
                except (ValueError, IndexError):
                    return "Invalid arguments for find_by_genre"
                
                result = movie_api.get_movies_by_genre(genre_id, date)
                
                if result["status"] == "success":
                    formatted = movie_api.format_search_results(result["results"], limit=5)
                    return f"Found {result['total_results']} movies in this genre:\n{formatted}"
                else:
                    return f"Error finding movies: {result.get('message', 'Unknown error')}"
            
            elif tool_name == "get_details":
                # Handle: get_details(movie_id)
                try:
                    movie_id = int(args_str.strip("'\""))
                except ValueError:
                    return f"Invalid movie ID: {args_str}"
                
                result = movie_api.get_movie_details(movie_id)
                
                if result["status"] == "success":
                    movie = result["movie"]
                    details = f"""
Title: {movie.get('title', 'N/A')}
Release Date: {movie.get('release_date', 'N/A')}
Rating: {movie.get('vote_average', 'N/A')}/10
Runtime: {movie.get('runtime', 'N/A')} minutes
Overview: {movie.get('overview', 'No description available')}
"""
                    return details
                else:
                    return f"Error getting details: {result.get('message', 'Unknown error')}"
            
            else:
                return f"Tool '{tool_name}' not found. Available tools: search_movies, find_by_genre, get_details"
        
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return f"Error executing tool: {str(e)}"

    def get_provider_info(self):
        """
        Get information about the LLM provider.
        """
        info = self.llm.get_provider_info()
        print(f"Model: {info['model']}")          # Tên model
        print(f"Provider: {info['provider']}")    # Class name (OpenAIProvider, GeminiProvider, etc)
        print(f"Type: {info['type']}")            # Loại: openai, gemini, local, groq
        return info
