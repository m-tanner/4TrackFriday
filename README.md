[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# [4 Track Friday](http://4trackfriday.com) Web App

This is the source code for hosting the back and front end of the Four Track Friday web application.
It uses Python and Flask for the back-end and Jinja2 for the front-end. Data for the app is stored in PostgreSQL. 
The app is deployed into a Google Kubernetes Engine cluster that I manage. It is deployed via a local Skaffold
pipeline, which you can inspect at `skaffold.yml`. This is all deployed live at [4trackfriday.com](http://4trackfriday.com).

## Setup

1) Install necessary software tools. For OS X, this is:<br/>
    ```
    brew install kubernetes-cli
    brew install kustomize
    brew install skaffold
    brew install terraform
    
    # Docker Desktop
    https://docs.docker.com/docker-for-mac/install/
    
    # Google Cloud Platform SDK
    https://cloud.google.com/sdk/docs/quickstart-macos
    
    # AWS SDK
    https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html
    ```
   
2) Clone this repo 
    ```
    git clone https://github.com/m-tanner/4TrackFriday.git
    ```

3) Create a virtual environment for the project
    ```
    virtualenv venv
    
    # and activate it
    source venv/bin/activate
    ```

4) Install the project's requirements
    ```
    pip install -r requirements.txt
    ```

5) Setup AWS CLI and GCloud CLI on your machine, configure the authentication

6) Setup your `bash_profile`, `bashrc`, or `zshrc`
    ```
    export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcloud/<CREDS>.json"
    export TF_VAR_GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcloud/<CREDS>.json"
    
    # This must be manually set to "AWS" or "gcloud" to determine what cloud provider to use
    # in any applications I've written that allow for the selection
    export CLOUD_PROVIDER="gcloud"
    
    export GCLOUD_PROJECT=<PROJECT>
    
    export STATIC_4TF_BUCKET=<BUCKET>
    export FTF_EMAIL_ADDRESS=<EMAIL>
    export FTF_EMAIL_PASSWORD=<PASSWORD>
    export TF_VAR_FTF_EMAIL_ADDRESS=<SAME AS FTF_EMAIL_ADDRESS>
    export TF_VAR_FTF_EMAIL_PASSWORD=<SAME AS FTF_EMAIL_PASSWORD>
    export ADMIN_EMAIL_ADDRESS=<ANOTHER EMAIL>
    export TF_VAR_SERVICE_ACCOUNT_EMAIL=<SERVICE ACCOUNT EMAIL>
    
    # Local Databases
    export DEV_DATABASE_URL="postgres://dev:dev@localhost:5432/dev"
    export TEST_DATABASE_URL="postgres://test:test@localhost:5431/test"
    
    # This is for flask and would need to change if the project structure changes
    export FLASK_CONFIG=dev
    export FLASK_ENV=developement
    export FLASK_DEBUG=1
    export FLASK_APP="src/app/four_track_friday.py"
    export FTF_SECRET_KEY=<A SECRET KEY>
    ```

7) Start two local databases, one for tests and one for dev
    ```
    # dev
    docker run --name ftf_postgres_dev -e POSTGRES_USER=dev -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:latest
   
    # test
    docker run --name ftf_postgres_test -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -p 5431:5432 -d postgres:latest
   
    # OR use the local_stack.yml
    docker-compose -f src/docker/local_stack.yml up
   
    # for help
    https://hub.docker.com/_/postgres
    ```

8) To connect to shell inside the running container if necessary
    ```
    docker exec -it ftf_postgres_dev /bin/bash
    ```

9) If this is your first time creating the database(s), you will need to initialize them
    ```
    (venv) user@machine 4TrackFriday % export FLASK_CONFIG=dev
    (venv) user@machine 4TrackFriday % flask shell
    >>> db.drop_all()
    >>> db.create_all()
    >>> exit()
    (venv) user@machine 4TrackFriday % flask db upgrade
    ```
   
10) Ensure that you can get the tests to pass
    ```
    (venv) user@machine 4TrackFriday % flask test
    ```

11) Start Kubernetes using Docker Desktop NOT minikube
    ```
    # follow instructions here
    https://docs.docker.com/docker-for-mac/kubernetes/
    
    # ensure that, under Resources > File Sharing, you've mounted $HOME
    
    # the old minikube command I used was 
    minikube start --driver hyperkit --kubernetes-version v1.16.12 --addons ingress --mount-string "$HOME:$HOME" --mount
    ```

12) Setup Kubernetes
    ```
    kubectl create namespace development
    kubectl config set-context --current --namespace=development
    
    # https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
    
    # https://kubernetes.github.io/ingress-nginx/deploy/#docker-for-mac
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.34.1/deploy/static/provider/cloud/deploy.yaml
    ```
    
13) Congrats! You're ready to deploy the app!

## Deploy to Kubernetes locally
```
1) kubectl config use-context docker-desktop
2) kubectl config set-context --current --namespace=development
3) kubectl apply -f src/k8s/dev/secret.yml
4) skaffold run
    # trailing the logs can be helpful when troubleshooting
    # skaffold run --trail
```

## Deploy to Kubernetes in the cloud
```
1) kubectl config use-context gke...
2) kubectl config set-context --current --namespace=<staging or production>
3) kubectl apply -f src/k8s/<stg or prod>/secret.yml
4) kubectl apply -f src/k8s/base/certificate.yml
3) skaffold run
    # trailing the logs can be helpful when troubleshooting
    # skaffold run --trail
```

## Run locally without Kubernetes
1) Simply run the following command in your favorite terminal: 
    ```
    (venv) user@machine 4TrackFriday % ftf_svc
    # This entry point is provided by the setup.py
    ```

## Test locally
1) Simply run the following commands in your favorite terminal:
    ```
    # pylint
    (venv) user@machine 4TrackFriday % pylint -j 0 src/ --ignore='' --errors-only` `pylint -j 0 tests/ --ignore='' --errors-only
   
    # flake8
    (venv) user@machine 4TrackFriday % flake8 src/ --max-line-length=120 --per-file-ignores=''` `flake8 tests/ --max-line-length=120 --per-file-ignores=''
   
    # black
    (venv) user@machine 4TrackFriday % black --check src/` `black --check tests/
   
    # pytest
    (venv) user@machine 4TrackFriday % coverage run --source=src/ -m pytest tests/ -s -v --disable-pytest-warnings
   
    # coverage
    (venv) user@machine 4TrackFriday % coverage report --omit='' -m --fail-under=1
    ```

## Build
1) To build locally, tag, and push to a remote container registry
    ```
    # from the project root directory
    (venv) user@machine 4TrackFriday % docker build -t ftf_web_app -f src/docker/Dockerfile .
   
    (venv) user@machine 4TrackFriday % docker run --name ftf -p 8080:8080 -e <all the env vars described in the bash profile section> -v $GOOGLE_APPLICATION_CREDENTIALS:/path/to/application/credentials -d ftf_web_app:latest
   
    (venv) user@machine 4TrackFriday % docker tag ftf_web_app:latest gcr.io/<CLOUD_PROJECT_NAME>/ftf_web_app
   
    (venv) user@machine 4TrackFriday % docker push gcr.io/<CLOUD_PROJECT_NAME>/ftf_web_app
    ``` 

## Related Infrastructure
1) I use Terraform to declare and deploy infrastructure
2) Build Four Track Friday's required cloud functions
    ```
    # if dependencies are required
    (venv) mtanner@Michaels-MBP cloud_functions % pip install -r requirements.txt -t .
    
    # always plan first!
    (venv) mtanner@Michaels-MBP terraform % terraform plan
   
    # then apply, check again before typing "yes"
    (venv) mtanner@Michaels-MBP terraform % terraform apply
    ``` 

## Use Skaffold to Build, Test, and Deploy
1) `kubectl config use-context docker-desktop`
2) `kubectl config set-context --current --namespace=development`
3) `skaffold run` or `skaffold run --trail`, which can be more helpful when troubleshooting

    or 

1) `kubectl config use-context gke...`
2) `kubectl config set-context --current --namespace=production`
3) `skaffold run` or `skaffold run --trail`, which can be more helpful when troubleshooting

    or for staging
    
1) `kubectl config use-context gke...`
2) `kubectl config set-context --current --namespace=staging`
3) `skaffold dev` or `skaffold dev --trail`, which can be more helpful when troubleshooting

## Caveat
If you would actually like to run, you'll need to get authentication tokens from me, which must
be on your machine for AWS, Google Cloud, and Heroku to work.
