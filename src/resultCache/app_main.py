from resultCache import app
import os

port = int(os.getenv('PORT', 8080))

def run_app():
    app.run(host=os.getenv('IP', '0.0.0.0'), port=port)

if __name__=="__main__":
    run_app()