try:
    from langchain_community.llms import GooglePalm
    from langchain_core.prompts import PromptTemplate
    from langchain.chains import LLMChain
    PALM_AVAILABLE = True
except ImportError:
    PALM_AVAILABLE = False

import os
import random
from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATES = [
    """
    As a {level} {sport} performance coach, craft a detailed coaching message for an athlete focused on {goals}.
    
    **MOTIVATIONAL MESSAGE** (7-8 sentences):
    - Start with an inspiring sports quote
    - Connect to their specific aspirations
    - Highlight their potential
    - Address common challenges at their level
    - Share a relevant athlete's story
    - Emphasize the journey over results
    - End with powerful call to action
    - Include a personal mantra
    
    **TECHNICAL MASTERY** (5-6 detailed tips):
    1. Primary technique refinement
    2. Secondary skill development
    3. Common mistake correction
    4. Equipment/form adjustment
    5. Sport-specific strategy
    6. Recovery technique
    
    **TRAINING BLUEPRINT**:
    - This week's focus area
    - Specific drills (3-4 variations)
    - Volume and intensity
    - Recovery protocol
    - Success metrics
    
    **MINDSET DEVELOPMENT**:
    - Daily mental exercise
    - Overcoming plateaus
    - Progress tracking method
    - Community building
    
    Length: Very detailed (15-20 sentences)
    Tone: {motivational_style}
    """,
    """
    Create an exhaustive {sport} coaching guide for {level} athletes targeting {goals}.
    
    **INSPIRATIONAL KICKSTART** (8 sentences):
    1. Opening powerful metaphor
    2. Their current potential
    3. Growth opportunity
    4. Champion's perspective
    5. Process over outcome
    6. Short-term focus
    7. Long-term vision
    8. Final rally cry
    
    **EXPERT TECHNIQUES** (6 professional tips):
    1. Fundamental skill
    2. Advanced technique
    3. Competitive edge
    4. Injury prevention
    5. Equipment optimization
    6. Mental approach
    
    **7-DAY CHALLENGE**:
    - Daily focus areas
    - Progressive overload
    - Active recovery
    - Self-assessment
    
    **PERFORMANCE HACKS**:
    - Pre-activity routine
    - In-the-moment tricks
    - Recovery protocol
    - Progress tracking
    
    Style: {motivational_style}
    Detail: Comprehensive
    """,
    """
    Develop a complete {sport} training manifesto for {level} athletes with {goals} goals.
    
    **POWERFUL MOTIVATION** (8-9 sentences):
    - Story of underdog success
    - Their unique advantages
    - Current opportunity
    - 3 reasons they'll succeed
    - Short inspirational story
    - Growth mindset emphasis
    - Daily commitment reminder
    - Final inspiring thought
    
    **ELITE TECHNIQUES** (6 key areas):
    1. Foundational movement
    2. Skill refinement
    3. Competitive strategy
    4. Mental preparation
    5. Recovery method
    6. Habit formation
    
    **14-DAY TRANSFORMATION**:
    - Phase 1: Foundation (Days 1-4)
    - Phase 2: Intensity (Days 5-9)
    - Phase 3: Performance (Days 10-14)
    - Daily mini-challenges
    - Progress tracking
    
    **CHAMPION'S MINDSET**:
    - Pre-activity ritual
    - In-the-moment focus
    - Post-activity review
    - Weekly reflection
    
    Detail: Extremely thorough
    Tone: {motivational_style}
    """
]

FALLBACK_PROMPTS = {
    'running': {
        'beginner': [
            {
                'motivational': """1. Welcome to the running community! Every great runner started exactly where you are now.
2. The first steps are the hardest, but each one makes you stronger.
3. Don't compare your chapter 1 to someone else's chapter 20 - your journey is unique.
4. Celebrate every run, no matter how short or slow - you're lapping everyone on the couch!
5. Consistency beats intensity - showing up regularly matters more than occasional heroics.
6. Your body is capable of amazing adaptations - trust the process.
7. The discomfort you feel today is building the endurance you'll celebrate tomorrow.
8. Remember: forward is a pace!""",
                'technical': """1. Posture: Run tall like a puppet on a string, slight forward lean from ankles
2. Footstrike: Aim for mid-foot landing under your center of gravity
3. Cadence: Count steps - aim for 160-170 per minute (each foot)
4. Arms: Keep elbows at 90°, swing front to back not across body
5. Breathing: Rhythmic patterns (try 2-step inhale, 2-step exhale)
6. Relaxation: Periodically check for tension in shoulders/face""",
                'training': """Week 1 Plan:
- Monday: 10 min walk, 1 min run/1 min walk x 5, 10 min walk
- Wednesday: 15 min walk, 90 sec run/90 sec walk x 4
- Friday: 20 min walk/run at comfortable ratio
- Sunday: 30 min brisk walk

Focus on time moving, not distance"""
            },
            {
                'motivational': """1. Running is the world's most accessible sport - just you and the open road!
2. The first month is the hardest - push through and you'll discover the joy.
3. Every runner has bad days - they make the good runs feel even better.
4. Your running shoes are tools of transformation - lace them up with purpose.
5. Progress comes in waves - plateaus are normal before breakthroughs.
6. The running community welcomes all paces - you belong here!
7. Bad weather makes you mentally tough - some of the best runs happen in rain.
8. Remember why you started when motivation fades.""",
                'technical': """1. Warm-up: Dynamic moves like leg swings, high knees, butt kicks
2. Cool-down: Walk 5 min + static stretches held 30 sec each
3. Terrain: Start on flat surfaces before tackling hills
4. Shoes: Replace every 300-500 miles to prevent injuries
5. Hydration: Sip water throughout the day, not just when running
6. Form check: Video yourself occasionally to spot inefficiencies""",
                'training': """Beginner Progression:
Week 1: 1 min run/2 min walk x 6
Week 2: 90 sec run/90 sec walk x 6 
Week 3: 2 min run/1 min walk x 6
Week 4: 3 min run/1 min walk x 5

Always start with warm-up and end with cool-down"""
            }
        ],
        'intermediate': [
            {
                'motivational': """1. You've graduated from beginner gains - now the real progress begins!
2. Intermediate runners have the most potential for improvement - this is your sweet spot.
3. Speed work may feel uncomfortable, but it's where breakthroughs happen.
4. Your training log is your roadmap - track diligently to see progress.
5. The magic happens outside your comfort zone - embrace challenging workouts.
6. Nutrition becomes performance fuel at this level - eat with purpose.
7. Recovery is training too - respect rest days as much as workout days.
8. You're now a role model for beginners - run with pride!""",
                'technical': """1. Tempo runs: Learn to sustain "comfortably hard" pace
2. Hill technique: Shorten stride, lift knees, pump arms
3. Speed form: Quick turnover, powerful arm drive
4. Breathing: Practice belly breathing for efficiency
5. Pacing: Use GPS watch or landmarks to maintain even effort
6. Race strategy: Negative splits (faster second half)""",
                'training': """Sample Week:
Mon: Easy 3 miles + strides
Tue: Interval: 6x400m at 5K pace with 400m recovery
Wed: Cross-train or rest
Thu: Tempo: 1 mile easy, 2 miles at threshold, 1 mile easy
Fri: Rest or yoga
Sat: Long run: 6-8 miles easy
Sun: Recovery: 30-45 min walk/swim"""
            }
        ]
    },
    'weight_training': {
        'beginner': [
            {
                'motivational': """1. Welcome to strength training - where every rep rewrites your physical potential!
2. The first 3 months will amaze you - enjoy these "newbie gains."
3. Strength is a skill - focus on perfect form before adding weight.
4. Your future self will thank you for starting today - consistency compounds.
5. Muscle grows during recovery - respect rest days as training days.
6. Progress photos tell the real story - take them monthly.
7. The weights don't care about your excuses - they only respond to effort.
8. You're building more than muscle - you're building discipline.""",
                'technical': """1. Squat: Feet shoulder-width, knees track over toes, depth to parallel
2. Bench: Arch back slightly, grip slightly wider than shoulders
3. Deadlift: Neutral spine, bar close to body, drive through heels
4. Overhead Press: Brace core, press straight up, slight lean back
5. Row: Hinge at hips, pull elbows back, squeeze shoulder blades
6. Core: Learn to brace properly before loading""",
                'training': """Starter Program (3x/week):
A Day:
- Squat 3x5
- Bench 3x5
- Row 3x8
- Plank 3x30sec

B Day:
- Deadlift 3x5
- OHP 3x5
- Lat Pulldown 3x8
- Hanging Knee Raise 3x10

Increase weight by 2.5-5lbs each session"""
            }
        ]
    }
}

def select_template(user_profile):
    """Select template based on input variety"""
    input_str = f"{user_profile['sport']}{user_profile['level']}{''.join(user_profile['goals'])}{user_profile['preferences']['motivational_style']}"
    input_hash = hash(input_str)
    return PROMPT_TEMPLATES[input_hash % len(PROMPT_TEMPLATES)]

def generate_coaching_prompt(user_profile):
    if PALM_AVAILABLE and os.getenv('PALM_API_KEY'):
        try:
            llm = GooglePalm(
                google_api_key=os.getenv('PALM_API_KEY'),
                temperature=1.0,  # Maximum creativity
                max_output_tokens=2048,  # Double length
                top_k=60,
                top_p=0.99
            )
            
            template = select_template(user_profile)
            
            prompt = PromptTemplate(
                template=template,
                input_variables=['sport', 'level', 'goals', 'length', 'motivational_style']
            )
            
            chain = LLMChain(llm=llm, prompt=prompt)
            
            response = chain.run({
                'sport': user_profile['sport'],
                'level': user_profile['level'],
                'goals': ", ".join(user_profile['goals']),
                'length': 'very detailed',
                'motivational_style': user_profile['preferences'].get('motivational_style', 'encouraging')
            })
            
            return format_response(response, user_profile)
        except Exception as e:
            print(f"AI generation failed: {e}")
            return generate_fallback_prompt(user_profile)
    
    return generate_fallback_prompt(user_profile)

def format_response(response, user_profile):
    """Enhanced formatting with dynamic sections"""
    # Convert markdown-style headers to HTML
    formatted = response.replace('**', '</strong>').replace('**', '<strong>')
    formatted = formatted.replace('\n\n', '</p><p>')
    formatted = f"""
    <div class='coaching-plan {user_profile["sport"]}-plan {user_profile["level"]}-level'>
        <p>{formatted}</p>
    </div>
    """
    return formatted

def generate_fallback_prompt(user_profile):
    """Generate comprehensive fallback content"""
    sport = user_profile.get('sport', 'running')
    level = user_profile.get('level', 'beginner')
    goals = user_profile.get('goals', [])
    style = user_profile.get('preferences', {}).get('motivational_style', 'encouraging')
    
    prompts = FALLBACK_PROMPTS.get(sport, {}).get(level, FALLBACK_PROMPTS['running']['beginner'])
    
    if not prompts:
        prompts = FALLBACK_PROMPTS['running']['beginner']
    
    # Select based on goals and style for variety
    selection_idx = hash(tuple(goals) + (style,)) % len(prompts)
    selected = prompts[selection_idx]
    
    return f"""
    <div class='fallback-plan {sport}-plan {level}-level'>
        <h4>Powerful Motivation</h4>
        <p>{selected['motivational']}</p>
        
        <h4>Expert Techniques</h4>
        <p>{selected['technical']}</p>
        
        <h4>Training Plan</h4>
        <p>{selected['training']}</p>
    </div>
    """