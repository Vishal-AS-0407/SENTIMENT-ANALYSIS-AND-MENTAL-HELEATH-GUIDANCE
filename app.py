from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Azure Text Analytics Configuration
language_key = "F8imrIIYFvKJKzRZYMuUQ9AO8B41safPpx1de1Z0fBsXh0hDDDOkJQQJ99AKACGhslBXJ3w3AAAaACOGTwaF"
language_endpoint = "https://vishal4724.cognitiveservices.azure.com/"
text_client = TextAnalyticsClient(endpoint=language_endpoint, credential=AzureKeyCredential(language_key))

# Azure OpenAI Configuration
openai_client = AzureOpenAI(
    api_key="AhwfzfTZrbxKJ0ssB0QFDBykYmy9AZi6lJAilMfKJqT2Ziu9QuvlJQQJ99AKAC5RqLJXJ3w3AAAAACOG6jvA",
    api_version="2024-05-01-preview",
    azure_endpoint="https://cben-m3lqueak-westeurope.openai.azure.com/"
)
deployment_name = "gpt-35-turbo"

UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER

def analyze_file(file_path):
    with open(file_path, 'r') as file:
        documents = [file.read()]
    
    response = text_client.analyze_sentiment(documents, show_opinion_mining=True)
    results = []
    
    for document in response:
        result = {
            "document_sentiment": document.sentiment,
            "positive_score": document.confidence_scores.positive,
            "negative_score": document.confidence_scores.negative,
            "neutral_score": document.confidence_scores.neutral,
            "sentences": []
        }

        for sentence in document.sentences:
            sentence_data = {
                "text": sentence.text,
                "sentiment": sentence.sentiment,
                "positive_score": sentence.confidence_scores.positive,
                "negative_score": sentence.confidence_scores.negative,
                "neutral_score": sentence.confidence_scores.neutral,
                "opinions": []
            }

            for opinion in sentence.mined_opinions:
                opinion_data = {
                    "target": opinion.target.text,
                    "target_sentiment": opinion.target.sentiment,
                    "assessments": [
                        {
                            "text": assessment.text,
                            "sentiment": assessment.sentiment
                        } for assessment in opinion.assessments
                    ]
                }
                sentence_data["opinions"].append(opinion_data)

            result["sentences"].append(sentence_data)
        results.append(result)
    return results

def generate_report(user_info, output_text=""):
    input_text = f"""
    User Details:
    Name: {user_info['name']}
    Age: {user_info['age']}
    Gender: {user_info['gender']}
    Workplace: {user_info['workplace']}
    
    Arousal: {user_info['arousal']}
    Dominance: {user_info['dominance']}
    Valence: {user_info['valence']}
    ERP: {user_info['erp']}
    
    Trauma Experience: {user_info['trauma_details']}
    Emotional Breakdown: {user_info['emotional_breakdown_details']}
    Positive Events: {user_info['positive_events_details']}
    
    Please generate a Detailed mental health report analyzing:
    - The impact of Arousal, Dominance, Valence, and ERP on mental health.
    - Emotional state, decision-making skills, and cognitive ability.
    - Recommendations for therapy or psychological support.
    - Suggestions for activities, workload management, and mental health improvement.
    """
    
    try:
        response = openai_client.completions.create(
            model=deployment_name,
            prompt=input_text,
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error: Could not generate report."

def save_report(report, filename):
    file_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
    with open(file_path, "w") as file:
        file.write("Mental Health Report\n")
        file.write("====================\n\n")
        file.write(report)
        file.write("\n\nEnd of Report")
    return file_path

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sentiment-analysis", methods=["GET", "POST"])
def sentiment_analysis():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            analysis_result = analyze_file(file_path)
            return render_template("sentiment_result.html", result=analysis_result)
    
    return render_template("sentiment_analysis.html")

@app.route("/mental-health", methods=["GET", "POST"])
def mental_health():
    if request.method == "POST":
        user_info = {
            'name': request.form.get('name'),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'workplace': request.form.get('workplace'),
            'arousal': request.form.get('arousal'),
            'dominance': request.form.get('dominance'),
            'valence': request.form.get('valence'),
            'erp': request.form.get('erp'),
            'trauma': request.form.get('trauma'),
            'trauma_details': request.form.get('trauma_details') or 'None',
            'emotional_breakdown': request.form.get('emotional_breakdown'),
            'emotional_breakdown_details': request.form.get('emotional_breakdown_details') or 'None',
            'positive_events': request.form.get('positive_events'),
            'positive_events_details': request.form.get('positive_events_details') or 'None'
        }
        
        report = generate_report(user_info)
        filename = f"report_{user_info['name']}_{user_info['age']}.txt"
        file_path = save_report(report, filename)
        return render_template("mental_health_result.html", report=report, filename=filename)
    
    return render_template("mental_health.html")

@app.route("/download-report/<filename>")
def download_report(filename):
    return send_file(os.path.join(app.config['REPORTS_FOLDER'], filename),
                    as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)