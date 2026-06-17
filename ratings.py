import os
from flask import Blueprint, request, redirect, session
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://zrzoddxzskquxhkzftwr.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ratings_bp = Blueprint('ratings', __name__)

@ratings_bp.route("/resource/<resource_id>/rate", methods=["POST"])
def rate_resource(resource_id):
    if "user" not in session:
        return redirect("/login")
        
    rating_val = request.form.get("rating")
    if rating_val and rating_val.isdigit():
        rating_val = int(rating_val)
        if 1 <= rating_val <= 5:
            try:
                supabase.table("ratings").upsert({
                    "resource_id": int(resource_id),
                    "user_email": session["user"],
                    "rating": rating_val
                }, on_conflict="resource_id,user_email").execute()
            except Exception:
                pass
                
    return redirect(f"/resource/{resource_id}")