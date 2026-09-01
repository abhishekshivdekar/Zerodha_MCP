#!/usr/bin/env python3
"""Query kite MCP server for available tools"""

import json
import requests
import time
from typing import Optional

def query_kite_mcp_server():
    """Connect to kite MCP server and list available tools"""
    
    url = "https://mcp.kite.trade/sse"
    
    print("🔗 Connecting to kite MCP server...")
    print(f"   Endpoint: {url}\n")
    
    try:
        # Send initial request with streaming
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Connection Status: {response.status_code} {response.reason}")
        print(f"📨 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"🔐 CORS: {response.headers.get('access-control-allow-origin', 'N/A')}")
        print(f"🌍 Server: {response.headers.get('Server', 'N/A')}\n")
        
        # Parse SSE events
        print("📋 Received Events from Server:\n")
        
        event_count = 0
        session_id = None
        message_endpoint = None
        
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
                
            event_count += 1
            print(f"Event {event_count}: {line}")
            
            if line.startswith("data:"):
                data = line[5:].strip()
                try:
                    parsed = json.loads(data)
                    print(f"  └─ Parsed: {json.dumps(parsed, indent=4)}\n")
                    
                    # Check for endpoint information
                    if "endpoint" in parsed or "sessionId" in parsed:
                        session_id = parsed.get("sessionId")
                        
                except json.JSONDecodeError:
                    pass
            
            # Stop after a reasonable number of events to avoid infinite stream
            if event_count >= 10:
                print("\n⏹️  Stopped after 10 events (stream is continuous)")
                break
        
        print("\n✅ Server is live and responding!")
        print("📝 Note: Kite MCP is using SSE (Server-Sent Events) protocol")
        print("   To interact with specific tools, use the MCP client protocol with JSON-RPC")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
    except requests.exceptions.Timeout:
        print(f"❌ Connection Timeout: Server took too long to respond")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    query_kite_mcp_server()
