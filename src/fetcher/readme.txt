FETCHER

/api (COMMUNICATION):

    This is where all the communication with the SM platform takes place. You will one folder seperated with /endpoints. Here, all the graphql queries are transformed into strings and sent into the CESMII platform to retreive data.
    
/tests (TESTING): 
    test_routes.py:
        Tests routes and the API/Endpoints created from routes.py from /api.

        To run tests, you will need to cd into fetcher/test and run the this line in the terminal:

                    pytest -v -s

        I wrote all the tests using the pytest library. Once you read the code and some articles, its very easy to comprehend what is going on. Of course, you need a baseline understanding of Flask and API routes, but its quite simple once you catch on.

    conftest.py:
        Tests configuration. Left the testing in there in case it is needed in the future

DOCKER:
    Make sure you are in the Fetcher directory before doing this
    To boot up a docker instance, you will need to run:

        docker build -t flask/fetcher .

    After building the image, you can run the container on:

        docker run -p 8000:8000 flask/fetcher


