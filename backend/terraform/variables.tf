variable "security_group_rules" {
  description = "A map where keys are security group names and values are lists of ingress rules."
  type = map(list(object({
    description = string
    protocol    = string
    from_port   = number
    to_port     = number
    # source_ip와 source_sg를 선택적(Optional) 속성으로 변경합니다.
    source_ip   = optional(string)
    source_sg   = optional(string)
  })))
  default = {}
}