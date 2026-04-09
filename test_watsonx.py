from app.services.route_service import _build_watsonx_client, _build_prompt, _watsonx_model
import logging
logging.basicConfig(level=logging.INFO)
try:
    client = _build_watsonx_client()
    print("Client initialized:", client is not None)
    if client:
        prompt = _build_prompt("Metro Polanco", "Metro Tacubaya")
        print("Executing generation...")
        res = client.generate_text(prompt=prompt)
        print("Result:", res)
except Exception as e:
    print("Exception occurred:", type(e).__name__, str(e))
