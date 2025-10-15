variable "security_group_rules" {
  description = "A map where keys are security group names and values are lists of ingress rules."
  type = map(list(object({
    description = string
    protocol    = string
    from_port   = number
    to_port     = number
    cidr_blocks = list(string)
  })))
  default = {}
}