from flask import Blueprint, render_template, request, redirect, session, abort
from supabase import create_client

SUPABASE_URL = "https://zrzoddxzskquxhkzftwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_bp = Blueprint('admin', __name__)

ADMIN_EMAILS = ["caitlintnathan2007@gmail.com"]

def require_admin():
    if "user" not in session or session["user"] not in ADMIN_EMAILS:
        abort(403)

@admin_bp.route("/admin")
def admin_panel():
    require_admin()
    pending_res = supabase.table("resources").select("*").eq("is_approved", False).execute()
    approved_res = supabase.table("resources").select("*").eq("is_approved", True).execute()
    return render_template("admin.html", pending=pending_res.data, approved=approved_res.data)

@admin_bp.route("/admin/approve/<resource_id>")
def approve_resource(resource_id):
    require_admin()
    supabase.table("resources").update({"is_approved": True}).eq("id", resource_id).execute()
    return redirect("/admin")

@admin_bp.route("/admin/reject/<resource_id>")
def reject_resource(resource_id):
    require_admin()
    supabase.table("resources").delete().eq("id", resource_id).execute()
    return redirect("/admin")