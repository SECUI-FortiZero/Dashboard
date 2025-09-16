provider "aws" {
  region = "ap-northeast-2"
}

resource "aws_security_group" "managed_sg" {
  for_each    = var.security_group_rules
  name        = each.key
  description = "Managed by Hybrid Firewall System"

  dynamic "ingress" {
    for_each = each.value
    content {
      description = ingress.value.description
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = each.key
  }
}