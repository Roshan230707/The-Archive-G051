import os
from flask import Blueprint, request, redirect, session, render_template
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://zrzoddxzskquxhkzftwr.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

comments_bp = Blueprint('comments', __name__)

@comments_bp.route("/resource/<resource_id>")
def view_resource(resource_id):
    if "user" not in session: return redirect("/login")
    res = supabase.table("resources").select("*").eq("id", resource_id).execute()
    if not res.data: return "Resource not found", 404
    comments_res = supabase.table("comments").select("*").eq("resource_id", resource_id).order("created_at", desc=True).execute()
    return render_template("resource_details.html", resource=res.data[0], comments=comments_res.data)

@comments_bp.route("/resource/<resource_id>/comment", methods=["POST"])
def post_comment(resource_id):
    if "user" not in session: return redirect("/login")
    text = request.form.get("comment_text", "").strip()
    if text:
        supabase.table("comments").insert({"resource_id": resource_id, "user_email": session["user"], "comment_text": text}).execute()
    return redirect(f"/resource/{resource_id}")