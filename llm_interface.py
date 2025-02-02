from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import openai
from dataclasses import dataclass
import random

@dataclass
class LLMResponse:
    """Data class to standardize LLM responses across different providers."""
    text: str
    raw_response: Any  # Original response from the LLM
    metadata: Optional[Dict[str, Any]] = None

class LLMInterface(ABC):
    """Abstract base class for LLM implementations."""
    
    @abstractmethod
    def initialize(self, **kwargs):
        """Initialize the LLM with necessary credentials and configuration."""
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response for the given prompt."""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that the credentials and configuration are valid."""
        pass

class MockLLM(LLMInterface):
    """Mock implementation of LLMInterface for testing purposes."""
    
    def __init__(self):
        self.initialized = False
        self.mock_responses = [
            "This article discusses advancements in artificial intelligence and its applications in various industries. "
            "The content emphasizes the importance of responsible AI development and ethical considerations. "
            "Based on the user profile, the most relevant aspects are the practical applications in business and technology sectors.",
            
            "The main focus of this piece is on sustainable energy solutions and environmental conservation. "
            "It presents several innovative approaches to reducing carbon emissions and promoting renewable energy sources. "
            "Given the user's interests, the economic implications and technological innovations are particularly noteworthy.",
            
            "This resource covers recent developments in digital transformation and cloud computing. "
            "It highlights how businesses are adapting to remote work environments and implementing new technologies. "
            "Considering the user's background, the sections on implementation strategies and cost-benefit analysis are most relevant."
        ]
    
    def initialize(self, **kwargs):
        """Mock initialization - always succeeds."""
        self.initialized = True
    
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a mock response."""
        if not self.initialized:
            raise RuntimeError("MockLLM not initialized. Call initialize() first.")
        
        # Randomly select a pre-written response
        response_text = random.choice(self.mock_responses)
        
        # Create metadata dictionary
        metadata = {
            'model': 'mock-llm',
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 150),
            'finish_reason': 'mock_complete'
        }
        
        return LLMResponse(
            text=response_text,
            raw_response={'mock': True},
            metadata=metadata
        )
    
    def validate_credentials(self) -> bool:
        """Mock validation - always returns True."""
        return True

class ChatGPTLLM(LLMInterface):
    """Concrete implementation of LLMInterface for ChatGPT."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.client = None
    
    def initialize(self, **kwargs):
        """Initialize the OpenAI client with API key."""
        self.api_key = kwargs.get('api_key', self.api_key)
        if not self.api_key:
            raise ValueError("API key is required for ChatGPT initialization")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI()
    
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using ChatGPT."""
        if not self.client:
            raise RuntimeError("ChatGPT client not initialized. Call initialize() first.")
        
        try:
            # Get optional parameters with defaults
            temperature = kwargs.get('temperature', 0.3)
            max_tokens = kwargs.get('max_tokens', 300)
            
            # Create the ChatGPT request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Create metadata dictionary
            metadata = {
                'model': self.model,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'finish_reason': response.choices[0].finish_reason
            }
            
            return LLMResponse(
                text=response_text,
                raw_response=response,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"Error generating response from ChatGPT: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate the API key by making a minimal API call."""
        try:
            if not self.api_key:
                return False
            
            # Make a minimal API call to verify credentials
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except:
            return False

class LLMFactory:
    """Factory class for creating LLM instances."""
    
    @staticmethod
    def create_llm(llm_type: str, **kwargs) -> LLMInterface:
        """
        Create and return an instance of the specified LLM type.
        
        Args:
            llm_type: String identifier for the LLM type (e.g., "chatgpt", "mock")
            **kwargs: Additional arguments to pass to the LLM constructor
        
        Returns:
            An initialized instance of the specified LLM
        """
        llm_map = {
            "chatgpt": ChatGPTLLM,
            "mock": MockLLM
        }
        
        llm_class = llm_map.get(llm_type.lower())
        if not llm_class:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
        
        llm = llm_class(**kwargs)
        llm.initialize(**kwargs)
        return llm

# Example usage:
if __name__ == "__main__":
    # Example of how to use the LLM interface
    try:
        # Create a ChatGPT instance using the factory
        llm = LLMFactory.create_llm(
            "chatgpt",
            api_key="your-api-key-here",
            model="gpt-3.5-turbo"
        )
        
        # Generate a response
        response = llm.generate_response(
            "What is the capital of France?",
            temperature=0.7,
            max_tokens=150
        )
        
        print(f"Response: {response.text}")
        print(f"Metadata: {response.metadata}")
        
    except Exception as e:
        print(f"Error: {str(e)}") 