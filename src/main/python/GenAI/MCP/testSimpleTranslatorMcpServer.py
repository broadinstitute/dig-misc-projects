
# test_mcp_server.py
from fastapi import FastAPI, Request
import uvicorn
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Test MCP Server",
    description="Simple test server that returns hard-coded phrases",
    version="0.1.0"
)

# Hard-coded phrases to return
PHRASES = [
    "Levonorgestrel, a reproductive drug similar to Ethinylestradiol, potentially treats Ehlers-Danlos syndrome",
    "Ethinylestradiol, a receptor modulator, potentially treats Ehlers-Danlos syndrome",
    """Midazolam, with properties Neurotransmitter Agent, Central Nervous System Drug, Apoptosis Inducer, Antineoplastic Agent, 
    Neuromuscular Agent, Anaesthetic and decreases the metabolic processing of genes ABCB6 and CYP3A4 
    which in turn decreases melatonin might treat Ehlers-Danlos syndrome
    """
]

@app.get("/")
async def health_check():
    """Health check endpoint"""
    logger.info(f"=============== Received query for health_check")

    return {"status": "ok", "message": "Test MCP Server is running"}

@app.post("/mcp/{path:path}")
async def mcp_endpoint(path: str, request: Request):
    """
    Main endpoint that returns a hard-coded phrase
    """
    try:
        # Log the incoming request
        body = await request.json()
        logger.info(f"Received request for path: {path}")
        logger.info(f"Request body: {body}")
        
        # Select a random phrase
        phrase = random.choice(PHRASES)
        
        # Return a response mimicking what your API might return
        return {
            "id": "test-response-id",
            "object": "completion",
            "created": 1682789043,
            "model": "test-mcp-model",
            "content": PHRASES,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 10,
                "output_tokens": len(phrase.split())
            }
        }
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/mcp/models")
async def list_models():
    """
    Endpoint to list available models (often used in API discovery)
    """
    logger.info(f"=============== Received query for MODELS")

    return {
        "object": "list",
        "data": [
            {
                "id": "test-mcp-model",
                "object": "model",
                "created": 1682789043,
                "owned_by": "test"
            }
        ]
    }

if __name__ == "__main__":
    # For local development
    # src/main/python/GenAI/MCP/testSimpleTranslatorMcpServer.py
    # uvicorn.run("test_mcp_server:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("testSimpleTranslatorMcpServer:app", host="0.0.0.0", port=8081, reload=True)

