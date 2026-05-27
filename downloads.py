from flask import Blueprint, redirect, session
from supabase import create_client

SUPABASE_URL = "https://zrzoddxzskquxhkzftwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

downloads_bp = Blueprint('downloads', __name__)

@downloads_bp.route("/download/<resource_id>")
def track_download(resource_id):
    if "user" not in session:
        return redirect("/login")

    try:
        # 1. Fetch current download record
        res = supabase.table("downloads").select("*").eq("resource_id", resource_id).execute()
        
        if res.data:
            new_count = res.data[0]["count"] + 1
            supabase.table("downloads").update({"count": new_count}).eq("resource_id", resource_id).execute()
        else:
            supabase.table("downloads").insert({"resource_id": resource_id, "count": 1}).execute()

        # 2. Get target URL to send the student to download page
        resource = supabase.table("resources").select("file_url").eq("id", int(resource_id)).execute()
        
        if resource.data and len(resource.data) > 0:
            return redirect(resource.data[0]["file_url"])
        else:
            print(f"Error: Could not find resource link for ID: {resource_id}")
            return f"Resource file link not found in database for ID {resource_id}.", 404

    except Exception as e:
        print("Download Tracking Exception error details:", e)
        return f"Download failed to initialize: {str(e)}", 500