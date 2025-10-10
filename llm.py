from google import genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GOOGLE_AI_API_KEY")
client = genai.Client(api_key=api_key)

class LLM:
    def __init__(self, model="gemini-2.0-flash-exp"):
        self.model = model
        self.mental_health_instructions = """
        You are a compassionate and professional mental health assistant. Your role is to:
        
        1. Provide supportive, empathetic responses to users' mental health concerns
        2. Use the user's fitness and health data to provide personalized advice
        3. Encourage healthy habits and positive lifestyle changes
        4. Recognize when users might need professional help and suggest appropriate resources
        5. Maintain confidentiality and non-judgmental attitude
        
        Guidelines:
        - Always be supportive and understanding
        - Use the user's workout history, diet logs, and water intake data to provide context-aware advice
        - Encourage physical activity as it relates to mental wellness
        - Suggest mindfulness, meditation, or relaxation techniques when appropriate
        - If user expresses serious mental health concerns (suicidal thoughts, severe depression), recommend seeking professional help
        - Keep responses conversational but professional
        - Ask follow-up questions to better understand the user's situation
        
        Remember: You are not a replacement for professional mental health treatment, but a supportive companion on their wellness journey.
        """

    def generate_content(self, contents, user_data=None, conversation_history=None):
        """
        Generate content with mental health context
        
        Args:
            contents: User query
            user_data: User's fitness and health data
            conversation_history: Previous conversation messages
        """
        try:
            # Build context-aware prompt
            prompt = self._build_mental_health_prompt(contents, user_data, conversation_history)
            
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."
    
    def _build_mental_health_prompt(self, user_query, user_data=None, conversation_history=None):
        """
        Build a comprehensive prompt for mental health assistance
        """
        prompt_parts = [self.mental_health_instructions]
        
        # Add user data context if available
        if user_data:
            prompt_parts.append(f"\nUser's Health Data Context:\n{json.dumps(user_data, indent=2)}")
        
        # Add conversation history if available
        if conversation_history and len(conversation_history) > 0:
            prompt_parts.append("\nPrevious Conversation:")
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                if msg.get('role') == 'user':
                    prompt_parts.append(f"User: {msg.get('query', '')}")
                elif msg.get('role') == 'assistant':
                    prompt_parts.append(f"Assistant: {msg.get('response', '')}")
        
        # Add current user query
        prompt_parts.append(f"\nCurrent User Query: {user_query}")
        prompt_parts.append("\nPlease provide a helpful, empathetic response as a mental health assistant:")
        

        return "\n".join(prompt_parts)
