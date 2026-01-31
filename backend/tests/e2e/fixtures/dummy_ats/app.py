"""Dummy ATS Flask application for E2E testing.

This simulates a Greenhouse/Lever-style job application form
for testing Playwright automation without hitting real sites.

Run with: flask --app tests/e2e/fixtures/dummy_ats/app run -p 5001
"""

from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Track submitted applications for verification
submitted_applications = []

GREENHOUSE_FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Apply - {{ job_title }} | Dummy Corp</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        .error-message { color: red; display: none; }
        .success-message { color: green; display: none; }
    </style>
</head>
<body>
    <h1>Apply for {{ job_title }}</h1>
    <p>Dummy Corp - Remote</p>
    
    <form id="application-form" method="POST" action="/greenhouse/submit" enctype="multipart/form-data">
        <div class="form-group">
            <label for="first_name">First Name *</label>
            <input type="text" id="first_name" name="job_application[first_name]" required>
        </div>
        
        <div class="form-group">
            <label for="last_name">Last Name *</label>
            <input type="text" id="last_name" name="job_application[last_name]" required>
        </div>
        
        <div class="form-group">
            <label for="email">Email *</label>
            <input type="email" id="email" name="job_application[email]" required>
        </div>
        
        <div class="form-group">
            <label for="phone">Phone</label>
            <input type="tel" id="phone" name="job_application[phone]">
        </div>
        
        <div class="form-group">
            <label for="resume">Resume *</label>
            <input type="file" id="resume" name="job_application[resume]" accept=".pdf,.docx">
        </div>
        
        <div class="form-group">
            <label for="cover_letter">Cover Letter</label>
            <textarea id="cover_letter" name="job_application[cover_letter]" rows="5"></textarea>
        </div>
        
        <div class="form-group">
            <label for="linkedin">LinkedIn URL</label>
            <input type="url" id="linkedin" name="job_application[linkedin]" placeholder="https://linkedin.com/in/...">
        </div>
        
        <div class="error-message" id="error-message"></div>
        
        <button type="submit">Submit Application</button>
    </form>
</body>
</html>
"""

LEVER_FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ job_title }} - Lever Demo</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; }
        .application-form { background: #f9f9f9; padding: 30px; border-radius: 8px; }
        .form-field { margin-bottom: 20px; }
        .form-field label { display: block; margin-bottom: 8px; font-weight: 500; }
        .form-field input, .form-field textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        .application-submit { background: #0073b1; color: white; padding: 14px 28px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
    </style>
</head>
<body>
    <h1>{{ job_title }}</h1>
    <p>Lever Demo Company</p>
    
    <div class="application-form">
        <form method="POST" action="/lever/submit" enctype="multipart/form-data">
            <div class="form-field">
                <label>Full Name *</label>
                <input type="text" name="name" required>
            </div>
            
            <div class="form-field">
                <label>Email *</label>
                <input type="email" name="email" required>
            </div>
            
            <div class="form-field">
                <label>Phone</label>
                <input type="tel" name="phone">
            </div>
            
            <div class="form-field">
                <label>Resume/CV *</label>
                <input type="file" name="resume" accept=".pdf,.docx">
            </div>
            
            <div class="form-field">
                <label>Additional Information</label>
                <textarea name="comments" rows="4" placeholder="Cover letter or additional details..."></textarea>
            </div>
            
            <div class="form-field">
                <label>LinkedIn</label>
                <input type="url" name="urls[LinkedIn]" placeholder="https://linkedin.com/in/...">
            </div>
            
            <button type="submit" class="application-submit">Submit Application</button>
        </form>
    </div>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head><title>Application Submitted</title></head>
<body>
    <div class="success-message" style="text-align: center; padding: 50px;">
        <h1>Thank you for applying!</h1>
        <p>Your application has been submitted successfully.</p>
        <p data-testid="success">Application received</p>
    </div>
</body>
</html>
"""


@app.route('/greenhouse/job/<job_id>')
def greenhouse_form(job_id):
    """Render Greenhouse-style application form."""
    return render_template_string(GREENHOUSE_FORM_HTML, job_title=f"Software Engineer (Job {job_id})")


@app.route('/greenhouse/submit', methods=['POST'])
def greenhouse_submit():
    """Handle Greenhouse form submission."""
    data = {
        'source': 'greenhouse',
        'first_name': request.form.get('job_application[first_name]'),
        'last_name': request.form.get('job_application[last_name]'),
        'email': request.form.get('job_application[email]'),
        'phone': request.form.get('job_application[phone]'),
        'cover_letter': request.form.get('job_application[cover_letter]'),
        'linkedin': request.form.get('job_application[linkedin]'),
    }
    submitted_applications.append(data)
    return render_template_string(SUCCESS_HTML)


@app.route('/lever/job/<job_id>')
def lever_form(job_id):
    """Render Lever-style application form."""
    return render_template_string(LEVER_FORM_HTML, job_title=f"Product Manager (Job {job_id})")


@app.route('/lever/submit', methods=['POST'])
def lever_submit():
    """Handle Lever form submission."""
    data = {
        'source': 'lever',
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'comments': request.form.get('comments'),
        'linkedin': request.form.get('urls[LinkedIn]'),
    }
    submitted_applications.append(data)
    return render_template_string(SUCCESS_HTML)


@app.route('/captcha/job/<job_id>')
def captcha_form(job_id):
    """Form with CAPTCHA for testing detection."""
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Apply - Protected Form</h1>
        <iframe src="https://www.google.com/recaptcha/api2/demo"></iframe>
        <div class="g-recaptcha" data-sitekey="test"></div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/api/submissions')
def get_submissions():
    """Get all submitted applications (for test verification)."""
    return jsonify(submitted_applications)


@app.route('/api/clear')
def clear_submissions():
    """Clear submitted applications."""
    submitted_applications.clear()
    return jsonify({'status': 'cleared'})


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
