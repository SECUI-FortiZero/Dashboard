variable "iam_users" {
  type = list(object({
    name                 = string
    path                 = optional(string, "/")
    tags                 = optional(map(string), {})
    force_destroy        = optional(bool, false)
    permissions_boundary = optional(string)

    managed_policies = optional(list(string), [])
    inline_policies  = optional(list(object({
      name     = string
      document = any
    })), [])

    create_login_profile    = optional(bool, false)
    login_password          = optional(string)
    password_reset_required = optional(bool, true)

    create_access_key = optional(bool, false)
    pgp_key           = optional(string)
  }))
  default = []
}

variable "iam_groups" {
  type = list(object({
    name             = string
    path             = optional(string, "/")
    tags             = optional(map(string), {})
    managed_policies = optional(list(string), [])
    inline_policies  = optional(list(object({
      name     = string
      document = any
    })), [])
    members = optional(list(string), [])  # 이 그룹에 소속될 사용자 이름들
  }))
  default = []
}

variable "iam_user_group_memberships" {
  type = list(object({
    user   = string          # iam_users[].name 과 동일
    groups = list(string)    # 콘솔에 이미 존재하는 IAM 그룹 이름들
  }))
  default = []
}
