# SG 컨테이너 (인라인 ingress 없음)
resource "aws_security_group" "managed_sg" {
  for_each = toset(var.managed_sg_names)
  name     = each.value
  vpc_id   = var.aws_vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = each.value }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [ingress, description, revoke_rules_on_delete]
  }
}

# 개별 인바운드 규칙
resource "aws_security_group_rule" "ingress" {
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

  # 반드시 한 줄 삼항식으로!
  cidr_blocks              = try(each.value.source_ip, null) != null ? [each.value.source_ip] : null
  source_security_group_id = try(each.value.source_sg, null) != null ? data.aws_security_group.source_sg[each.value.source_sg].id : null

  lifecycle {
    create_before_destroy = false
  }
}
