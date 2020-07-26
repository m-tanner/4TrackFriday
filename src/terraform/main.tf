terraform {
  backend "gcs" {
    bucket = "terraform.4trackfriday.com"
    prefix = "terraform/state"
  }

  required_version = "~> 0.12.29"

  required_providers {
    google  = "~> 3.31"
    archive = "~> 1.3"
  }
}

provider "google" {
  credentials = file(var.GOOGLE_APPLICATION_CREDENTIALS)
  project = "four-track-friday-2"
  version = "~> 3.31"
}

resource "google_storage_bucket" "bucket" {
  name = "cloud.4trackfriday.com"
}

data "archive_file" "source" {
  # before this will work, run
  # pip install -r requirements.txt
  # inside src/cloud_functions
  type = "zip"
  output_path = "../cloud_functions/${var.FUNCTION_NAME}-${formatdate("YYMMDDhhmmss", timestamp())}.zip"
  source_dir = "../cloud_functions"
}

resource "google_storage_bucket_object" "archive" {
  name   = "${var.FUNCTION_NAME}.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.source.output_path
}

resource "google_cloudfunctions_function" "function" {
  name                  = "${var.FUNCTION_NAME}-${formatdate("YYMMDDhhmmss", timestamp())}"
  description           = "send emails from the 4tf email address"
  runtime               = "python37"
  region                = "us-central1"
  https_trigger_url     = "https://4trackfriday.cloudfunctions.net/${var.FUNCTION_NAME}"

  available_memory_mb   = 128
  trigger_http          = true
  ingress_settings      = "ALLOW_ALL"
  service_account_email = var.SERVICE_ACCOUNT_EMAIL
  timeout               = 5
  entry_point           = "send_email"
  max_instances         = 2

  environment_variables = {
    FTF_EMAIL_ADDRESS   = var.FTF_EMAIL_ADDRESS
    FTF_EMAIL_PASSWORD  = var.FTF_EMAIL_PASSWORD
  }

  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

output "endpoint" {
  value = google_cloudfunctions_function.function.https_trigger_url
}