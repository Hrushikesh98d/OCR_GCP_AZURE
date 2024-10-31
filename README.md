# Document Extraction 

## Author
**Hrushikesh Dandge**

## About

This web application enables users to upload PDF documents and extract specific information using either Google Document AI or Azure Document Intelligence services. The application supports the processing of various document types such as:

- Promissory Note
- Closing Instruction
- Deed of Trust
- Loan Documentation Request
- Bill of Lading
- Commercial Invoice
- Letter of credit (45A Field) (Azure)

Both Google and Azure services have been trained to recognize and extract specified data fields from these document types. The extracted information is displayed on the web application interface for easy access and review.

## Features

- **Upload PDF**: Users can upload their documents in PDF format.
- **Service Selection**: Choose between Google Document AI or Azure Document Intelligence for data extraction.
- **Document Type Selection**: Select the type of document from a predefined list.
- **Data Extraction**: The application extracts predefined fields from the uploaded document based on the selected service and document type.
- **Output Display**: Extracted data is displayed directly in the web application.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Cloud Services**: Google Document AI, Azure Document Intelligence
- **Document Processing**: Custom processors trained to handle specific document types

## Installation & Setup

1. Clone the repository to your local machine:
2. Install the required dependencies:
   
   `pip install -r requirements.txt`
3. Downlaod the service-account-key.json to your local machine and set up the path in the app.py at line:62
4. Run the application
   `python app.py`
5. Open your browser and navigate to http://localhost:5000.

   

