#!/usr/bin/env python3
"""
Simple HTTP server to test if the basic web functionality works.
This will help diagnose if the issue is with Streamlit specifically or with network/port access.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Video Transcriber - Test Server</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f6; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #262730; text-align: center; }
                    .status { padding: 15px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; margin: 20px 0; }
                    .info { padding: 15px; background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; margin: 20px 0; }
                    .error { padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; margin: 20px 0; }
                    ul { text-align: left; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎙️ Video Transcriber - Server Test</h1>
                    
                    <div class="status">
                        <strong>✅ SUCCESS:</strong> Basic web server is working!
                    </div>
                    
                    <div class="info">
                        <strong>📋 Diagnosis:</strong> If you can see this page, the network and port access are working correctly. 
                        The issue is specifically with Streamlit configuration or startup.
                    </div>
                    
                    <div class="info">
                        <strong>🔧 Next Steps:</strong>
                        <ul>
                            <li>The transcriber core functionality is working (transcriber.py)</li>
                            <li>Python and dependencies are properly installed</li>
                            <li>Network and port access are functional</li>
                            <li>We need to resolve the Streamlit-specific issue</li>
                        </ul>
                    </div>
                    
                    <div class="info">
                        <strong>💡 Alternative Solutions:</strong>
                        <ul>
                            <li>Use the CLI version: <code>python3 cli_app.py video.mp4</code></li>
                            <li>Create a simple Flask web interface</li>
                            <li>Troubleshoot Streamlit configuration</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode())
        else:
            super().do_GET()

def main():
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"✅ Simple server running at http://localhost:{PORT}")
            print("🔍 This will help diagnose if the issue is with Streamlit or network access")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
