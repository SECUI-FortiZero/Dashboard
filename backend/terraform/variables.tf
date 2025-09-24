variable "aws_region" {
  type    = string
  default = "ap-northeast-2"
}

variable "aws_vpc_id" {
  type = string
}

variable "managed_sg_names" {
  description = "관리 대상 SG 이름 목록"
  type        = list(string)
}

variable "sg_rules" {
  description = "인바운드 규칙 목록"
  type = list(object({
    target_sg   = string
    protocol    = string
    from_port   = number
    to_port     = number
    source_ip   = optional(string)
    source_sg   = optional(string)
    description = optional(string)
  }))
}
