from flask import Flask, render_template, request, redirect, session
from supabase import create_client
from auth import auth_bp            
from downloads import downloads_bp  

app = Flask(__name__)
app.secret_key = "super-secret-key"  

SUPABASE_URL = "https://zrzoddxzskquxhkzftwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# HOME PAGE
@app.route("/")
def home():
    if "user" not in session:  
        return redirect("/login")

    response = supabase.table("resources").select("*").execute()
    resources = response.data
    
    counts_res = supabase.table("downloads").select("*").execute()
    counts = {str(item["resource_id"]): item["count"] for item in counts_res.data}

    return render_template("index.html", resources=resources, counts=counts)

# UPLOAD RESOURCE
@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    title = request.form["title"]
    subject_code = request.form["subject_code"]
    category = request.form["category"]
    file_url = request.form["file_url"]

    supabase.table("resources").insert({
        "title": title,
        "subject_code": subject_code,
        "category": category,
        "file_url": file_url
    }).execute()

    return redirect("/")

# SERVER-SIDE ROUTED SEARCH (FILTERING WITH SUPABASE)
@app.route("/search")
def search():
    if "user" not in session:
        return redirect("/login")

    query = request.args.get("query", "")
    category = request.args.get("category", "all")

    # Start by filtering match on the subject code text
    db_query = supabase.table("resources").select("*").ilike("subject_code", f"%{query}%")

    # If category dropdown is not set to 'all', add category match filter
    if category != "all":
        db_query = db_query.eq("category", category)

    response = db_query.execute()
    resources = response.data
    
    counts_res = supabase.table("downloads").select("*").execute()
    counts = {str(item["resource_id"]): item["count"] for item in counts_res.data}
    
    return render_template("index.html", resources=resources, counts=counts)

# BLUEPRINT REGISTRATIONS
app.register_blueprint(auth_bp)
app.register_blueprint(downloads_bp)

if __name__ == "__main__":
    app.run(debug=True)