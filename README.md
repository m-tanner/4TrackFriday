[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# [4 Track Friday](http://4trackfriday.com) Web App

This is the source code for hosting the back and front end of the Four Track Friday web application.
It uses Python and Flask for the back-end and Jinja2 for the front-end. Data for the app is stored 
in Google Cloud and AWS. The app is able to use either data store, configurable by environment variable. 
The app is deployed into a Google Kubernetes Engine cluster that I manage. It is deployed via a local Skaffold
pipeline, which you can inspect at `skaffold.yml`. This is all deployed live at [4trackfriday.com](http://4trackfriday.com).

## Setup Instructions
1) Install necessary software tools. For OS X, this is:<br/>
`brew install kubernetes-cli`<br/>
`brew install kustomize`<br/>
`brew install minikube`<br/>
`brew install skaffold`
2) Start minikube<br/>
`minikube start --driver=hyperkit`<br/>
3) Clone this repo<br/> 
`git clone <url>`
4) Create a virtual environment for the project<br/>
`virtualenv venv` and activate it `source venv/bin/activate`
5) Install the project's requirements<br/>
`pip install .` or `pip install -e ".[tests,lint]"` to install additional requirements for running tests and linting
6) Setup AWS CLI and GCloud CLI on your machine, configure the authentication
7) Set a variable in your environment `CLOUD_PROVIDER` to `AWS` or `gcloud`
8) Set a variable in your environment for the secret Flask key

## Run
Simply run the following command in your favorite terminal: `ftf_svc`<br/>
This entry point is provided by the `setup.py`.

## Test
- Pylint: `pylint -j 0 src/ --ignore='' --errors-only` `pylint -j 0 tests/ --ignore='' --errors-only`
- Flake8: `flake8 src/ --max-line-length=120 --per-file-ignores=''` `flake8 tests/ --max-line-length=120 --per-file-ignores=''`
- Black: `black --check src/` `black --check tests/`
- Pytest: `coverage run --source=src/ -m pytest tests/ -s -v --disable-pytest-warnings`
- Coverage Report: `coverage report --omit='' -m --fail-under=1`

## Build
1) Ensure you have Docker and can successfully build Docker's hello-world example
2) `docker build -t ftf_web_app -f src/docker/Dockerfile .`
3) `docker run --name ftf -p 8080:8080 -e FTF_SECRET_KEY="<some_secret_key>"-e CLOUD_PROVIDER="gcloud" -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/application/credentials -v $GOOGLE_APPLICATION_CREDENTIALS:/path/to/application/credentials -d ftf_web_app:latest`
4) `docker tag ftf_web_app:latest gcr.io/<CLOUD_PROJECT_NAME>/ftf_web_app`
5) `docker push gcr.io/<CLOUD_PROJECT_NAME>/ftf_web_app`

## Deploy
1) Ensure you have kubectl installed and properly configured with minikube running
2) `kubectl apply -f src/k8s/base/certificate.yml`
3) `kubectl apply -f src/k8s/base/secret.yml` (after generating a secret and filling in the value)
4) `kubectl apply -k src/k8s/prod`
5) `kubectl rollout status -w deployment/ftf-deployment`

## Use Skaffold to Build, Test, and Deploy
1) `kubectl config use-context minikube`
2) `kubectl config set-context --current --namespace=development`
3) `skaffold run --tail` 

    or 

1) `kubectl config use-context gke...`
2) `kubectl config set-context --current --namespace=production`
3) `skaffold run` or `skaffold run --tail`, which can be more helpful when troubleshooting

## Caveat
If you would actually like this to run for you, you'll need to get authentication tokens from me, which must
be on your machine for AWS or Google Cloud to work.
