# OCI AI configuration for the backend
MODEL_REGISTRY = {
    "cohere_oci": {
        "model_id": "cohere.command-r-plus-08-2024",
        "service_endpoint": "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com",
        "compartment_id": "ocid1.compartment.oc1..aaaaaaaaohqhsft2n2hbefl7pushupe6zcel4b2hzpgotevssjrz57nf5fia",
        "provider": "cohere",
        "auth_type": "API_KEY",
        "auth_profile": "DEFAULT",
        "model_kwargs": {"temperature": 0, "max_tokens": 4000},
        "embedding_model": "cohere.embed-multilingual-v3.0",
    },
    "meta_oci": {
        "model_id": "ocid1.generativeaimodel.oc1.eu-frankfurt-1.amaaaaaask7dceya4tdabclcsqbc3yj2mozvvqoq5ccmliv3354hfu3mx6bq",
        "service_endpoint": "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com",
        "compartment_id": "ocid1.compartment.oc1..aaaaaaaaohqhsft2n2hbefl7pushupe6zcel4b2hzpgotevssjrz57nf5fia",
        "provider": "meta",
        "auth_type": "API_KEY",
        "auth_profile": "DEFAULT",
        "model_kwargs": {"temperature": 0, "max_tokens": 2000},
    },
}

# Function to get prompt by model name and prompt type
def get_prompt(model_name, prompt_type):
    from .promptsM import PROMPT_SETS
    
    if model_name not in PROMPT_SETS:
        raise ValueError(f"No prompts defined for model {model_name}")
    
    model_prompts = PROMPT_SETS[model_name]
    
    if prompt_type not in model_prompts:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    return model_prompts[prompt_type]