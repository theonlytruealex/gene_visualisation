import volcano
from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)
app.config["df"] = pd.read_csv("data.csv")

app = volcano.init_dash("/volcano/", app)

@app.route("/")
def home():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>protein main</title>
            <link rel="stylesheet" 
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <style>
                body { background-color: #f8f9fa; }
                .container { max-width: 600px; margin-top: 50px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-primary">Protein activity level viualiser</h1>
                <h2>Select Your Dash App</h2>
                <ul class="list-group">
                    <li class="list-group-item">
                        <a href='/volcano/' class="btn btn-success">Open Dash App</a>
                    </li>
                </ul>
            </div>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
