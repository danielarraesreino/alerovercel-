from app import create_app, db
from flask_migrate import upgrade

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        upgrade() # Auto-migrate database
    app.run(debug=True, host='0.0.0.0', port=5000)

# Vercel entry point
# This part is executed by Vercel's WSGI server
# We also want to ensure migrations run here
with app.app_context():
    try:
        upgrade()
        print("Database migration successful!")
        # Debug: List tables to confirm migration worked
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        print(f"Tables in DB: {inspector.get_table_names()}")
    except Exception as e:
        print(f"Migration failed (might be already up to date or connection issue): {e}")
