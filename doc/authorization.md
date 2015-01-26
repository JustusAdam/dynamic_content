# TLDR
- Decorate your controller function with `@authorize(permission)`. 
- assign `permission` to the control group (id=0)
- assign `permission` to groups you wish to have access via the admin interface at /permissions

# Client information

Information about the client can be found in the DynamicContent instance you controller is being called with by accessing the `client` field of the `request` field.

The field contains an instance of `dyc.modules.users.client.Information` which provides a `check_permission(self, permission)` method, which can be used to check whether a specific `permission` has been assigned to the group this user belongs to.
  
# Decorator

The module `dyc.modules.user` also provides a `@authorize(permission)` decorator in the `dyc.modules.user.decorator` module. On every request to this controller the decorator will call `check_permission` as described above to authorize the user with the given permission. 