# source_sg(이름) -> ID 조회 (있을 때만)
data "aws_security_group" "source_sg" {
  for_each = toset(distinct([
    for r in var.sg_rules : r.source_sg
    if try(r.source_sg, null) != null
  ]))
  name   = each.value
  vpc_id = var.aws_vpc_id
}
