variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "us-central1"
}
variable "image" {
  type        = string
  description = "Container image, e.g. us-central1-docker.pkg.dev/PROJECT/studioclear/app:latest"
}
variable "parallel_api_key" {
  type      = string
  sensitive = true
}
variable "gemini_api_key" {
  type      = string
  sensitive = true
}
