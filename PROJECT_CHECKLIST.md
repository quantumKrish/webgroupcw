# Auction Web App - 8 Day Development Checklist

## Team Structure (Equal Work Distribution - 33% each)

- **Adrian**: Complex infrastructure, deployment, cron/email system
- **Emir**: Authentication, profile, frontend routing
- **Krish**: Items, search, bidding, Q&A

---

## DAY 1 - Foundation Setup

### Adrian

- [x] Setup custom User model with AbstractUser
- [x] Configure Django authentication framework
- [x] Setup Gmail account for project emails

### Emir

- [x] Configure Vue Router structure
- [x] Setup Pinia global store architecture
- [x] Create basic Vue layout/navigation components

### Krish

- [x] Design database models for auction items
- [x] Design database models for bids
- [x] Design database models for Q&A system

---

## DAY 2 - Models & Basic Auth

### Adrian

- [ ] Create User serializers for API
- [x] Add Python type hints to User model
- [ ] Build user authentication API endpoints
- [x] Add TypeScript interfaces for User model

### Emir

- [x] Create signup Django form and template
- [x] Create login Django form and template
- [x] Test signup/login flow
- [x] Create basic Vue authenticated layout

### Krish

- [x] Create item models and run migrations
- [x] Create Bid model and run migrations
- [x] Create Q&A models (Question, Reply) and migrations
- [x] Add TypeScript interfaces for Item/Bid/Q&A models

---

## DAY 3 - Core Features Part 1

### Adrian

- [x] Configure Django email settings
- [x] Setup basic cron job configuration
- [ ] Create email templates for winners
- [x] Test email sending functionality

### Emir

- [x] Build profile page Vue component
- [x] Implement profile edit API endpoint
- [x] Add profile image upload field
- [x] Connect profile page with Ajax (fetch API)
- [x] Test profile updates without page refresh

### Krish

- [x] Create item listing page Vue component
- [x] Build item list API endpoint
- [x] Build search API endpoint for items
- [x] Implement search functionality with Ajax
- [x] Test search without page refresh

---

## DAY 4 - Core Features Part 2

### Adrian

- [x] Implement cron job for checking auction end times
- [x] Create logic to determine auction winners
- [x] Test automated email sending to winners
- [ ] Add error handling for email failures

### Emir

- [x] Integrate Vue Router for all pages
- [x] Setup Pinia store for user state
- [x] Setup Pinia store for auth state
- [x] Add route guards for authenticated pages
- [x] Polish navigation and routing

### Krish

- [x] Create "post new item" Vue component
- [x] Build POST item API endpoint
- [x] Add image upload for items
- [x] Build bidding API endpoint (POST bid)
- [x] Add bid validation (amount > current bid)

---

## DAY 5 - Advanced Features

### Adrian

- [ ] Start OpenShift deployment configuration
- [ ] Create Dockerfile/deployment files
- [ ] Add Python type hints throughout backend
- [ ] Review and ensure all serializers use type hints
- [ ] Test local build for deployment

### Emir

- [x] Setup Pinia store for items/bids
- [x] Add TypeScript type checking to all Vue components
- [x] Ensure all interfaces properly typed
- [x] Add error handling throughout frontend
- [x] Polish UI/UX across all pages

### Krish

- [x] Create individual item detail page
- [x] Display current bids and bid history on item page
- [x] Create bid Vue component for item page
- [x] Implement Question API endpoints (GET, POST)
- [x] Implement Reply API endpoints (GET, POST)

---

## DAY 6 - Final Features & Deployment

### Adrian

- [ ] Complete OpenShift deployment
- [ ] Deploy application to OpenShift
- [ ] Configure cron jobs on OpenShift
- [ ] Test email sending from deployed app
- [ ] Code review all backend code

### Emir

- [x] Code review all frontend code
- [x] Verify all Ajax calls work correctly
- [x] Test Vue Router on all pages
- [x] Test Pinia stores update correctly
- [x] Fix any frontend bugs found

### Krish

- [x] Build Q&A Vue component for item detail page
- [x] Allow users to ask questions on items
- [x] Allow item owners to reply to questions
- [x] Display Q&A on item detail page
- [x] Test entire item/bid/Q&A flow

---

## DAY 7 - Test Data & Testing

### Adrian

- [ ] Create admin superuser account
- [ ] Test all backend API endpoints
- [ ] Verify email notifications work
- [ ] Verify cron jobs run correctly
- [ ] Fix any backend bugs found

### Emir

- [ ] Create 5 test user accounts
- [ ] Add profile images for test users
- [ ] Test all user/profile features
- [ ] Verify routing works on deployed app
- [ ] Start writing README (team contributions section)

### Krish

- [ ] Create 10+ auction items with images
- [ ] Add realistic titles, descriptions, prices
- [ ] Set various auction end dates/times
- [ ] Add test bids to various items
- [ ] Add sample questions and replies to items

---

## DAY 8 - Final Testing & Submission

### Adrian

- [ ] Final deployment verification on OpenShift
- [ ] Test all features on deployed app
- [ ] Verify cron jobs working on production
- [ ] Final code review and cleanup
- [ ] Help finalize README if needed

### Emir

- [ ] Final testing of auth flow on deployed app
- [ ] Final testing of profile features
- [ ] Final testing of routing/navigation
- [ ] Add admin credentials to README
- [ ] Add test user credentials to README

### Krish

- [ ] Final testing of items/search on deployed app
- [ ] Final testing of bidding system
- [ ] Final testing of Q&A system
- [ ] Add deployed app URL to README
- [ ] Prepare and submit final zip file to QM+

---

## Work Distribution Summary

### Adrian (~33% - Complex Tasks)

**Focus**: Infrastructure, deployment, cron/email automation

- Custom User model & auth framework
- Email configuration & cron jobs
- OpenShift deployment & production setup
- Python type hints throughout backend
- Backend code review & testing

### Emir (~33% - Frontend Architecture)

**Focus**: Vue architecture, auth UI, profile features

- Vue Router configuration & routing
- Pinia global store setup
- Signup/login forms and templates
- Profile page with Ajax editing
- Frontend type checking & code review

### Krish (~34% - Feature Development)

**Focus**: Items, bidding, Q&A systems

- All database models (Item, Bid, Q&A)
- Item listing & search with Ajax
- Item creation & detail pages
- Bidding system (backend + frontend)
- Q&A system (backend + frontend)
- Test data creation

---

## Critical Success Factors

### Must Have by End of Day 2

- Custom User model working
- Vue Router & Pinia configured
- All database models created
- Basic authentication (signup/login)

### Must Have by End of Day 4

- Email configuration complete
- Routing & navigation working
- Item listing and search working
- Bidding API functional

### Must Have by End of Day 6

- Deployed to OpenShift
- Cron jobs working on production
- Q&A system complete
- All frontend properly typed

### Must Have by End of Day 8

- All test data populated
- Everything tested and working
- README complete
- Submitted to QM+

---

## Daily Standup Questions

Each team member should answer:

1. What did you complete yesterday?
2. What are you working on today?
3. Are you blocked by anything?

---

## Submission Checklist

- [ ] App deployed to OpenShift
- [ ] Cron jobs working (automated emails)
- [ ] 5 test users created with profile images
- [ ] 10+ auction items created with images
- [ ] Sample bids added to items
- [ ] Sample Q&A added to items
- [ ] README.md includes:
  - [ ] List of group members
  - [ ] Description of each member's contributions
  - [ ] URL of deployed application
  - [ ] Admin username and password
  - [ ] All 5 test user credentials
- [ ] requirements.txt file included
- [ ] Python type hints used throughout
- [ ] TypeScript interfaces used throughout
- [ ] All Ajax calls work without page refresh
- [ ] Vue Router working on all pages
- [ ] Pinia store properly implemented
- [ ] All features working on deployed app
- [ ] Submitted as single zip file to QM+
