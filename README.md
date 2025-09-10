# The $100 Question — Dash App

An educational Dash web application that explores two common investing questions:

1) *If I had invested $100 in a company in the past, what would it be worth today?*  
2) *How risky is a stock over time?*

The app uses historical market data from the Alpha Vantage API and presents it through three interactive views: a normalized “$100 grows to …” chart, an interactive daily candlestick view, and a rolling volatility (risk) view. The site includes a simple login/sign-up flow, a polished theme, and a dashboard-style navigation.

> **Educational use only.** Nothing here is investment advice.

---


## Live / Demo

Render Link: https://final-group-project-dash-app-team-9.onrender.com

---



### Navigation & Access
- **Home** with a short value proposition, clear “Login / Sign up” calls to action, and a **Know the Founders** section (group image + hover headshots).
- **Auth**: login/sign-up flow (passwords hashed via Werkzeug). After sign-in, **Dashboard** becomes the landing page.
- **Top nav** shows **Dashboard, The $100 Question, Daily Trading Activity, Volatility** only after login.
- **Profile menu** at top-right (avatar) opens on click with “Signed in as …” and “Logout”.

### Analytics Pages
- **The $100 Question** (`/hundred`)
  - Normalizes each selected ticker to 100 on its first available date so lines are directly comparable.
  - Optional **Log scale** toggle.
  - **Date range** picker + **ticker** multiselect.
  - Range-slider on x-axis.
  - Colorblind-friendly defaults and responsive layout.

- **Daily Trading Activity** (`/activity`)
  - Interactive **candlestick** chart with **20/50 day** moving averages.
  - **Date range** picker + **ticker** selector.
  - Weekend range breaks, unified hover, and a compact mode bar.

- **Volatility** (`/volatility`)
  - Rolling **annualized volatility** (configurable window via slider).
  - **Date range** picker + **ticker** multiselect.
  - Stacked area chart with a small preview (range slider) and unified hover.
  - Reuses the same return/volatility logic as the standalone script in the prompt.

### Design & UX
- Unified theme in `assets/style.css` (accessible color contrast, consistent components).
- Responsive two-column analysis layout (sticky filter sidebar).
- Images delivered via `assets/images/*` (company logo, founders group and headshots, avatar).
- Error-tolerant defaults (e.g., if API is rate-limited, cached CSVs are used when available).

---


## How to Run Locally

**Prerequisites**
- Python 3.10+ (3.11/3.12 also OK)
- A working internet connection (for initial data fetch), or pre-populated `data_cache/`
- (Recommended) A local SQLite file or a MySQL connection for auth

**1) Clone and enter the repo**
git clone https://github.com/suyog12/Final-Group-Project---Dash-App-Team-9.git
cd Final-Group-Project---Dash-App-Team-9

**2) Install Requirements**
pip install -r requirements.txt

**3) Configure environment**
ALPHAVANTAGE_API_KEY=
DATABASE_URL=
SECRET_KEY=

**4) Run the app**
python app.py
