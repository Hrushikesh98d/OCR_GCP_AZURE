from flask import Flask, render_template, request, send_from_directory
from google.oauth2 import service_account
from google.cloud import documentai
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import GoogleAPIError

import os
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] =
import mimetypes
import logging

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)

# Define Azure Form Recognizer details
azure_models = {
    "promissory_note": {
        "endpoint": "https://eastus.api.cognitive.microsoft.com/",
        "key": "d0939dff498f473888e3f8ae53bb20d8",
        "model_id": "promissory_note"  # Ensure model_id is correctly specified here
    },
    "Closing_Instruction": {
        "endpoint": "https://eastus.api.cognitive.microsoft.com/",
        "key": "5e6778d8f19d40a28acd8053aaa96404",
        "model_id": "Closing_Instruction"
    },
    "Deed_of_Trust": {
        "endpoint": "https://eastus.api.cognitive.microsoft.com/",
        "key": "6904b7b57e4543b6aedb6fced68ceea7",
        "model_id": "Deed_of_Trust"
    },
    "Loan_Documentation_Request": {
        "endpoint": "https://eastus.api.cognitive.microsoft.com/",
        "key": "cd9c6ef505184658a367313ab9726fe0",
        "model_id": "Loan_Documentation_Request"
    }
}


def process_document_google(file_content, processor_id, mime_type):
    project_id = "842588065610"
    location = "us"

    try:
        credentials = service_account.Credentials.from_service_account_file("/Users/Hrushikesh/Desktop/Trade_Sun_Project/Clone/OCR_GCP_AZURE/service-account-key.json"
        )
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts, credentials=credentials)
        name = client.processor_path(project_id, location, processor_id)

        raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
        request_obj = documentai.ProcessRequest(name=name, raw_document=raw_document, field_mask="entities")
        result = client.process_document(request=request_obj)
        document = result.document

        entities = [(entity.type_, entity.mention_text) for entity in document.entities]
        return entities
    except GoogleAPIError as e:
        logging.error(f"An error occurred: {e}")
        return [("Error", str(e))]

def process_document_azure(file_path, model_info):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=model_info["endpoint"],
        credential=AzureKeyCredential(model_info["key"])
    )

    with open(file_path, "rb") as document:
        poller = document_analysis_client.begin_analyze_document(
            model_id=model_info["model_id"],
            document=document
        )
        result = poller.result()

    extracted_data = []
    for idx, document in enumerate(result.documents):
        for name, field in document.fields.items():
            if field.value_type:  # Only include labeled fields
                field_value = field.value if field.value else field.content
                extracted_data.append((name, field_value))
    return extracted_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        document_file = request.files['document_file']
        service_type = request.form['service_type']
        processor_id = request.form['processor_type']

        if document_file:
            file_content = document_file.read()
            mime_type, _ = mimetypes.guess_type(document_file.filename)

            if mime_type is None:
                logging.error("Unsupported file type")
                return "Unsupported file type", 400

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], document_file.filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)

            if service_type == 'google':
                entities = process_document_google(file_content, processor_id, mime_type)
            else:
                model_info = azure_models.get(processor_id)
                entities = process_document_azure(file_path, model_info)

            file_url = f"/uploads/{document_file.filename}"
            return render_template('results.html', entities=entities, file_url=file_url)

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
