# Jaeger v2 test project

## Description 
Test enviroment with redis and 3 microservices with Jaeger tracing integration.

## Run
1. Clone the repository
2. Create .env file from .env.template
3. Run docker-compose
4. Open printer container in interactive mode and run `python3 printer.py`. Input to numbers.
5. Run spark-dependencies container and wait it to finish
6. Open jaeger in browser: https://127.0.0.1:8080

