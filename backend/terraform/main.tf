provider "aws" {
  region = "ap-northeast-2"
}

# YAML에 source_sg로 명시된 보안 그룹의 ID를 이름으로 찾기 위한 데이터 소스
data "aws_security_group" "source_sg_data" {
  # --- [수정된 부분 시작] ---
  # distinct() 함수를 사용하여 YAML 파일에 source_sg가 여러 번 나와도 고유한 이름만 사용하도록 보장
  for_each = toset(distinct([
    for rule in flatten([for sg_rules in var.security_group_rules : sg_rules]) : rule.source_sg if try(rule.source_sg, null) != null
  ]))
  # --- [수정된 부분 끝] ---
  name = each.value
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
      
     # --- [수정된 부분 시작] ---
      cidr_blocks     = try(ingress.value.source_ip, null) != null ? [ingress.value.source_ip] : null
      # 'source_security_group_id' -> 'security_groups' 로 변경하고, 값을 리스트 [ ] 로 감싸줍니다.
      security_groups = try(ingress.value.source_sg, null) != null ? [data.aws_security_group.source_sg_data[ingress.value.source_sg].id] : null
      # --- [수정된 부분 끝] ---
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