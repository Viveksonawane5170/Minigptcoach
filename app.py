from flask import Flask, render_template, request, redirect, url_for, flash
from services.palm_service import generate_coaching_prompt
from services.firebase_service import save_user_profile, save_prompt_feedback
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Update the index route to pass empty dicts:
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Validate required fields
            if not all([request.form.get('sport'), request.form.get('level')]):
                flash('Please fill all required fields', 'error')
                return redirect(url_for('index'))
            
            # Create user profile
            user_profile = {
                'sport': request.form.get('sport'),
                'level': request.form.get('level'),
                'goals': request.form.getlist('goals'),
                'preferences': {
                    'motivational_style': request.form.get('motivational_style', 'encouraging'),
                    'length': request.form.get('length', 'medium')
                },
                'created_at': datetime.now().isoformat()
            }
            
            # Save profile (will work even without Firebase)
            try:
                profile_ref = save_user_profile(user_profile)
                profile_id = profile_ref.id if hasattr(profile_ref, 'id') else 'local'
            except Exception as e:
                profile_id = 'local'
                flash('Note: Coaching not being saved to database', 'warning')
            
            # Generate prompt
            prompt = generate_coaching_prompt(user_profile)
            
            return render_template('results.html',
                       prompt=prompt,
                       profile_id=profile_id,
                       sport_name=user_profile['sport'].replace('_', ' ').title())

        
        except Exception as e:
            flash(f'Error generating prompt: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return render_template('index.html',
                         sports={},  # Will be handled in template
                         goals=[])   # Will be handled in template

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        profile_id = request.form.get('profile_id')
        feedback_value = request.form.get('feedback')
        
        if profile_id and profile_id != 'local':
            save_prompt_feedback(profile_id, feedback_value)
            flash('Thank you for your feedback!', 'success')
        else:
            flash('Feedback recorded locally', 'info')
            
    except Exception as e:
        flash(f'Error saving feedback: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')