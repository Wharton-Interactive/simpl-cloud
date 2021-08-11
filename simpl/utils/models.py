from datetime import datetime
from typing import Any, Optional

from django.db import transaction
from django.utils import timezone


class DataMixin:
    def update_data(
        self, *, _save: bool = True, _now: Optional[datetime] = None, **kwargs
    ) -> list:
        """
        Update variable values (provided as keyword arguments).
        """
        modified = []
        if not kwargs:
            return modified
        if not hasattr(self, "modified_data"):
            self.modified_data = {}
            self.original_data = self.data.copy()
        now = _now or timezone.now()
        for key, value in kwargs.items():
            if key in self.data and self.data[key] == value:
                continue
            self.data[key] = value
            if key in self.original_data and self.original_data[key] == value:
                try:
                    del self.modified_data[key]
                except KeyError:
                    pass
            else:
                self.modified_data[key] = now
            modified.append(key)
        if _save:
            return self.save_data()
        return modified

    update_data.alters_data = True

    def save_data(self, *, keep_modified: bool = False) -> list:
        """
        Saves any pending data, fetching the latest data from the database first
        to avoid concurrency issues.
        """
        modified_data = getattr(self, "modified_data", None)
        if not modified_data:
            return []
        with transaction.atomic():
            new_data = self.data
            self.data = (
                self.__class__._default_manager.select_for_update()
                .filter(pk=self.pk)
                .values_list("data", flat=True)[0]
            )
            update_fields = {"data"}
            if "modified" in self._meta.fields:
                update_fields.add("modified")
            for key, now in modified_data.items():
                value = new_data[key]
                old_value = self.data.get(key)
                if key in self.data and old_value == value:
                    continue
                self.data[key] = value
                altered_fields = self.save_data_item(
                    key=key, value=value, old_value=old_value, now=now
                )
                if altered_fields:
                    update_fields |= altered_fields
            self.save(update_fields=update_fields)
        if keep_modified:
            self.original_data = self.data.copy()
        else:
            del self.modified_data
            del self.original_data
        return list(modified_data)

    save_data.alters_data = True

    def save_data_item(
        self, key: str, value: Any, old_value: Any, now: datetime
    ) -> Optional[set]:
        """
        A hook triggered whenever a data item is about to be saved.

        Should return a set of any fields altered.
        """
