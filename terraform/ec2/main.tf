provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "demo" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  root_block_device {
    volume_size = 40       # Set root volume to 40 GB
    volume_type = "gp2"
  }

  tags = {
    Name = "test_finops"
    CostId = "finops-demo"
    Owner = "p.naik@reply.de"
  }
}
