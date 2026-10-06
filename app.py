from flask import Flask, render_template

app = Flask(__name__)

# When a user visits the home page, render the index.html file
@app.route('/')
def home():
    # Flask automatically looks inside the 'templates' folder for this file
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
