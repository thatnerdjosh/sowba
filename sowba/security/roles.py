class Role(str):
    """
    Role("user") == "role:sowba.User"
    """

    def __init__(self, role: str):
        self.role = role

    def __str__(self):
        return f"role:sowba.{self.role.capitalize()}"

    def __repr__(self):
        return f"role:sowba.{self.role.capitalize()}"

    def __eq__(self, value):
        return value == f"role:sowba.{self.role.capitalize()}"


user = Role("user")
root = Role("root")
admin = Role("admin")
