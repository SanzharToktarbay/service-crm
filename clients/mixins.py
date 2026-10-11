class ManagerScopedMixin:
    """Сотрудник с доступом к админке видит всё, менеджер — только свои записи."""

    manager_field = "manager"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(**{self.manager_field: user})