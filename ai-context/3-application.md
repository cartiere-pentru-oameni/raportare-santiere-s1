# Application Components

## Public Components (No Authentication)

### 1. Home Page
- Welcome message and project introduction
- Quick access to report submission
- Link to tutorial on checking paperwork
- Statistics overview

### 2. Report Submission Form
- Type of violation dropdown
- Interactive map for location selection
- Address input (optional)
- Description textarea (optional)
- Multi-file image upload with client-side EXIF stripping
- Form validation
- Anonymous submission (no user tracking)

### 3. Reports Map View
- Interactive map showing all public reports
- Filter by status and type
- Clickable markers that link to report details
- Visual indicators for report status (color coding)

### 4. Report Detail Page
- Unique permanent URL per report
- Display report information based on status:
  - **Pending**: Only location and type visible
  - **In-review/Validated**: Full details visible
  - **Invalidated**: Show validator comments
- Status history timeline
- Validator comments (when available)

### 5. Statistics Dashboard
- Total reports by type
- Reports by status (charts/graphs)
- Average completion time
- Reports auto-deleted after 30 days
- Trend analysis over time

### 6. Tutorial Page
- Step-by-step guide on checking construction paperwork
- Visual examples and explanations
- Legal framework information

### 7. Information Page
- Project description and mission
- Anonymity guarantees and GDPR compliance
- Contact information
- Terms of service and privacy policy

### 8. Anonymous Contact Form
- Form to report personal data leaks in reports
- General inquiries
- No tracking or identification

### 9. Permits Search Page
- Search building permits by address or permit number
- Data from two sources: PS1 (Primaria Sector 1) and PMB (Primaria Municipiului Bucuresti)
- Helps citizens verify if a construction site has valid permits

## Authenticated Components (Official Users)

### 10. Login Page
- Username/password authentication
- Session management with secure cookies

### 11. Validator Dashboard
- List of all reports with advanced filters:
  - By status
  - By type
  - By date range
- Sorting options
- Quick status overview

### 12. Report Review Page (Validators)
- Full report details including raw data
- Tools to edit/remove personal data:
  - Text editing for description/address
  - Image removal/replacement
- Status change workflow:
  - Pending � In-review / Not-allowed
  - In-review � Validated / Invalidated
  - Validated � Waiting for authorities feedback
  - Waiting for authorities feedback � Resolved
- Comment input for each status change
- Inappropriate content flagging

### 13. Administrator Dashboard
- User management interface
- System statistics and health
- Configuration settings

### 14. User Management Page (Admins)
- Add new users (validators, admins)
- Edit user roles
- Deactivate/delete users

### 15. Permits Management Page (Admins)
- View permits data statistics (total count, last scraped)
- Trigger scraper refresh for PS1 and PMB data
- Monitor scraper status (running, error, idle)

### 16. Contact Messages Page (Admins)
- View anonymous contact form submissions
- Mark messages as read
- Add admin notes

# Application Flows

### Citizen Report Submission Flow
1. User accesses report form
2. User selects location on map
3. User uploads photos (EXIF stripped client-side)
4. User fills in optional details
5. User selects violation type
6. User submits form
7. Server validates and strips EXIF again (redundant safety)
8. Server stores images in object storage
9. Server creates report with status "pending"
10. Server returns unique report URL
11. User can share/save the link

### Validator Review Flow
1. Validator logs in
2. Validator sees list of pending reports
3. Validator opens report for review
4. Validator checks for:
   - Inappropriate content
   - Personal data (names, faces, phone numbers, addresses)
5. Validator removes any personal data if found
6. Validator changes status to "in-review" or "not-allowed"
7. If validated, validator adds public comment
8. Validator updates status through workflow
9. Public sees updated status and comments

### Auto-deletion Flow (Background Job)
1. Scheduled job runs daily
2. Query reports with status "pending" older than 30 days
3. Delete associated images from storage
4. Delete report records
5. Log deletion count for statistics

## Security Considerations

### Privacy Protection
- No IP address logging
- No user agent tracking
- No cookies for anonymous users
- EXIF data stripped on client AND server
- Personal data redaction tools for validators

### Authentication & Authorization
- Secure password hashing (bcrypt)
- Flask server-side sessions (not JWT)
- Role-based access control (RBAC) via `@login_required(role='admin')` decorator
- Session management with HTTP-only cookies

### Input Validation
- Server-side validation for all inputs
- File type validation (images only)
- File size limits (e.g., 5MB per image, max 10 images)
- XSS protection on all text inputs
- SQL injection prevention via parameterized queries