from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="../static", template_folder="../templates")

USE_CASES_FILE = 'use_cases.json'

def load_use_cases():
    if not os.path.exists(USE_CASES_FILE):
        return []
    with open(USE_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_use_cases(use_cases):
    with open(USE_CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(use_cases, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/use-cases')
def use_cases():
    use_cases = load_use_cases()
    return render_template('use_cases.html', use_cases=use_cases)

@app.route('/use-case/<int:use_case_id>')
def use_case_landing(use_case_id):
    use_cases = load_use_cases()
    if 0 <= use_case_id < len(use_cases):
        use_case = use_cases[use_case_id]
        return render_template('use_case_landing.html', use_case=use_case)
    else:
        return "Use case not found", 404

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        url = request.form.get('url')
        category = request.form.get('category')
        tech_used = request.form.get('tech_used')
        demo_video_url = request.form.get('demo_video_url')
        team_members = request.form.get('team_members')
        success_stories = request.form.get('success_stories')
        logo_url = None
        logo_file = request.files.get('logo_file')
        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            static_dir = os.path.join(os.path.dirname(__file__), '../static/images')
            os.makedirs(static_dir, exist_ok=True)
            logo_path = os.path.join(static_dir, filename)
            logo_file.save(logo_path)
            logo_url = url_for('static', filename=f'images/{filename}')
        if not (title and description and url and category):
            return jsonify({'success': False, 'error': 'All fields required'}), 400
        use_cases = load_use_cases()
        use_cases.append({
            'title': title,
            'description': description,
            'url': url,
            'category': category,
            'tech_used': tech_used,
            'demo_video_url': demo_video_url,
            'team_members': team_members,
            'success_stories': success_stories,
            'logo_url': logo_url
        })
        save_use_cases(use_cases)
        return jsonify({'success': True})
    else:
        use_cases = load_use_cases()
        return render_template('admin.html', use_cases=use_cases)

@app.route('/admin/edit', methods=['POST'])
def edit_use_case():
    index = request.form.get('index')
    if index is None:
        return jsonify({'success': False, 'error': 'Missing index'}), 400
    try:
        index = int(index)
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid index'}), 400
    use_cases = load_use_cases()
    if not (0 <= index < len(use_cases)):
        return jsonify({'success': False, 'error': 'Index out of range'}), 400
    title = request.form.get('title')
    description = request.form.get('description')
    url = request.form.get('url')
    category = request.form.get('category')
    tech_used = request.form.get('tech_used')
    demo_video_url = request.form.get('demo_video_url')
    team_members = request.form.get('team_members')
    success_stories = request.form.get('success_stories')
    logo_url = use_cases[index].get('logo_url')
    logo_file = request.files.get('logo_file')
    remove_logo = request.form.get('remove_logo')
    if remove_logo:
        logo_url = None
    elif logo_file and logo_file.filename:
        filename = secure_filename(logo_file.filename)
        static_dir = os.path.join(os.path.dirname(__file__), '../static/images')
        os.makedirs(static_dir, exist_ok=True)
        logo_path = os.path.join(static_dir, filename)
        logo_file.save(logo_path)
        logo_url = url_for('static', filename=f'images/{filename}')
    if not (title and description and url and category):
        return jsonify({'success': False, 'error': 'All fields required'}), 400
    use_cases[index] = {
        'title': title,
        'description': description,
        'url': url,
        'category': category,
        'tech_used': tech_used,
        'demo_video_url': demo_video_url,
        'team_members': team_members,
        'success_stories': success_stories,
        'logo_url': logo_url
    }
    save_use_cases(use_cases)
    return jsonify({'success': True, 'logo_url': logo_url})

@app.route('/admin/delete', methods=['POST'])
def delete_use_case():
    data = request.get_json()
    index = data.get('index')
    use_cases = load_use_cases()
    try:
        index = int(index)
        if 0 <= index < len(use_cases):
            use_cases.pop(index)
            save_use_cases(use_cases)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid index'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Vercel expects the variable to be named 'app' 