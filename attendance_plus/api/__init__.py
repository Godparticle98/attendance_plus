def test_desktop_page():
    import frappe
    import json
    from frappe.desk.desktop import get_desktop_page
    page_data = frappe.get_doc("Workspace", "Attendance Plus")
    res = get_desktop_page(json.dumps(page_data.as_dict(convert_dates_to_str=True)))
    return {
        "number_cards": [c.get("label") for c in res.get("number_cards", {}).get("items", [])],
        "shortcuts": [s.get("label") for s in res.get("shortcuts", {}).get("items", [])],
    }
