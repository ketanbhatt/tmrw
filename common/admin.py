class CommonAdminMixin:
    def has_delete_permission(self, request, obj=None):
        return False

    common_readonly = ('created_at', 'last_modified_at')
