from flask import Flask, render_template, request, redirect
from supabase import create_client

app = Flask(__name__)

# SUPABASE CONFIG

SUPABASE_URL = "https://zrzoddxzskquxhkzftwr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyem9kZHh6c2txdXhoa3pmdHdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjYyODEsImV4cCI6MjA5NDI0MjI4MX0.lB-D9HpPGC4ykbvRlMht_milJIml5KDiVHYgfeQGyh8"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# HOME PAGE

@app.route("/")
def home():

    response = supabase.table("resources").select("*").execute()

    resources = response.data

    return render_template(
        "index.html",
        resources=resources
    )

# UPLOAD RESOURCE

@app.route("/upload", methods=["POST"])
def upload():

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

# SEARCH

@app.route("/search")
def search():

    query = request.args.get("query", "")

    response = supabase.table("resources") \
        .select("*") \
        .ilike("subject_code", f"%{query}%") \
        .execute()

    resources = response.data

    return render_template(
        "index.html",
        resources=resources
    )

if __name__ == "__main__":
    app.run(debug=True)