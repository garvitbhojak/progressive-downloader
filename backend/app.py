from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests

# Initialize the FastAPI application
app = FastAPI(title="Video Proxy Server")

# Add CORSMiddleware to allow all origins
# This ensures that our future React frontend can communicate with this API without CORS errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allows all origins
    allow_credentials=True,     # Allows cookies and credentials
    allow_methods=["*"],        # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],        # Allows all HTTP headers
)

# Define a Pydantic BaseModel to validate the incoming URL payload
class URLPayload(BaseModel):
    url: str

@app.post("/analyze-url")
def analyze_url(payload: URLPayload):
    """
    Endpoint 1: Analyzes the target URL.
    Fetches headers without downloading the actual content and checks if it supports range requests.
    """
    try:
        # Perform a HEAD request on the target URL.
        # This will fetch headers only, validating the URL and gathering metadata quickly.
        response = requests.head(payload.url, allow_redirects=True, timeout=10)
        
        # Raise an exception for HTTP error codes (e.g., 404, 500)
        response.raise_for_status()
        
        # Parse the response to extract important headers
        content_length = response.headers.get("Content-Length")
        content_type = response.headers.get("Content-Type")
        accept_ranges = response.headers.get("Accept-Ranges")
        
        # Determine if the server natively supports partial content (byte ranges)
        supports_range = (accept_ranges == "bytes")

        # Return the parsed data as a JSON object
        return {
            "url": payload.url,
            "content_length": content_length,
            "content_type": content_type,
            "supports_range": supports_range
        }
        
    except requests.exceptions.Timeout:
        # Handle connection and read timeouts elegantly
        raise HTTPException(status_code=408, detail="Request timeout while trying to analyze the URL")
    except requests.exceptions.RequestException as e:
        # Handle all other typical request exceptions (e.g., connection errors, bad URLs)
        raise HTTPException(status_code=400, detail=f"Failed to analyze URL: {str(e)}")

@app.get("/stream")
def stream_video(url: str, request: Request):
    """
    Endpoint 2: Acts as a local streaming proxy.
    Accepts range requests from local clients (like video players) and proxies them to the target server.
    """
    # Dictionary to hold the outgoing requests headers
    req_headers = {}
    
    # Extract the Range header sent by the incoming client
    # Used extensively by browsers and players to request video chunks instead of whole files
    range_header = request.headers.get("Range")
    if range_header:
        req_headers["Range"] = range_header
        
    try:
        # Pass the request forward to the target server
        # stream=True ensures we don't load the entire file into memory at once
        response = requests.get(
            url, 
            headers=req_headers, 
            stream=True, 
            allow_redirects=True,
            timeout=10 # Base timeout to establish server connection
        )
        
        # Ensure we catch bad status responses before proxying streams
        response.raise_for_status()

        # Dictionary to hold headers to send back to the client
        res_headers = {}
        
        # Crucially, pass the target server's relevant response headers back to the client
        # Without these, video players will fail to interpret the video length properly or seek
        for header_name in ["Content-Type", "Content-Length", "Content-Range", "Accept-Ranges"]:
            if header_name in response.headers:
                res_headers[header_name] = response.headers[header_name]

        # Generator function that reads from the server and yields raw chunks back to the client
        def stream_generator():
            # requests.iter_content efficiently slices the incoming stream into 8KB chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        # Output passing back via a StreamingResponse, forwarding the generator, status code, and headers
        # Important: status_code handles both `200 OK` (full file) and `206 Partial Content` appropriately
        return StreamingResponse(
            stream_generator(), 
            status_code=response.status_code, 
            headers=res_headers
        )

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timeout while connecting to the stream URL")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Bad Gateway. Error streaming URL: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Convenience execution block for development testing
    uvicorn.run(app, host="0.0.0.0", port=8000)
