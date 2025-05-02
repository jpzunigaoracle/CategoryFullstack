// Simplified model registry that only contains model names for reference
export const MODEL_NAMES = {
  COHERE: 'cohere_oci',
  META: 'meta_oci'
};

// Default model to use
export const DEFAULT_MODEL = MODEL_NAMES.COHERE;

// Import from backend configuration
export const MODEL_REGISTRY = {
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
};