try:
    from langchain_community.llms import GooglePalm
    from langchain_core.prompts import PromptTemplate
    from langchain.chains import LLMChain
    PALM_AVAILABLE = True
except ImportError:
    PALM_AVAILABLE = False

import os
from dotenv import load_dotenv

load_dotenv()

FALLBACK_PROMPTS = {
    'running': [
        "Focus on maintaining a steady cadence around 180 steps per minute.",
        "Remember to keep your posture tall and shoulders relaxed.",
        "Try interval training to improve your speed and endurance."
    ],
    'swimming': [
        "Work on your flip turns to improve your lap times.",
        "Focus on bilateral breathing for better oxygen intake.",
        "Keep your body position horizontal to reduce drag."
    ],
    'cycling': [
        "Maintain a cadence of 80-100 RPM for optimal efficiency.",
        "Use your gears effectively to maintain consistent pedal strokes.",
        "Keep your upper body relaxed while pedaling."
    ],
    'weight_training': [
        "Focus on controlled movements throughout each exercise.",
        "Remember to breathe out during the exertion phase.",
        "Maintain proper form even with lighter weights."
    ]
}

def generate_coaching_prompt(user_profile):
    if PALM_AVAILABLE and os.getenv('PALM_API_KEY'):
        try:
            llm = GooglePalm(
                google_api_key=os.getenv('PALM_API_KEY'),
                temperature=0.7,
                max_output_tokens=512
            )
            
            template = """
            As an expert {sport} coach for {level} athletes,
            create a {length}, {motivational_style} coaching message focused on: {goals}.

            Include:
            1. A motivational statement
            2. One technical tip
            3. One training suggestion
            4. An encouraging note

            Keep it professional but engaging.
            """
            
            prompt = PromptTemplate(
                template=template,
                input_variables=['sport', 'level', 'goals', 'length', 'motivational_style']
            )
            
            chain = LLMChain(llm=llm, prompt=prompt)
            
            response = chain.run({
                'sport': user_profile['sport'],
                'level': user_profile['level'],
                'goals': ", ".join(user_profile['goals']),
                'length': user_profile['preferences'].get('length', 'medium'),
                'motivational_style': user_profile['preferences'].get('motivational_style', 'encouraging')
            })
            
            return response.strip()
        except Exception:
            pass
    
    # Fallback to local prompts
    sport = user_profile.get('sport', 'running')
    prompts = FALLBACK_PROMPTS.get(sport, FALLBACK_PROMPTS['running'])
    return prompts[hash(user_profile.get('level', '')) % len(prompts)]