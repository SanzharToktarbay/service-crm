def scope_for_user(queryset, user, field="manager"):
    """Сотрудник с доступом к админке видит всё, менеджер — только свои записи."""
    if user.is_staff:
        return queryset
    return queryset.filter(**{field: user})


class ManagerScopedMixin:
    manager_field = "manager"

    def get_queryset(self):
        return scope_for_user(super().get_queryset(), self.request.user, self.manager_field)