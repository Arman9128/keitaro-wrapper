# Adrobot — Keitaro Campaign Manager

Adrobot is a web application that integrates with the Keitaro Tracker through its Admin API.

It provides a simple interface for creating advertising campaigns, configuring GEO-based traffic routing, and managing offers and their traffic distribution.

## Features

### Campaign Management

- Create campaigns directly in Keitaro.
- Configure campaign domain, group, and traffic source.
- Generate unique campaign aliases automatically.
- Create two campaign streams with predefined routing logic.
- Configure country-based traffic filtering.
- Store campaign information in a local database.
- Track campaign creation status.

### Traffic Routing

Each newly created campaign contains two streams:

**1. Google Stream**
- Redirects traffic to `https://google.com`.
- Uses an HTTP redirect action.
- Accepts traffic from the selected GEO.
- Has the first stream position.

**2. Offers Stream**
- Contains the selected active offer.
- Initially assigns 100% of traffic to the offer.
- Has the second stream position.

### Offer Management

- View offers assigned to a campaign.
- Add offers to existing campaigns.
- Remove offers from campaigns.
- Automatically distribute traffic shares between offers.
- Manually update traffic distribution.
- Validate that the total traffic share equals 100%.
- Prevent duplicate offers.
- Prevent removing the last offer from a campaign.

### Web Interface

- Campaign dashboard.
- Campaign creation form.
- Campaign status indicators.
- Offer management interface.
- Traffic distribution editor.
- Responsive layout.

## Tech Stack

**Backend**
- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- HTTPX

**Frontend**
- HTML5
- CSS3
- JavaScript
- Jinja2

**Database**
- SQLite

**Integration**
- Keitaro Admin API

## Project Structure

```text
keitaro-wrapper/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── campaigns.py
│   │       └── offers.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── integrations/
│   │   └── keitaro.py
│   ├── models/
│   │   └── campaign.py
│   ├── schemas/
│   │   ├── campaign.py
│   │   └── offer.py
│   ├── services/
│   │   ├── campaign_service.py
│   │   └── offer_service.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   ├── templates/
│   │   └── index.html
│   └── main.py
├── migrations/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.13 or newer
- pip
- Access to a Keitaro installation
- Keitaro Admin API key

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/keitaro-wrapper.git
cd keitaro-wrapper
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file from the example:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Configure your Keitaro connection in `.env`:

```env
APP_NAME=Adrobot
APP_ENV=development
APP_DEBUG=true

DATABASE_URL=sqlite:///./adrobot.db

KEITARO_BASE_URL=https://your-keitaro-domain.com
KEITARO_API_KEY=your_keitaro_api_key

KEITARO_DOMAIN_ID=your_domain_id
KEITARO_GROUP_ID=your_campaign_group_id
KEITARO_TRAFFIC_SOURCE_ID=your_traffic_source_id
```

Replace the example values with the corresponding values from your Keitaro installation.

**Security:** Keep your `.env` file private. Never commit API keys or other credentials to Git.

### 5. Apply database migrations

Run the following command from the project root:

```bash
python -m alembic upgrade head
```

This creates the local SQLite database and applies the database schema.

To check the current migration:

```bash
python -m alembic current
```

### 6. Start the application

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at:

| Resource | URL |
|---|---|
| Web Interface | http://127.0.0.1:8000 |
| API Documentation | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

## API Endpoints

All application API endpoints use the `/api` prefix.

### Campaigns

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/campaigns` | Create a campaign |
| GET | `/api/campaigns` | Retrieve all local campaigns |
| GET | `/api/campaigns/{campaign_id}` | Retrieve a campaign by local ID |

**Create campaign example:**

Request:

```json
{
  "name": "My Campaign",
  "country_code": "DE",
  "offer_id": 4440
}
```

### Campaign Offers

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/campaigns/{campaign_id}/offers` | Retrieve campaign offers |
| POST | `/api/campaigns/{campaign_id}/offers` | Add an offer |
| PUT | `/api/campaigns/{campaign_id}/offers` | Update offer traffic shares |
| DELETE | `/api/campaigns/{campaign_id}/offers/{offer_id}` | Remove an offer |

**Add offer example:**

```json
{
  "offer_id": 25327
}
```

**Update traffic distribution example:**

```json
{
  "offers": [
    {
      "offer_id": 4440,
      "share": 70
    },
    {
      "offer_id": 25327,
      "share": 30
    }
  ]
}
```

The total traffic share must equal 100%.

**Important:** The `campaign_id` in Adrobot API endpoints is the local database ID. Adrobot internally maps it to the corresponding Keitaro campaign ID.

## Database Migrations

The project uses Alembic to manage database schema changes.

Apply all migrations:

```bash
python -m alembic upgrade head
```

Check the current migration:

```bash
python -m alembic current
```

Generate a migration after modifying SQLAlchemy models:

```bash
python -m alembic revision --autogenerate -m "describe your changes"
```

## Configuration

The following environment variables are supported:

| Variable | Description |
|---|---|
| `APP_NAME` | Application name |
| `APP_ENV` | Application environment |
| `APP_DEBUG` | Enable or disable debug mode |
| `DATABASE_URL` | SQLAlchemy database connection URL |
| `KEITARO_BASE_URL` | Keitaro installation base URL |
| `KEITARO_API_KEY` | Keitaro Admin API key |
| `KEITARO_DOMAIN_ID` | Keitaro domain ID |
| `KEITARO_GROUP_ID` | Keitaro campaign group ID |
| `KEITARO_TRAFFIC_SOURCE_ID` | Keitaro traffic source ID |

## Security

- Keitaro API credentials are loaded from environment variables.
- `.env` files are excluded from version control.
- Local database files are excluded from version control.
- API requests are validated using Pydantic.
- Communication with Keitaro is handled through HTTPX.

## License

Developed as a technical assignment.
