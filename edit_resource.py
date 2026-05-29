from flask import Blueprint, render_template, request, redirect, session, abort
from supabase import create_client

SUPABASE_URL = "https://zrzoddxzskquxhkzftwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

edit_bp = Blueprint('edit_resource', __name__)

@edit_bp.route("/resource/<resource_id>/edit", methods=["GET", "POST"])
def edit_resource(resource_id):
    if "user" not in session:
        return redirect("/login")
        
 
    res = supabase.table("resources").select("*").eq("id", resource_id).execute()
    if not res.data:
        return "Resource not found", 404
        
    resource = res.data[0]
    
   
    if resource.get("uploaded_by") != session["user"]:
        abort(403) # Forbidden
        
    if request.method == "POST":
        updated_title = request.form["title"]
        updated_code = request.form["subject_code"]
        updated_category = request.form["category"]
        updated_url = request.form["file_url"]
        
    
        supabase.table("resources").update({
            "title": updated_title,
            "subject_code": updated_code,
            "category": updated_category,
            "file_url": updated_url,
            "is_approved": False 
        }).eq("id", resource_id).execute()
        
        return redirect("/")
        
    return render_template("edit_resource.html", resource=resource)