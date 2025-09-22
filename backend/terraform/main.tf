provider "aws" {
  region = "ap-northeast-2"
}

# source_sg(이름) → ID 조회 (있을 때만)
data "aws_security_group" "source_sg" {
  for_each = toset([
    for r in var.sg_rules : r.source_sg
    if try(r.source_sg, null) != null
  ])
  name   = each.value
  vpc_id = "vpc-0fc8c284cdbf5306d" # 실제 VPC ID
}

# SG 컨테이너만 관리 (인라인 ingress 없음)
resource "aws_security_group" "managed_sg" {
  for_each = var.managed_sg_names
  name     = each.value
  vpc_id   = "vpc-0fc8c284cdbf5306d" # 실제 VPC ID

  # 인바운드는 분리, 아웃바운드는 필요 시 유지
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = each.value }

  lifecycle {
    prevent_destroy = true                         # SG 본체 삭제 방지
    ignore_changes  = [ingress, description, revoke_rules_on_delete]  # ForceNew 요인 무시
  }
}

# 개별 규칙 리소스
resource "aws_security_group_rule" "ingress" {
  # for_each 키는 규칙의 자연키로 고정 (SG, proto, ports, source)
  for_each = {
    for r in var.sg_rules :
    format(
      "%s_%s_%d_%d_%s",
      r.target_sg, r.protocol, r.from_port, r.to_port,
      coalesce(try(r.source_ip, null), try(r.source_sg, "self"))
    ) => r
  }

  type              = "ingress"
  security_group_id = aws_security_group.managed_sg[each.value.target_sg].id
  protocol          = each.value.protocol
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  description       = try(each.value.description, "")

  # 소스는 CIDR 또는 SG ID
  cidr_blocks = try(each.value.source_ip, null) != null ? [each.value.source_ip] : null
  source_security_group_id = try(each.value.source_sg, null) != null
    ? data.aws_security_group.source_sg[each.value.source_sg].id
    : null

  lifecycle {
    create_before_destroy = false
  }
}
