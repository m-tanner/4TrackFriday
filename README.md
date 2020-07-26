[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# [4 Track Friday](http://4trackfriday.com) Web App

This is the source code for hosting the back and front end of the Four Track Friday web application.
It uses Python and Flask for the back-end and Jinja2 for the front-end. Data for the app is stored 
in Google Cloud and/or AWS.
The app is able to use either data store, configurable by environment variable.
SQL data is stored using Heroku. 
The app is deployed into a Google Kubernetes Engine cluster that I manage. It is deployed via a local Skaffold
pipeline, which you can inspect at `skaffold.yml`. This is all deployed live at [4trackfriday.com](http://4trackfriday.com).

## Setup Instructions
1) Install necessary software tools. For OS X, this is:<br/>
`brew install kubernetes-cli`<br/>
`brew install kustomize`<br/>
`brew install minikube`<br/>
`brew install skaffold`<br/>
`brew tap heroku/brew && brew install heroku`<br/>
`https://cloud.google.com/sdk/docs/quickstart-macos`<br/>
`https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html`<br/>
2a) Start minikube with the same version as the GKE cluster<br/>
`minikube start --driver=hyperkit --kubernetes-version=v1.16.12 --mount-string="$HOME/path/to/creds.json:/hosthome/creds.json" --mount`<br/>
`kubectl create namespace development`
`minikube addons enable ingress`
2b) See the pretty UI by running<br/>
`minikube dashboard`
3) Clone this repo<br/> 
`git clone <url>`
4) Create a virtual environment for the project<br/>
`virtualenv venv` and activate it `source venv/bin/activate`
5) Install the project's requirements<br/>
`pip install -r requirements.txt`
6) Setup AWS CLI and GCloud CLI on your machine, configure the authentication
7) Setup your `bash_profile`, `bashrc`, or `zshrc`
```$xslt
# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/<user>/Applications/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/<user>/Applications/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/<user>/Applications/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/<user>/Applications/google-cloud-sdk/completion.zsh.inc'; fi

export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials"

# This must be manually set to "AWS" or "gcloud" to determine what cloud provider to use
# in any applications I've written that allow for the selection
export CLOUD_PROVIDER="<AWS or gcloud>"

export GCLOUD_PROJECT="<name of project>"
export STATIC_4TF_BUCKET="path.to.bucket"

export FTF_EMAIL_ADDRESS="<email address>"
export FTF_EMAIL_PASSWORD="<email password>"

# These are apps in Heroku
export DATABASE_URL=$(heroku config:get DATABASE_URL -a <app-name>)
export DEV_DATABASE_URL=$(heroku config:get DATABASE_URL -a <app-name>)
export TEST_DATABASE_URL=$(heroku config:get DATABASE_URL -a <app-name>)

# This is for flask and would need to change if the project structure changes
export FLASK_CONFIG=“<development/production/testing>”
export FLASK_DEBUG=1
export FLASK_APP="path/to/four_track_friday.py"
export FTF_SECRET_KEY="<some wicked string>"
```
8) To view the Heroku-stored DB's in Intellij follow [this guide](https://www.jetbrains.com/help/datagrip/how-to-connect-to-heroku-postgres.html)
8) You could also run a local instance of MySQL and update the database URL's to point locally, I recommend PostgreSQL
For instructions on how to do this, see [Docker's Postgres documentation](https://hub.docker.com/_/postgres)
`docker run --name ftf_postgres_dev -e POSTGRES_USER=dev -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:latest`
Swapping out `dev` for `test` or `prod` would allow you to locally reproduce different environments
To have all three running at once, be sure to map non-conflicting ports, i.e.
`docker run --name ftf_postgres_test -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -p 5431:5432 -d postgres:latest`
`docker run --name ftf_postgres_prod -e POSTGRES_USER=prod -e POSTGRES_PASSWORD=prod -p 5433:5432 -d postgres:latest`
To connect to shell inside the running container:
`docker exec -it ftf_postgres_dev /bin/bash`
OR
`docker-compose -f src/docker/local_stack.yml up`
This then requires your bash profile to look like:
```bash
export DATABASE_URL="postgres://prod:prod@localhost:5433/prod"
export DEV_DATABASE_URL="postgres://dev:dev@localhost:5432/dev"
export TEST_DATABASE_URL="postgres://test:test@localhost:5431/test"
```
If this is your first time creating the database(s), you will need to initialize them by doing the following
```bash
(venv) user@machine 4TrackFriday % export FLASK_CONFIG=dev
(venv) user@machine 4TrackFriday % flask shell
>>> db.drop_all()
>>> db.create_all()
>>> exit()
(venv) user@machine 4TrackFriday % flask db upgrade
```
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

## Cloud Functions
`(venv) mtanner@Michaels-MBP cloud_functions % pip install -r requirements.txt -t .`

## Deploy
1) Ensure you have kubectl installed and properly configured with minikube running
2) `kubectl apply -f src/k8s/base/certificate.yml`
3) `kubectl apply -f src/k8s/base/secret.yml` (after generating a secret and filling in the value)
4) `kubectl apply -k src/k8s/prod`
5) `kubectl rollout status -w deployment/ftf-deployment`

## Use Skaffold to Build, Test, and Deploy
1) `kubectl config use-context minikube`
2) `kubectl config set-context --current --namespace=development`
3) `skaffold run --trail` 

    or 

1) `kubectl config use-context gke...`
2) `kubectl config set-context --current --namespace=production`
3) `skaffold run` or `skaffold run --trail`, which can be more helpful when troubleshooting

## Caveat
If you would actually like to run, you'll need to get authentication tokens from me, which must
be on your machine for AWS, Google Cloud, and Heroku to work.
