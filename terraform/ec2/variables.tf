variable "aws_region" {
  default = "eu-central-1"
}

variable "ami_id" {
  description = "Amazon Machine Image ID"
  default     = "ami-03250b0e01c28d196"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "key_name" {
  description = "Name of your EC2 Key Pair"
  type        = string
}
