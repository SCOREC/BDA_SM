from sampler import app
import os

def run_app():
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 9999)))

if __name__=="__main__":
    run_app()