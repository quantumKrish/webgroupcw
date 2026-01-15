# Auction Web Application

A Django + Vue.js auction web application (eBay-like) where users can create accounts, post items for auction, bid on items, ask questions, and receive winner notifications via email.

## Features

### Core Functionality
- **User Authentication**: Custom Django User model with signup/login using Django forms
- **User Profiles**: Edit profile with image, email, and date of birth via Ajax
- **Item Posting**: Create auction items with title, description, starting price, images, and end date/time
- **Item Browsing**: List all items with search functionality (no page refresh) and advanced filters
  - **Filters**: All items, Won auctions, Ended auctions, Active auctions
  - **Sorting**: By price (high/low), date (newest/oldest)
- **Bidding System**: Place bids on items before auction end time with validation
- **Q&A System**: Users can ask item owners questions; owners can reply
- **Winner Notifications**: Automated email sent to auction winner via cron job
- **Image Carousel**: Multi-image upload per item with fullscreen viewer and thumbnail navigation
- **Auction Closed State**: Clear indication when bidding has ended

### Technical
- **Frontend**: Vue 3 with TypeScript, Pinia store, Vue Router, Vite
- **Backend**: Django 5.2.6 with type hints, REST API endpoints
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Email**: Gmail SMTP with cron job automation (Huey)
- **Type Safety**: TypeScript interfaces + Python type annotations throughout

## Team & Contributions

### Adrian
- Django custom User model & authentication framework
- Email configuration and cron job system (Huey)
- OpenShift deployment setup
- Python type hints throughout backend

### Emir
- Vue Router & Pinia store architecture
- Frontend authentication (signup/login forms)
- User profile page with Ajax editing
- Profile display pages
- Frontend type checking & TypeScript

### Krish
- All database models (Item, Bid, Question, Reply, ItemImage)
- Item listing, search, and detail pages
- Bidding system (backend + frontend)
- Q&A system (backend + frontend)
- Image carousel and modal viewer
- Item filtering and sorting
- Winner notification frontend display

## Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- Conda or virtualenv

### Backend Setup
```bash
# Create virtual environment
conda create -n auction_env python=3.12
conda activate auction_env

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Start Django server
python manage.py runserver

# Start Huey background worker (in separate terminal)
python manage.py run_huey
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Visit `http://localhost:5173` to access the application.

## Test Data

### Admin Credentials
- **Username**: admin
- **Password**: [See team for credentials]

### Test Users
| Username | Password | Role |
|----------|----------|------|
| krish | password123 | Seller/Buyer |
| edwin | password123 | Seller/Buyer |
| emir | password123 | Seller/Buyer |

## Deployed Application
- **URL**: [OpenShift deployment URL - added upon deployment]
- **Status**: In development (OpenShift deployment in progress)

## API Endpoints

### Authentication
- `POST /signup/` - Create new user account
- `POST /login/` - Login user
- `GET /logout/` - Logout user

### User & Profile
- `GET /api/user/` - Get current user info & won items
- `GET /api/profile/` - Get user profile
- `POST /api/profile/` - Update user profile
- `GET /api/user/<user_id>/` - Get public user profile

### Items
- `GET /api/items/` - List all items (supports search)
- `POST /api/items/create/` - Create new item
- `GET /api/items/<item_id>/` - Get item detail with bids & Q&A
- `DELETE /api/items/<item_id>/delete/` - Delete item

### Bidding
- `POST /api/bids/create/` - Place a bid

### Q&A
- `POST /api/questions/create/` - Ask a question
- `POST /api/replies/create/` - Reply to a question

## Key Technologies

- **Django 5.2.6** - Python web framework
- **Django REST Framework** - API serialization
- **Vue 3** - Frontend framework
- **TypeScript** - Static typing for JavaScript
- **Pinia** - Vue state management
- **Vite** - Frontend build tool
- **Huey** - Task queue for cron jobs
- **Pillow** - Image processing
- **SQLite/PostgreSQL** - Database

## Development Notes

- Frontend runs on `http://localhost:5173` with Vite dev server
- Backend API runs on `http://localhost:8000`
- Huey worker processes background tasks (email sending, cron jobs)
- Images stored in `media/` directory locally
- Email sending requires valid Gmail credentials in environment variables

## OpenShift Deployment

Once your project is ready to be deployed:

1. Build the Vue app:

    ```bash
    # On Mac/Linux
    npm run build

    # On Windows
    npm run build-windows
    ```

2. Follow OpenShift deployment instructions from QM+

## Known Limitations

- Email sending in development requires valid SMTP credentials
- Huey cron jobs run on a schedule (not real-time)
- Images limited to 5MB per file
- SQLite for local development only (use PostgreSQL for production)

## Future Enhancements

- WebSocket support for real-time bid updates
- Advanced user reputation system
- Payment integration
- Automated re-listing
- Bid sniping prevention
- Category tags for items
- Email digest of favorite items

## License

This code is dedicated to the public domain to the maximum extent permitted by applicable law, pursuant to [CC0](http://creativecommons.org/publicdomain/zero/1.0/).

---
**Module**: ECS639U Web Programming (Queen Mary University of London)
**Module Leader**: Paulo Oliva <p.oliva@qmul.ac.uk>
**Submitted**: January 15, 2026
