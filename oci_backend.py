import oci
import uuid
import base64
import responses
import json

from oci.ai_document import AIServiceDocumentClientCompositeOperations, AIServiceDocumentClient
from oci.ai_document.models import DocumentTextExtractionFeature, OutputLocation, DocumentKeyValueExtractionFeature

config = oci.config.from_file('.oci/config')

COMPARTMENT_ID = "ocid1.tenancy.oc1..aaaaaaaaijbjiap7x7uf27u3jpr6qamm2qtverpdtvqhneyxw6poinyonh7a"


closing_checklist_model_id = "ocid1.aidocumentmodel.oc1.phx.amaaaaaabcseiqaakzvl44czwkgea75n2i5sktxu74s6um3jtt3a4rvxoewq"
promissory_note_model_id = "ocid1.aidocumentmodel.oc1.phx.amaaaaaabcseiqaangc3hdq7hc42fhgvsvbguhbcuvygtgidli2kfx476ira"
dot_model_id = "ocid1.aidocumentmodel.oc1.phx.amaaaaaabcseiqaak2ewah77h6wkqzpz3snybsuzjuz2xwq4qe2nb572qyrq"


def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)

def process_with_oci(file_path, service_type):
    
    text_extraction = None
    with open(file_path, 'rb') as file:
        text_extraction = base64.b64encode(file.read()).decode('utf-8')
    

    aisservice_client = AIServiceDocumentClientCompositeOperations(AIServiceDocumentClient(config=config))

    text_extraction_feature = DocumentTextExtractionFeature()

    output_location = OutputLocation()

    output_location.namespace_name = "axvcnr0z0fj0"
    output_location.bucket_name = "tradesun_storage"
    output_location.prefix = "results"

    this_model_id = ""

    if service_type == "Closing Checklist":
        this_model_id = closing_checklist_model_id
    
    if service_type == "Promissory Note":
        this_model_id = promissory_note_model_id
    
    if service_type == "Deed Of Trust":
        this_model_id = dot_model_id
    
    print("service tyoe: ", service_type, this_model_id)

    create_processor_job_details_text_extraction = oci.ai_document.models.CreateProcessorJobDetails(
                                                    display_name=str(uuid.uuid4()),
                                                    compartment_id=COMPARTMENT_ID,
                                                    input_location=oci.ai_document.models.InlineDocumentContent(data=text_extraction),
                                                    output_location=output_location,
                                                    processor_config=oci.ai_document.models.GeneralProcessorConfig(processor_type="GENERAL", features=[DocumentKeyValueExtractionFeature(feature_type="KEY_VALUE_EXTRACTION", model_id=this_model_id)]))
                                                
    print("Calling create_processor with create_processor_job_details_text_extraction:", create_processor_job_details_text_extraction)

    create_processor_response = aisservice_client.create_processor_job_and_wait_for_state(
        create_processor_job_details=create_processor_job_details_text_extraction, 
        wait_for_states=[oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED],
        waiter_kwargs={"wait_callback": create_processor_job_callback}
    )

    print("processor call succeeded with status: {} and request_id: {}.".format(create_processor_response.status, create_processor_response.request_id))
    processor_job: oci.ai_document.models.ProcessorJob = create_processor_response.data
    print("create_processor_job_details_text_detection response: ", create_processor_response.data)

    print("Getting defaultObject.json from the output_location")
    object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
    get_object_response = object_storage_client.get_object(namespace_name=output_location.namespace_name,
                                                        bucket_name=output_location.bucket_name,
                                                        object_name="{}/{}/_/results/defaultObject.json".format(
                                                            output_location.prefix, processor_job.id))
    
    data_dict = json.loads(get_object_response.data.content.decode())
    
    result = {}

    if service_type == "Deed Of Trust":
        docFields = data_dict['pages'][0]['documentFields']

        for d in docFields:
            print(d["fieldLabel"]["name"], d["fieldValue"]["value"])
            result[d["fieldLabel"]["name"]] = d["fieldValue"]["value"]
        
        print(result)
    
    if service_type == "Promissory Note":
        docFields = data_dict['pages'][0]['documentFields']

        for d in docFields:
            print(d["fieldLabel"]["name"], d["fieldValue"]["value"])
            result[d["fieldLabel"]["name"]] = d["fieldValue"]["value"]
        
        print(result)

    if service_type == "Closing Checklist":
        docFields = data_dict['pages'][0]['documentFields']

        for d in docFields:
            print(d["fieldLabel"]["name"], d["fieldValue"]["value"])
            result[d["fieldLabel"]["name"]] = d["fieldValue"]["value"]
        
        print(result)
            
        s = result['Recording Responsibility']

        if "COMPANY" in s:
            result['Recording Responsibility'] = s.replace("COMPANY", "")
        
        result["Jurisdiction"] = result["Property City"] + " " + result["Property State"]
        result["Complete Property Addresss"] = result["Property Address"] + " " + result["Property City"] + " " + result["Property State"]+ " " + result["Property ZIP"] 

    return result

    


