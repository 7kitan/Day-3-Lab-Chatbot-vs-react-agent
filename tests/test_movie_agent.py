import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.groq_provider import GroqProvider
from src.agent.agent import ReActAgent

def create_movie_agent(provider_type: str = "groq"):
    """
    Create a ReAct agent for movie booking.
    
    Args:
        provider_type: "openai", "gemini", or "groq"
    
    Returns:
        ReActAgent instance with movie search tools
    """
    
    # Define movie search tools
    tools = [
        {
            "name": "search_movies",
            "description": "Search movies by title or keywords. Usage: search_movies(query, year=2024)"
        },
        {
            "name": "find_by_genre",
            "description": "Find movies by genre ID and date. Usage: find_by_genre(genre_id, date='YYYY-MM-DD')"
        },
        {
            "name": "get_details",
            "description": "Get detailed information about a specific movie. Usage: get_details(movie_id)"
        }
    ]
    
    # Initialize provider based on type
    if provider_type.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or "your_" in api_key:
            print("❌ Error: OPENAI_API_KEY not set correctly in .env")
            return None
        llm = OpenAIProvider(model_name="gpt-4o", api_key=api_key)
    
    elif provider_type.lower() == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "your_" in api_key:
            print("❌ Error: GEMINI_API_KEY not set correctly in .env")
            return None
        llm = GeminiProvider(api_key=api_key)
    
    elif provider_type.lower() == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or "your_" in api_key:
            print("❌ Error: GROQ_API_KEY not set correctly in .env")
            return None
        model_name = os.getenv("DEFAULT_MODEL", "qwen/qwen3-32b")
        llm = GroqProvider(model_name=model_name, api_key=api_key)
    
    else:
        print(f"❌ Unknown provider: {provider_type}")
        return None
    
    # Create and return agent
    agent = ReActAgent(
        llm=llm,
        tools=tools,
        max_steps=5
    )
    
    return agent


def test_movie_agent():
    """
    Test the movie booking agent with sample queries.
    """
    load_dotenv()
    
    print("🎬 Movie Booking Agent - Demo\n")
    print("=" * 60)
    
    # Get provider from .env or environment variable, default to groq
    provider = os.getenv("DEFAULT_PROVIDER", "groq").lower()
    
    # Validate API key is set
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "")
    else:
        api_key = ""
    
    if not api_key or "your_" in api_key:
        print(f"❌ Error: API key for {provider.upper()} not configured in .env")
        print(f"\nAvailable providers:")
        print("  - openai (set OPENAI_API_KEY)")
        print("  - gemini (set GEMINI_API_KEY)")
        print("  - groq (set GROQ_API_KEY)")
        return
    
    print(f"Using provider: {provider.upper()}")
    
    agent = create_movie_agent(provider_type=provider)
    if not agent:
        print("Failed to initialize agent.")
        return
    
    # Test queries
    test_queries = [
        "Find me a scary movie released on 2024-01-15",
        "Search for action movies from 2024",
        "I want to watch a superhero movie, what do you recommend?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"User: {query}")
        print("-" * 60)
        
        try:
            response = agent.run(query)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()


if __name__ == "__main__":
    test_movie_agent()
