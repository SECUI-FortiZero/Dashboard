locals {
  iam_users = var.iam_users
}

# IAM User
resource "aws_iam_user" "this" {
  for_each              = { for u in local.iam_users : u.name => u }
  name                  = each.value.name
  path                  = coalesce(try(each.value.path, null), "/")
  force_destroy         = try(each.value.force_destroy, false)
  permissions_boundary  = try(each.value.permissions_boundary, null)
  tags                  = try(each.value.tags, null)
}

# Managed Policy Attachments
resource "aws_iam_user_policy_attachment" "managed" {
  for_each = {
    for pair in flatten([
      for u in local.iam_users : [
        for p in try(u.managed_policies, []) : {
          key     = "${u.name}::${p}"
          user    = u.name
          policy  = p
        }
      ]
    ]) : pair.key => pair
  }

  user       = aws_iam_user.this[each.value.user].name
  policy_arn = each.value.policy
}

# Inline Policies
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

# (옵션) 콘솔 로그인 프로필
resource "aws_iam_user_login_profile" "this" {
  for_each = {
    for u in local.iam_users : u.name => u
    if try(u.create_login_profile, false)
  }

  user = aws_iam_user.this[each.key].name

  password_reset_required = try(each.value.password_reset_required, true)

  # password 미지정 시 AWS가 생성 + (보안 위해) PGP 키 요구하는 사용 예가 흔함
  # 필요하면 아래 2줄을 켜고 pgp_key 지정:
  # pgp_key = try(each.value.pgp_key, null)
  # password = try(each.value.login_password, null)
}

# (옵션) Access Key
resource "aws_iam_access_key" "this" {
  for_each = {
    for u in local.iam_users : u.name => u
    if try(u.create_access_key, false)
  }

  user   = aws_iam_user.this[each.key].name
  pgp_key = try(each.value.pgp_key, null) # 지정 시 secret이 암호화되어 출력됨
  # secret/encrypted_secret 등은 Terraform이 sensitive로 처리함
}
