variable "aws_vpc_id" { type = string }

variable "managed_sg_names" {
  type    = list(string)
  default = []
}

variable "sg_rules" {
  type = list(object({
    target_sg   = string
    protocol    = string
    from_port   = number
    to_port     = number
    source_ip   = optional(string)
    source_sg   = optional(string)
    description = optional(string)
  }))
  default = []
}
