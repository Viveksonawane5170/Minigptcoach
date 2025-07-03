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

PROMPT_TEMPLATE = """
As an expert {sport} coach, create a comprehensive coaching message for a {level} athlete with these goals: {goals}.

Structure your response with these sections:

1. **Motivational Boost** (3-4 sentences):
- Start with powerful inspiration
- Connect emotionally with athlete's aspirations
- Use {motivational_style} tone
- Build confidence and determination

2. **Technical Mastery** (3 specific tips):
- Focus on proper form/technique
- Include {sport}-specific insights
- Make each tip actionable and clear

3. **Training Plan**:
- Recommend a specific workout/drill
- Include duration, intensity, frequency
- Explain how it targets their goals

4. **Final Inspiration**:
- Leave them with a memorable phrase
- Connect to long-term success
- End with a call to action

Tone: {motivational_style}
Length: {length} (approximately 10-15 sentences)
"""

FALLBACK_PROMPTS = {
    'running': {
        'motivational': [
            "Every mile you run is a step toward a stronger you. The discomfort you feel today is building the endurance you'll celebrate tomorrow. Remember, champions aren't born - they're made through consistent effort like yours!",
            "Running isn't just about moving your feet; it's about moving your limits. Each time you push through when it gets tough, you're rewriting what's possible for yourself. The road may be long, but so is your determination!"
        ],
        'technical': [
            "1. Maintain a slight forward lean from ankles, not waist\n2. Land mid-foot with quick, light steps\n3. Keep arms at 90 degrees, swinging front-to-back",
            "1. Breathe rhythmically (inhale 2 steps, exhale 2 steps)\n2. Relax shoulders and unclench hands\n3. Increase stride rate to 170-180 steps per minute"
        ],
        'training': [
            "Try 4x800m intervals at 5K pace with 400m recovery jogs. This builds both speed and endurance effectively.",
            "Do a progression run: 10 min easy, 20 min moderate, 10 min strong. Teaches pacing and finishing strong."
        ]
    },
    'weight_training': {
        'motivational': [
            "The weights don't care how tired you are, but they do respect consistency. Every rep is depositing strength into your future self's bank account. Stay focused - your breakthrough is coming!",
            "Strength isn't just about muscles - it's about mindset. When you challenge yourself under that bar, you're building mental toughness that spills into every area of life. Keep showing up!"
        ],
        'technical': [
            "1. Brace core before every lift\n2. Control both lifting and lowering phases\n3. Keep joints aligned during movement",
            "1. Maintain neutral spine position\n2. Exhale during exertion, inhale during release\n3. Focus on mind-muscle connection"
        ],
        'training': [
            "For strength: 5 sets of 5 reps at 80% 1RM with 3 min rest between sets.",
            "For hypertrophy: 4 sets of 8-12 reps at 70% 1RM with 60 sec rest."
        ]
    }
}

def generate_coaching_prompt(user_profile):
    if PALM_AVAILABLE and os.getenv('PALM_API_KEY'):
        try:
            llm = GooglePalm(
                google_api_key=os.getenv('PALM_API_KEY'),
                temperature=0.8,
                max_output_tokens=1024,
                top_k=50,
                top_p=0.95
            )
            
            prompt = PromptTemplate(
                template=PROMPT_TEMPLATE,
                input_variables=['sport', 'level', 'goals', 'length', 'motivational_style']
            )
            
            chain = LLMChain(llm=llm, prompt=prompt)
            
            response = chain.run({
                'sport': user_profile['sport'],
                'level': user_profile['level'],
                'goals': ", ".join(user_profile['goals']),
                'length': user_profile['preferences'].get('length', 'detailed'),
                'motivational_style': user_profile['preferences'].get('motivational_style', 'encouraging')
            })
            
            return format_response(response)
        except Exception as e:
            print(f"AI generation failed: {e}")
            return generate_fallback_prompt(user_profile)
    
    return generate_fallback_prompt(user_profile)

def format_response(response):
    """Format the AI response for better readability"""
    sections = {
        'Motivational Boost': '',
        'Technical Mastery': '',
        'Training Plan': '',
        'Final Inspiration': ''
    }
    
    # Simple formatting if sections are detected
    for section in sections:
        if f"{section}:" in response:
            sections[section] = response.split(f"{section}:")[1].split("\n\n")[0].strip()
    
    if any(sections.values()):
        formatted = ""
        for title, content in sections.items():
            if content:
                formatted += f"<h4>{title}</h4>\n<p>{content}</p>\n\n"
        return formatted.strip()
    return response  # Return as-is if formatting fails

def generate_fallback_prompt(user_profile):
    """Generate comprehensive fallback content"""
    sport = user_profile.get('sport', 'running')
    level = user_profile.get('level', 'intermediate')
    style = user_profile.get('preferences', {}).get('motivational_style', 'encouraging')
    
    prompts = FALLBACK_PROMPTS.get(sport, FALLBACK_PROMPTS['running'])
    
    # Select based on level and style
    motivational_idx = hash(level + style) % len(prompts['motivational'])
    technical_idx = hash(level) % len(prompts['technical'])
    training_idx = hash(level) % len(prompts['training'])
    
    return f"""
    <h4>Motivational Boost</h4>
    <p>{prompts['motivational'][motivational_idx]}</p>
    
    <h4>Technical Mastery</h4>
    <p>{prompts['technical'][technical_idx]}</p>
    
    <h4>Training Plan</h4>
    <p>{prompts['training'][training_idx]}</p>
    
    <h4>Final Inspiration</h4>
    <p>Stay consistent and trust the process. Your hard work will pay off!</p>
    """