locals {
  # for_each 키 (파이썬 auto-import 키와 동일)
  rules_map = {
    for r in var.sg_rules :
    "${r.target_sg}_${r.protocol}_${r.from_port}_${r.to_port}_${coalesce(r.source_ip, r.source_sg, "self")}" => r
  }

  source_sg_names = toset([
    for r in var.sg_rules : r.source_sg
    if try(r.source_sg, null) != null
  ])

  target_sg_names = toset(var.managed_sg_names)
}

# 소스 SG 이름 → ID
data "aws_security_group" "source" {
  for_each = local.source_sg_names
  name     = each.value
  vpc_id   = var.aws_vpc_id
}

# 타겟 SG 이름 → ID
data "aws_security_group" "target" {
  for_each = local.target_sg_names
  name     = each.value
  vpc_id   = var.aws_vpc_id
}

# 인바운드 규칙을 개별 리소스로 관리 (SG 삭제 없음)
resource "aws_security_group_rule" "ingress" {
  for_each = local.rules_map

  type              = "ingress"
  protocol          = each.value.protocol
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  description       = try(each.value.description, null)

  security_group_id = data.aws_security_group.target[each.value.target_sg].id

  cidr_blocks = try(each.value.source_ip, null) != null
    ? [each.value.source_ip]
    : null

  source_security_group_id = try(each.value.source_sg, null) != null
    ? data.aws_security_group.source[each.value.source_sg].id
    : null
}
