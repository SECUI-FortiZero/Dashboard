locals {
  iam_users  = var.iam_users
  iam_groups = var.iam_groups
}

# ── Users ────────────────────────────────────────────────────────────────────
resource "aws_iam_user" "this" {
  for_each              = { for u in local.iam_users : u.name => u }
  name                  = each.value.name
  path                  = coalesce(try(each.value.path, null), "/")
  force_destroy         = try(each.value.force_destroy, false)
  permissions_boundary  = try(each.value.permissions_boundary, null)
  tags                  = try(each.value.tags, null)
}

resource "aws_iam_user_policy_attachment" "managed" {
  for_each = {
    for pair in flatten([
      for u in local.iam_users : [
        for p in try(u.managed_policies, []) : {
          key    = "${u.name}::${p}"
          user   = u.name
          policy = p
        }
      ]
    ]) : pair.key => pair
  }
  user       = aws_iam_user.this[each.value.user].name
  policy_arn = each.value.policy
}

resource "aws_iam_user_policy" "inline" {
  for_each = {
    for pair in flatten([
      for u in local.iam_users : [
        for ip in try(u.inline_policies, []) : {
          key      = "${u.name}::${ip.name}"
          user     = u.name
          name     = ip.name
          document = ip.document
        }
      ]
    ]) : pair.key => pair
  }
  user   = aws_iam_user.this[each.value.user].name
  name   = each.value.name
  policy = jsonencode(each.value.document)
}

resource "aws_iam_user_login_profile" "this" {
  for_each = {
    for u in local.iam_users : u.name => u
    if try(u.create_login_profile, false)
  }
  user                     = aws_iam_user.this[each.key].name
  password_reset_required  = try(each.value.password_reset_required, true)
  # pgp_key  = try(each.value.pgp_key, null)
  # password = try(each.value.login_password, null)
}

resource "aws_iam_access_key" "this" {
  for_each = {
    for u in local.iam_users : u.name => u
    if try(u.create_access_key, false)
  }
  user   = aws_iam_user.this[each.key].name
  pgp_key = try(each.value.pgp_key, null)
}

# ── Groups ───────────────────────────────────────────────────────────────────
resource "aws_iam_group" "this" {
  for_each = { for g in local.iam_groups : g.name => g }
  name     = each.value.name
  path     = coalesce(try(each.value.path, null), "/")
  tags     = try(each.value.tags, null)
}

resource "aws_iam_group_policy_attachment" "managed" {
  for_each = {
    for pair in flatten([
      for g in local.iam_groups : [
        for p in try(g.managed_policies, []) : {
          key    = "${g.name}::${p}"
          group  = g.name
          policy = p
        }
      ]
    ]) : pair.key => pair
  }
  group      = aws_iam_group.this[each.value.group].name
  policy_arn = each.value.policy
}

resource "aws_iam_group_policy" "inline" {
  for_each = {
    for pair in flatten([
      for g in local.iam_groups : [
        for ip in try(g.inline_policies, []) : {
          key      = "${g.name}::${ip.name}"
          group    = g.name
          name     = ip.name
          document = ip.document
        }
      ]
    ]) : pair.key => pair
  }
  group  = aws_iam_group.this[each.value.group].name
  name   = each.value.name
  policy = jsonencode(each.value.document)
}

# 그룹 전체 멤버십(목록을 "소유"함)
resource "aws_iam_group_membership" "members" {
  for_each = { for g in local.iam_groups : g.name => g }
  name  = "membership-${each.value.name}"
  group = aws_iam_group.this[each.key].name
  users = [
    for u in try(each.value.members, []) :
    aws_iam_user.this[u].name
  ]
}

# 기존 그룹 “이름”에 유저를 소속 (그룹을 생성하지 않음)
resource "aws_iam_user_group_membership" "by_user" {
  for_each = {
    for m in var.iam_user_group_memberships : m.user => m
  }

  user   = aws_iam_user.this[each.value.user].name
  groups = each.value.groups
}
