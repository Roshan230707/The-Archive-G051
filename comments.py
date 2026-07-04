from flask import Blueprint, request, redirect, session, render_template, abort
from supabase import create_client

SUPABASE_URL = "https://zrzoddxzskquxhkzftwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

comments_bp = Blueprint('comments', __name__)

@comments_bp.route("/resource/<resource_id>")
def view_resource(resource_id):
    if "user" not in session: return redirect("/login")
    
    try:
        res = supabase.table("resources").select("*").eq("id", resource_id).execute()
        if not res.data: return "Resource not found", 404
        
        comments_res = supabase.table("comments").select("*").eq("resource_id", resource_id).order("created_at", desc=True).execute()
        
        if comments_res.data:
            print("\n🔵 CURRENT COMMENT DATABASE KEYS LOOK LIKE THIS:", comments_res.data[0], "\n")
            
        return render_template("resource_details.html", resource=res.data[0], comments=comments_res.data)
    except Exception as e:
        print("🔴 ERROR LOADING COMMENTS PAGE:", str(e))
        return f"Error loading discussion page: {str(e)}", 500

@comments_bp.route("/resource/<resource_id>/comment", methods=["POST"])
def post_comment(resource_id):
    if "user" not in session: return redirect("/login")
    
    text = request.form.get("comment_text", "").strip()
    if text:
        try:
            supabase.table("comments").insert({
                "resource_id": resource_id, 
                "user_email": session["user"], 
                "comment_text": text
            }).execute()
        except Exception as e:
            print("🔴 ERROR POSTING COMMENT TO DATABASE:", str(e))
            
            try:
                supabase.table("comments").insert({
                    "resource_id": resource_id, 
                    "email": session["user"], 
                    "comment_text": text
                }).execute()
            except Exception as e2:
                print("🔴 BOTH COLUMN INSERT ATTEMPTS FAILED:", str(e2))
                return f"Database error while saving comment: {str(e2)}", 500
            
    return redirect(f"/resource/{resource_id}")

@comments_bp.route("/resource/<resource_id>/comment/<comment_id>/edit", methods=["POST"])
def edit_comment(resource_id, comment_id):
    if "user" not in session: return redirect("/login")
    
    new_text = request.form.get("comment_text", "").strip()
    if not new_text:
        return "Comment cannot be empty", 400
        
    try:
        comment_check = supabase.table("comments").select("*").eq("id", comment_id).execute()
        if not comment_check.data:
            return "Comment not found", 404
            
        comment_data = comment_check.data[0]
        owner_email = comment_data.get("user_email") or comment_data.get("email")
        
        is_admin = (
            session.get("is_admin") == True or 
            session.get("user") == "roshanvictor237@gmail.com" or 
            session.get("user") == "caitlintnathan2007@gmail.com"
        )
        
        if owner_email != session["user"] and not is_admin:
            abort(403)
            
        supabase.table("comments").update({"comment_text": new_text}).eq("id", comment_id).execute()
    except Exception as e:
        print("🔴 ERROR EDITING COMMENT:", str(e))
        return f"Database error while updating comment: {str(e)}", 500
        
    return redirect(f"/resource/{resource_id}")

@comments_bp.route("/resource/<resource_id>/comment/<comment_id>/delete")
def delete_comment(resource_id, comment_id):
    if "user" not in session: return redirect("/login")
    
    try:
        comment_check = supabase.table("comments").select("*").eq("id", comment_id).execute()
        if not comment_check.data:
            return "Comment not found", 404
            
        comment_data = comment_check.data[0]
        owner_email = comment_data.get("user_email") or comment_data.get("email")
        
        is_admin = (
            session.get("is_admin") == True or 
            session.get("user") == "roshanvictor237@gmail.com" or 
            session.get("user") == "caitlintnathan2007@gmail.com"
        )
        
        if owner_email != session["user"] and not is_admin:
            abort(403)
            
        supabase.table("comments").delete().eq("id", comment_id).execute()
    except Exception as e:
        print("🔴 ERROR DELETING COMMENT:", str(e))
        return f"Database error while deleting comment: {str(e)}", 500
        
    return redirect(f"/resource/{resource_id}")