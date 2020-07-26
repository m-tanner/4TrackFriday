variable "GOOGLE_APPLICATION_CREDENTIALS" {}

variable "FTF_EMAIL_ADDRESS" {}

variable "FTF_EMAIL_PASSWORD" {}

variable "SERVICE_ACCOUNT_EMAIL" {}

variable "FUNCTION_NAME" {
  default = "ftf_send_email"
  description = "the name of the cloud function and simultaneously the invoked function"
}