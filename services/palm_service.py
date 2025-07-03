import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
GEMINI_AVAILABLE = False
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

def generate_coaching_prompt(user_profile):
    if not GEMINI_AVAILABLE:
        return generate_fallback_response(user_profile)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Create a comprehensive {user_profile['sport']} training plan for a {user_profile['level']} athlete with these goals: {', '.join(user_profile['goals'])}.
        
        The response should include:
        1. Motivational message (inspiring and personalized)
        2. Technical tips (specific to their level and goals)
        3. Training plan (structured and progressive)
        4. Mindset advice (to overcome challenges)
        
        Use a {user_profile['preferences']['motivational_style']} tone and keep it {user_profile['preferences']['length']} in length.
        """
        
        response = model.generate_content(prompt)
        return format_response(response.text, user_profile)
    except Exception as e:
        print(f"Gemini generation failed: {e}")
        return generate_fallback_response(user_profile)

def format_response(response, user_profile):
    """Format the Gemini response with HTML"""
    formatted = f"""
    <div class='coaching-plan {user_profile["sport"]}-plan {user_profile["level"]}-level'>
        <p>{response.replace('\n', '</p><p>')}</p>
    </div>
    """
    return formatted

def generate_fallback_response(user_profile):
    """Simple fallback if Gemini fails"""
    return f"""
    <div class='coaching-plan {user_profile["sport"]}-plan {user_profile["level"]}-level'>
        <p>Our AI coach is currently unavailable. Here's some general advice:</p>
        <p>As a {user_profile['level']} {user_profile['sport']} athlete, focus on consistent practice and gradual improvement in your {', '.join(user_profile['goals'])}. 
        Remember that progress takes time - celebrate small wins along the way!</p>
    </div>
    """