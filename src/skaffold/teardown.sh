#!/bin/zsh

find ./src/k8s/base              -type f -exec sed -i "" "s|$CLOUD_PROJECT|@CLOUD_PROJECT@|g"                                   {} \;
find ./src/skaffold              -type f -exec sed -i "" "s|$KUBECONTEXT|@KUBECONTEXT@|g"                                       {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$GOOGLE_APPLICATION_CREDENTIALS|@GOOGLE_APPLICATION_CREDENTIALS@|g" {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$CLOUD_PROVIDER|@CLOUD_PROVIDER@|g"                                 {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$GCLOUD_PROJECT|@GCLOUD_PROJECT@|g"                                 {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$STATIC_4TF_BUCKET|@STATIC_4TF_BUCKET@|g"                           {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$TEST_DATABASE_URL|@TEST_DATABASE_URL@|g"                           {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$FTF_EMAIL_ADDRESS|@FTF_EMAIL_ADDRESS@|g"                           {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$FTF_EMAIL_PASSWORD|@FTF_EMAIL_PASSWORD@|g"                         {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$ADMIN_EMAIL_ADDRESS|@ADMIN_EMAIL_ADDRESS@|g"                       {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$FLASK_CONFIG|@FLASK_CONFIG@|g"                                     {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$FLASK_ENV|@FLASK_ENV@|g"                                           {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$FLASK_DEBUG|@FLASK_DEBUG@|g"                                       {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$FLASK_APP|@FLASK_APP@|g"                                           {} \;
find ./tests/container-structure -type f -exec sed -i "" "s|$FTF_SECRET_KEY|@FTF_SECRET_KEY@|g"                                 {} \;