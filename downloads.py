from flask import Blueprint, redirect, session, send_file, abort
from supabase import create_client
import requests
import io
from werkzeug.utils import secure_filename

SUPABASE_URL = "https://zrzoddxzskquxhkzftwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

downloads_bp = Blueprint('downloads', __name__)

@downloads_bp.route("/download/<resource_id>")
def track_download(resource_id):
    if "user" not in session:
        return redirect("/login")

    try:
       
        res = supabase.table("downloads").select("*").eq("resource_id", resource_id).execute()
        
        if res.data:
            new_count = res.data[0]["count"] + 1
            supabase.table("downloads").update({"count": new_count}).eq("resource_id", resource_id).execute()
        else:
            supabase.table("downloads").insert({"resource_id": resource_id, "count": 1}).execute()

  
        resource = supabase.table("resources").select("file_url", "title").eq("id", int(resource_id)).execute()
        
        if not resource.data:
            print(f"Error: Could not find resource link for ID: {resource_id}")
            return f"Resource file link not found in database.", 404
            
        file_url = resource.data[0]["file_url"]
        original_title = resource.data[0]["title"]

        
        file_response = requests.get(file_url)
        if file_response.status_code != 200:
            return "Could not retrieve file from storage provider", 500

        
        file_extension = file_url.split('.')[-1].split('?')[0]
        clean_filename = f"{secure_filename(original_title)}.{file_extension}"

       
        return send_file(
            io.BytesIO(file_response.content),
            mimetype=file_response.headers.get('Content-Type'),
            as_attachment=True,          # <-- This line forces the download dialog window!
            download_name=clean_filename
        )

    except Exception as e:
        print("Download Tracking Exception error details:", e)
        return f"Download failed to initialize: {str(e)}", 500