from flask import Flask, render_template, request, redirect, url_for, flash
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Provide your Azure credentials here
language_key = "F8imrIIYFvKJKzRZYMuUQ9AO8B41safPpx1de1Z0fBsXh0hDDDOkJQQJ99AKACGhslBXJ3w3AAAaACOGTwaF"
language_endpoint = "https://vishal4724.cognitiveservices.azure.com/"
client = TextAnalyticsClient(endpoint=language_endpoint, credential=AzureKeyCredential(language_key))

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def analyze_file(file_path):
    with open(file_path, 'r') as file:
        documents = [file.read()]
    
    response = client.analyze_sentiment(documents, show_opinion_mining=True)
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

@app.route("/", methods=["GET", "POST"])
def index():
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
            return render_template("result.html", result=analysis_result)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
