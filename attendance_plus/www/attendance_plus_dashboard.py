import frappe
import os

no_cache = 1

def get_context(context):
    csrf_token = frappe.sessions.get_csrf_token()
    
    frontend_path = frappe.get_app_path('attendance_plus', 'public', 'frontend', 'index.html')
    
    with open(frontend_path, 'r') as f:
        html = f.read()

    # Inject frappe boot into the HTML
    boot_script = f"""
    <script>
        window.frappe = window.frappe || {{}};
        window.frappe.csrf_token = '{csrf_token}';
    </script>
    """
    
    html = html.replace('</head>', f'{boot_script}</head>')
    context.html = html
