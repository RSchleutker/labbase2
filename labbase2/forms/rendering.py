__all__ = ["custom_field", "select_field", "file_field", "submit_field"]


custom_field: dict[str, str] = {"class": "form-control form-control-sm"}
select_field: dict[str, str] = {"class": "form-select form-select-sm", "size": 1}
boolean_field: dict[str, str] = {"class": "form-check-input"}
file_field: dict[str, str] = {"class": "form-control form-control-sm"}
submit_field: dict[str, str] = {"class": "btn btn-sm btn-primary"}
