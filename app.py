import volcano
from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

app = volcano.init_dash("/volcano/", app)

@app.route("/")
def home():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Protein Activity Visualizer</title>
            <link rel="stylesheet" 
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <style>
                body {
                    background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    color: #212529;
                }
                .container {
                    max-width: 700px;
                    margin-top: 80px;
                    text-align: center;
                    padding: 30px;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }
                h1 {
                    font-size: 2.5rem;
                    color: #4a148c;
                }
                .btn-success {
                    background-color: #6a1b9a;
                    border: none;
                    padding: 10px 20px;
                    font-size: 1.1rem;
                }
                .btn-success:hover {
                    background-color: #4a148c;
                }
                .gene-icon {
                    font-size: 50px;
                    color: #6a1b9a;
                    margin-bottom: 20px;
                }
            </style>
            <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
        </head>
        <body>
            <div class="container">
                <div class="gene-icon">
                    <i class="fas fa-dna"></i>
                </div>
                <h1>Protein Activity Visualizer</h1>
                <a href='/volcano/' class="btn btn-success">
                    🔬 Launch Volcano Plot App
                </a>
            </div>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
