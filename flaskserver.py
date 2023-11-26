
from flask import Flask
import random
app = Flask(__name__)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=random.randint(10000,65535), debug=True)
