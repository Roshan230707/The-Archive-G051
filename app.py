import os
import time  
from flask import Flask, render_template, request, redirect, session
from supabase import create_client
from werkzeug.utils import secure_filename 

from auth import auth_bp            
from downloads import downloads_bp  
from admin import admin_bp
from comments import comments_bp
from edit_resource import edit_bp
from ratings import ratings_bp

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key")  

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://zrzoddxzskquxhkzftwr.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_avg_ratings():
    try:
        data_res = supabase.table("ratings").select("resource_id, rating").execute()
        if not data_res.data:
            return {}
            
        averages = {}
        counts = {}
        for row in data_res.data:
            
            r_id = str(row["resource_id"]).strip()
            averages[r_id] = averages.get(r_id, 0) + row["rating"]
            counts[r_id] = counts.get(r_id, 0) + 1
        return {r_id: round(averages[r_id] / counts[r_id], 1) for r_id in averages}
    except Exception:
        return {}

@app.route("/")
def home():
    if "user" not in session:  
        return redirect("/login")

    response = supabase.table("resources").select("*").eq("is_approved", True).execute()
    resources = response.data
    
    counts_res = supabase.table("downloads").select("*").execute()
    counts = {str(item["resource_id"]): item["count"] for item in counts_res.data}
    
    raw_ratings = get_avg_ratings()
   
    ratings = {str(k): v for k, v in raw_ratings.items()}
    
    return render_template("index.html", resources=resources, counts=counts, ratings=ratings)

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    title = request.form["title"]
    subject_code = request.form["subject_code"]
    category = request.form["category"]
    
    
    if 'resource_file' not in request.files:
        return "Form setup issue: File part missing.", 400
        
    file = request.files['resource_file']
    
    if file.filename == '':
        return "No file selected in picker selection", 400

    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        
        try:
           
            file_data = file.read()
            supabase.storage.from_("resources").upload(
                path=unique_filename,
                file=file_data,
                file_options={"content-type": file.content_type}
            )
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/resources/{unique_filename}"
            
        except Exception as e:
            return f"Supabase Storage Engine upload failure: {str(e)}", 500

       
        supabase.table("resources").insert({
            "title": title,
            "subject_code": subject_code,
            "category": category,
            "file_url": file_url,
            "is_approved": False,
            "uploaded_by": session["user"] 
        }).execute()

    return redirect("/")

@app.route("/search")
def search():
    if "user" not in session:
        return redirect("/login")

    query = request.args.get("query", "")
    category = request.args.get("category", "all")

    db_query = supabase.table("resources").select("*").ilike("subject_code", f"%{query}%").eq("is_approved", True)

    if category != "all":
        db_query = db_query.eq("category", category)

    response = db_query.execute()
    resources = response.data
    
    counts_res = supabase.table("downloads").select("*").execute()
    counts = {str(item["resource_id"]): item["count"] for item in counts_res.data}
    
    raw_ratings = get_avg_ratings()
    ratings = {str(k): v for k, v in raw_ratings.items()}
    
    return render_template("index.html", resources=resources, counts=counts, ratings=ratings)

app.register_blueprint(auth_bp)
app.register_blueprint(downloads_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(edit_bp)
app.register_blueprint(ratings_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)