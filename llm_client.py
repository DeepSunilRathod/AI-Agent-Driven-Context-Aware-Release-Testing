# llm_client.py - LLM Integration Layer with Fallback
import os
import json
from datetime import datetime

class LLMClient:
    """
    LLM Client with multiple provider support and fallback to pattern-based generation
    """
    
    def __init__(self, provider="mock", api_key=None):
        """
        Initialize LLM client
        
        Args:
            provider: "openai", "azure", "mock"
            api_key: API key for the provider
        """
        self.provider = provider
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('AZURE_OPENAI_KEY')
        self.response_dir = "llm_responses"
        os.makedirs(self.response_dir, exist_ok=True)
        
        # Initialize provider-specific client
        if self.provider == "openai" and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print(" OpenAI client initialized")
            except:
                print("  OpenAI not available, using mock mode")
                self.provider = "mock"
        elif self.provider == "azure" and self.api_key:
            # Azure OpenAI setup would go here
            print("  Azure OpenAI not configured, using mock mode")
            self.provider = "mock"
        else:
            self.provider = "mock"
            print("  Using mock LLM mode (pattern-based generation)")
    
    def load_prompt_template(self, template_name):
        """Load prompt template from file"""
        template_path = f"prompts/{template_name}.txt"
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise FileNotFoundError(f"Prompt template not found: {template_path}")
    
    def generate_prompt(self, template_name, **parameters):
        """
        Generate prompt by injecting parameters into template
        
        Args:
            template_name: Name of the template file (without .txt)
            **parameters: Parameters to inject into template
            
        Returns:
            Formatted prompt string
        """
        template = self.load_prompt_template(template_name)
        
        # Inject parameters
        try:
            prompt = template.format(**parameters)
            return prompt
        except KeyError as e:
            raise ValueError(f"Missing parameter for template: {e}")
    
    def call_llm(self, prompt, model="gpt-4", temperature=0.3):
        """
        Call LLM with prompt
        
        Args:
            prompt: The prompt to send
            model: Model to use
            temperature: Temperature setting
            
        Returns:
            LLM response
        """
        print(f"\n Calling LLM ({self.provider})...")
        
        if self.provider == "openai":
            return self._call_openai(prompt, model, temperature)
        elif self.provider == "azure":
            return self._call_azure(prompt, model, temperature)
        else:
            return self._call_mock(prompt)
    
    def _call_openai(self, prompt, model, temperature):
        """Call OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert QA test engineer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            return {
                'success': True,
                'response': response.choices[0].message.content,
                'provider': 'openai',
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f" OpenAI call failed: {e}")
            print("   Falling back to mock mode...")
            return self._call_mock(prompt)
    
    def _call_azure(self, prompt, model, temperature):
        """Call Azure OpenAI API"""
        # Azure implementation would go here
        print("  Azure not implemented, using mock")
        return self._call_mock(prompt)
    
    def _call_mock(self, prompt):
        """Mock LLM response (pattern-based)"""
        print("   Using pattern-based generation (no API call)")
        
        # Return a structured response indicating mock mode
        return {
            'success': True,
            'response': None,  # Will be handled by post-processor
            'provider': 'mock',
            'model': 'pattern-based',
            'timestamp': datetime.now().isoformat(),
            'note': 'Using RAG pattern matching instead of LLM'
        }
    
    def save_response(self, response, identifier):
        """Save LLM response to file for learning"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{identifier}_{timestamp}.json"
        filepath = os.path.join(self.response_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        print(f" LLM response saved: {filepath}")
        return filepath
    
    def load_past_responses(self, identifier=None, limit=10):
        """Load past LLM responses for learning"""
        responses = []
        
        if not os.path.exists(self.response_dir):
            return responses
        
        files = sorted(os.listdir(self.response_dir), reverse=True)
        
        for filename in files[:limit]:
            if identifier and not filename.startswith(identifier):
                continue
            
            filepath = os.path.join(self.response_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    responses.append(json.load(f))
            except:
                continue
        
        return responses


# Test
if __name__ == "__main__":
    print("=" * 80)
    print(" LLM CLIENT - TEST")
    print("=" * 80)
    
    # Initialize client
    client = LLMClient(provider="mock")
    
    # Test prompt generation
    try:
        prompt = client.generate_prompt(
            "test_generation_prompt",
            user_story="As a user, I want to login with email and password",
            retrieved_patterns="Pattern 1: Valid login test\nPattern 2: Invalid credentials test"
        )
        
        print("\n Prompt generated successfully")
        print(f"   Length: {len(prompt)} characters")
        
        # Test LLM call
        response = client.call_llm(prompt)
        
        print(f"\n LLM response received")
        print(f"   Provider: {response['provider']}")
        print(f"   Model: {response['model']}")
        
        # Save response
        client.save_response(response, "test")
        
        print("\n LLM client working correctly!")
        
    except Exception as e:
        print(f"\n Error: {e}")
    
    print("=" * 80)