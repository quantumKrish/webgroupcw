# Auction Web Application

A Django + Vue.js auction web application (eBay-like) where users can create accounts, post items for auction, bid on items, ask questions, and receive winner notifications via email.

## Group Members & Contributions

### Adrian (Infrastructure & Backend)
**Assigned**: Django setup, User model, authentication, email system  
**Delivered**: Implemented custom AbstractUser model, signup/login forms, email configuration with Gmail SMTP, Huey background task queue for cron jobs, winner notification system, OpenShift deployment setup, Python type hints throughout backend code.

### Emir (Frontend Architecture & Auth)
**Assigned**: Vue.js frontend, authentication UI, routing  
**Delivered**: Vue 3 with TypeScript setup, Pinia global store for auth/items, Vue Router with auth guards, signup/login form pages, user profile display and edit page with Ajax, frontend type checking and TypeScript interfaces for all data models.

### Kirishanth (Data Models, Bidding, Items & Q&A)
**Assigned**: Database schema, items, bidding, search, Q&A  
**Delivered**: All core models (Item, Bid, Question, Reply, ItemImage), multi-image carousel with modal viewer, item listing with search and filters (all/won/ended status, price/date sorting), complete bidding system with validation, Q&A with seller-only replies, winner banner display, auction closed state handling.

## Deployed Application

**URL**: https://auction-app-web-apps-ec22888.apps.a.comp-teach.qmul.ac.uk/

## Admin & Test Credentials

### Admin Account
- **Username**: [To be added]
- **Password**: [To be added]

### Test Users (5 accounts)
| Username | Password | Role |
|----------|----------|-------|
| [krish] | [webprogramming] | Seller/Buyer |
| [Emir] | [WebGroupCW] | Seller/Buyer |
| [Gabagool] | [WebGroupCW] | Seller/Buyer |
| [ChosenUndead] | [WebGroupCW] | Seller/Buyer |
| [user5] | [password] | Seller/Buyer |

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
