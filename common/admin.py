class CommonAdminMixin:
    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(CommonAdminMixin, self).get_readonly_fields(request, obj)
        readonly_fields += ('created_at', 'last_modified_at')
        return readonly_fields
