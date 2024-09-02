# Trade Sun

## Author
Hrushikesh Dandge

# Google Document AI Flask Web Application

This is a Flask web application that uses Google Document AI and Azure document Intelligence to extract entities from uploaded documents (e.g., PDFs). The extracted information is displayed as labels on a results page. The app uses Google Cloud's Document AI  and Azure document Intelligence to process the documents and return structured data
## Features

- Upload a document (PDF) through the web interface.
- Extract entities like dates, names, or custom labels using Google Document AI.
- Display extracted entities in a user-friendly results page.

## Prerequisites


## Google Cloud Setup

Follow these steps to set up Google Cloud and enable Document AI for this project:

### Step 1: Set Up Google Cloud Account
1. If you don’t already have a Google Cloud account, create one by visiting the [Google Cloud Console](https://console.cloud.google.com/).
2. Set up a new project:
    - Go to the Google Cloud Console.
    - Click on the project dropdown at the top of the page and select **New Project**.
    - Enter your project name and other required information, then click **Create**.

### Step 2: Enable the Document AI API
1. In the Google Cloud Console, navigate to the **API & Services** dashboard.
2. Click on **Enable APIs and Services**.
3. In the search bar, search for **Document AI API**.
4. Click on the **Document AI API** from the search results.
5. Click the **Enable** button to activate the API for your project.

### Step 3: Set Up a Service Account
1. Go to the **IAM & Admin** section in the Google Cloud Console.
2. Click on **Service Accounts** in the sidebar.
3. Click on the **+ Create Service Account** button.
4. Fill in the required information:
    - Enter a **name** and **description** for the service account.
5. Click **Create and Continue**.
6. Assign roles to the service account:
    - Select **Project > Editor** (or choose a more restrictive role if preferred).
7. Click **Continue**, then click **Done**.

### Step 4: Create and Download the Service Account Key
1. In the **Service Accounts** page, locate your newly created service account.
2. Click on the **email** of the service account to open its details.
3. Navigate to the **Keys** tab.
4. Click **Add Key** and select **Create New Key**.
5. Choose **JSON** as the key type and click **Create**.
6. A JSON file containing your service account key will be automatically downloaded to your computer. Save this file securely as it is needed to authenticate with Google Cloud.

### Step 5: Set Up Environment Variable for Service Account Key
1. Once you have the service account key, set up the `GOOGLE_APPLICATION_CREDENTIALS` environment variable on your machine. Use the following command:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
````

Replace /path/to/your/service-account-key.json with the actual path to your Google Cloud service account key file.


# Azure Form Recognizer Setup

## Step 1: Set Up Azure Account

1. **Create an Azure Account**
   - If you don’t have an Azure account, create one at the [Azure Portal](https://portal.azure.com).

2. **Set Up a Form Recognizer Resource**
   - Navigate to **Create a resource**.
   - Search for **Form Recognizer**.
   - Click **Create** to set up a new Form Recognizer instance.
   - Note down the **Endpoint** and **Key** provided after the resource is created. You’ll need these for your application.

## Step 2: Create Custom Models (Optional)

1. **Deploy Custom Models**
   - If needed, deploy custom models for specific document types (e.g., promissory notes, deeds of trust) to your Form Recognizer resource.

2. **Note Model IDs**
   - After deploying custom models, note down the **Model IDs** for each document type. These IDs will be used when integrating the Form Recognizer service into your application.






# Installation

### 1.Clone the Repository

```bash 
git clone https://github.com/your-username/document-ai-flask-app.git
cd document-ai-flask-app
```

### 2. Set Up the Environment

Install the required dependencies:

```bash 
pip install -r requirements.txt
```

# Run application

```bash 
python app.py
```

