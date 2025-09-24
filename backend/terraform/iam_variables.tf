variable "iam_users" {
  type = list(object({
    name                  = string
    path                  = optional(string, "/")
    tags                  = optional(map(string), {})
    force_destroy         = optional(bool, false)
    permissions_boundary  = optional(string)

    managed_policies = optional(list(string), [])
    inline_policies  = optional(list(object({
      name     = string
      document = any
    })), [])

    create_login_profile     = optional(bool, false)
    login_password           = optional(string)
    password_reset_required  = optional(bool, true)

    create_access_key = optional(bool, false)
    pgp_key           = optional(string)
  }))
  default = []
}
