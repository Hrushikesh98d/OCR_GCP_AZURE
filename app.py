import os
import mimetypes
import logging

from flask import Flask, render_template, request, send_from_directory
from google.oauth2 import service_account
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import GoogleAPIError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

from oci_backend import process_with_oci

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)

# Azure models configuration
azure_models = {
    "promissory_note": {
        "endpoint": "https://promissorynote.cognitiveservices.azure.com/",
        "key": "3d7f3244281049f986f0fcbb13655d4b",
        "model_id": "promissorynote"  # Ensure model_id is correctly specified here
    },
    "Closing_Instruction": {
        "endpoint": "https://closinginstruction.cognitiveservices.azure.com/",
        "key": "e4ac7ab296f449a3a2026e1557beaeaf",
        "model_id": "closingInstruction"
    },
    "Deed_of_Trust": {
        "endpoint": "https://deedoftrust.cognitiveservices.azure.com/",
        "key": "b40458b766e54b6b99ad3ce44f489727",
        "model_id": "deedoftrust"
    },
    "Loan_Documentation_Request": {
        "endpoint": "https://loandocumentationrequest.cognitiveservices.azure.com/",
        "key": "e21150cb732846fdb1c5437b5959924a",
        "model_id": "loandocumentationrequest"
    },

    "commercial_invoice": {
        "endpoint":"https://commercialinvoice.cognitiveservices.azure.com/",
        "key":"46d0d8c7b69d41ca9522b860e85b14d1",
        "model_id":"commericalinvoice"
    },

    "bill_of_lading": {
        "endpoint":"https://billoflading.cognitiveservices.azure.com/",
        "key":"c27b0231b9324950b417200a3db45ac3",
        "model_id":"billoflading"
    },
    "45A": {
        "endpoint": "https://45a.cognitiveservices.azure.com/",
        "key": "bb460754073646d2ada133f6b470a5ac",
        "model_id": "45A_2"  # Ensure model_id is correctly specified here
    },
    "46A": {
        "endpoint": "https://46a.cognitiveservices.azure.com/",
        "key": "FDXGQwkdHKhiKZ6lF8fM8vDO7g6NqBBMEvB4eapK0VZoC2qD4UG6JQQJ99AKACYeBjFXJ3w3AAALACOGZrGM",
        "model_id": "46A"  # Ensure model_id is correctly specified here
    },
    "47": {
        "endpoint": "https://47.cognitiveservices.azure.com/",
        "key": "8W4JRGcB24YaSgh1jUhBIvSGldrqYXbK48UOcogdSkifG6a7Xk51JQQJ99AKACYeBjFXJ3w3AAALACOG4CCc",
        "model_id": "47"  # Ensure model_id is correctly specified here
    }




}


def process_document_google(file_content, processor_id, mime_type):
    project_id = "842588065610"
    location = "us"

    try:
        credentials = service_account.Credentials.from_service_account_file("/Users/Hrushikesh/Desktop/Trade_Sun_Project/Clone/OCR_GCP_AZURE/service-account-key.json")
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts, credentials=credentials)
        name = client.processor_path(project_id, location, processor_id)

        raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
        request_obj = documentai.ProcessRequest(name=name, raw_document=raw_document, field_mask="entities")
        result = client.process_document(request=request_obj)
        document = result.document

        entities = []
        for entity in document.entities:
            bounding_polys = []
            for page_ref in entity.page_anchor.page_refs:
                bounding_poly = page_ref.bounding_poly  # Use bounding_poly, not bounding_polys
                if bounding_poly:
                    bounding_polys.append({
                        "left": bounding_poly.normalized_vertices[0].x,
                        "top": bounding_poly.normalized_vertices[0].y,
                        "right": bounding_poly.normalized_vertices[2].x,
                        "bottom": bounding_poly.normalized_vertices[2].y,
                    })
            entities.append({
                "type": entity.type_,
                "mention_text": entity.mention_text,
                "bounding_boxes": bounding_polys
            })
        return entities

    except GoogleAPIError as e:
        logging.error(f"An error occurred: {e}")
        return [{"Error": str(e)}]

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
    extracted_data.sort(key=lambda x: x[0])
    return extracted_data

import openai

def format_data_with_openai45A(extracted_data):
    """
    Use OpenAI Chat API to format and summarize extracted data.
    """
    openai.api_key = "sk-svcacct-wE6OYzsc9F70a4a2BAlPmdVgOITYvQctdLJI9Ik0CuF8lP8QBw_ssW10xYEjeMqhoUpmQxWT3BlbkFJeNV7Yf5i7rGKfKWQaZxqtk3Um52-Dk2bFBavbY8tGflBq44FjsHsNRZyNkgMBZR7wE6EEAA"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant skilled at formatting and analyzing raw document data. "
                "Your task is to format the given data into structured, readable sections and provide insights."
            ),
        },
        {
            "role": "user",
            "content": f"""
            The following is raw extracted data from a document:
            {extracted_data}
            
            
            This is letter of credit 45A field data, Format it into a structured format and readable format, and give me insights about it 
            """,
        },
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' if you don't have GPT-4 access
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        formatted_data = response["choices"][0]["message"]["content"].strip()
        return formatted_data
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return "Error in formatting data with OpenAI."

def format_data_with_openai46A(extracted_data):
    """
    Use OpenAI Chat API to format and summarize extracted data.
    """
    openai.api_key = "sk-svcacct-wE6OYzsc9F70a4a2BAlPmdVgOITYvQctdLJI9Ik0CuF8lP8QBw_ssW10xYEjeMqhoUpmQxWT3BlbkFJeNV7Yf5i7rGKfKWQaZxqtk3Um52-Dk2bFBavbY8tGflBq44FjsHsNRZyNkgMBZR7wE6EEAA"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant skilled at formatting and analyzing raw document data. "
                "Your task is to format the given data into structured, readable sections and provide insights."
            ),
        },
        {
            "role": "user",
            "content": f"""
            The following is raw extracted data from a document:
            {extracted_data}
            
            This is letter of credit 46A field data, Format it into a structured format and readable format, and give me insights about it
            """,
        },
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' if you don't have GPT-4 access
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        formatted_data = response["choices"][0]["message"]["content"].strip()
        return formatted_data
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return "Error in formatting data with OpenAI."


def format_data_with_openai47(extracted_data):
    """
    Use OpenAI Chat API to format and summarize extracted data.
    """
    openai.api_key = "sk-svcacct-wE6OYzsc9F70a4a2BAlPmdVgOITYvQctdLJI9Ik0CuF8lP8QBw_ssW10xYEjeMqhoUpmQxWT3BlbkFJeNV7Yf5i7rGKfKWQaZxqtk3Um52-Dk2bFBavbY8tGflBq44FjsHsNRZyNkgMBZR7wE6EEAA"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant skilled at formatting and analyzing raw document data. "
                "Your task is to format the given data into structured, readable sections and provide insights."
            ),
        },
        {
            "role": "user",
            "content": f"""
            The following is raw extracted data from a document:
            {extracted_data}
            
            This is letter of credit 45A field data, Format it into a structured format and readable format, and give me insights about it
            """,
        },
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' if you don't have GPT-4 access
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        formatted_data = response["choices"][0]["message"]["content"].strip()
        return formatted_data
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return "Error in formatting data with OpenAI."


def process_field_45A(file_path):
    """
    Process the '45A' field from Letter of Credit documents using the specific Azure model.
    """
    model_info = azure_models.get("45A")  # Fetch configuration for the '45A' model
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

    # Extract only the '45A' field
    extracted_45A = {}
    for document in result.documents:
        for name, field in document.fields.items():
            if field.value_type:  # Check if it's the '45A' field
                field_value = field.value if field.value else field.content
                if field_value:
                    extracted_45A[name] = field_value

    # Format extracted data using OpenAI
    raw_data = extracted_45A

    if raw_data:
        formatted_data = format_data_with_openai45A(raw_data)
        print("formared data *********" ,  formatted_data)
        return {"raw_data": raw_data, "formatted_data": formatted_data}
    else:
        return {"raw_data": raw_data, "formatted_data": {}}

#46A function to extract the data from the azure
def process_field_46A(file_path):

    model_info = azure_models.get("46A")  # Fetch configuration for the '45A' model
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


    extracted_46A = {}
    for document in result.documents:
        for name, field in document.fields.items():
            if field.value_type:
                field_value = field.value if field.value else field.content
                if field_value:
                    extracted_46A[name] = field_value

    # Format extracted data using OpenAI
    raw_data = extracted_46A

    if raw_data:
        formatted_data = format_data_with_openai46A(raw_data)
       # print("formared data *********" ,  formatted_data)
        return {"raw_data": raw_data, "formatted_data": formatted_data}
    else:
        return {"raw_data": raw_data, "formatted_data": {}}

#47 function to extract the data from the azure
def process_field_47(file_path):

    model_info = azure_models.get("47")  # Fetch configuration for the '45A' model
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


    extracted_47 = {}
    for document in result.documents:
        for name, field in document.fields.items():
            if field.value_type:
                field_value = field.value if field.value else field.content
                if field_value:
                    extracted_47[name] = field_value


    raw_data = extracted_47

    if raw_data:
        formatted_data = format_data_with_openai47(raw_data)
        # print#("formared data *********" ,  formatted_data)
        return {"raw_data": raw_data, "formatted_data": formatted_data}
    else:
        return {"raw_data": raw_data, "formatted_data": {}}




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
                return render_template('results.html', entities=entities, file_url=f"/uploads/{document_file.filename}")
            elif service_type == 'azure':
                if processor_id == "45A":
                    # Process the specific '45A' field
                    extracted_45A = process_field_45A(file_path)
                    return render_template('results45A.html', entities=extracted_45A, file_url=f"/uploads/{document_file.filename}")
                elif processor_id =="46A":

                    extracted_46A = process_field_46A(file_path)
                    return render_template('results45A.html', entities=extracted_46A, file_url=f"/uploads/{document_file.filename}")

                elif processor_id == "47":

                    extracted_47= process_field_47(file_path)
                    return render_template('results45A.html', entities=extracted_47, file_url=f"/uploads/{document_file.filename}")


                else:
                    # Process other Azure models
                    model_info = azure_models.get(processor_id)
                    entities = process_document_azure(file_path, model_info)
                    return render_template('results2.html', entities=entities, file_url=f"/uploads/{document_file.filename}")
            elif service_type == 'oci':
                content = process_with_oci(file_path, processor_id)
                # print("content", content)
                return render_template('results_oci.html', content=content, file_url=f"/uploads/{document_file.filename}")

    return render_template('index.html')



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
