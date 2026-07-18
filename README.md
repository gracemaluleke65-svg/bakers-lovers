🍰 Bakers Lovers – Cake Shop E‑Commerce Platform
A full‑stack web application for ordering custom cakes, built with Flask and PostgreSQL, deployed on Vercel with a persistent Neon database. Features user authentication, product browsing, shopping cart, Stripe payments, order management, and an admin dashboard.

🔗 Live: https://bakers-lovers-vercel.vercel.app

✨ Features
User registration / login / logout (session‑based)

Browse cakes by category, view details

Add to cart, update quantities, apply discount coupons

Secure checkout with Stripe (ZAR currency)

Order history and status tracking

Admin dashboard: manage users, products, orders, coupons, feedback

Favourites and product reviews

Fully responsive (Bootstrap)

🛠️ Tech Stack
Layer	Tools
Backend	Python 3.12, Flask
Database	PostgreSQL (Neon), SQLAlchemy, Alembic
Sessions	Flask‑Session (database‑backed)
Auth	Flask‑Login
Payments	Stripe API
Frontend	HTML5, CSS3, JavaScript, Bootstrap 5
Deployment	Vercel (serverless)
Version Control	Git, GitHub
🚀 Quick Start (Local Development)
Clone the repo

bash
git clone https://github.com/gracemaluleke65-svg/bakers-lovers-vercel.git
cd bakers-lovers-vercel
Create a virtual environment

bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Set environment variables – create a .env file in the root:

env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/dbname   # or sqlite:///bakerslovers.db
ADMIN_PASSWORD=available on request
STRIPE_PUBLISHABLE_KEY=your-key   # optional for local testing
STRIPE_SECRET_KEY=your-key
Run the app

bash
python run.py
Visit http://localhost:5000 – the database tables will be created automatically.

