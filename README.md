# Cocoon V2

## Overview

Cocoon V2 is a comprehensive household services marketplace application designed to bridge the gap between customers seeking home services and skilled service professionals. The platform facilitates seamless interactions for services ranging from plumbing and electrical repairs to cleaning and maintenance.

## Problem Statement

In today's fast-paced world, finding reliable household services can be challenging:

- Time-consuming traditional service sourcing methods
- Lack of transparency in service delivery
- Difficulty in guaranteeing service quality
- Disconnection between customers and service professionals

## Solution

Cocoon V2 addresses these challenges by providing:

- Easy service request management
- Real-time service tracking
- Customer feedback and review system
- Efficient service professional management interface

## Technology Stack

### Backend

- **Framework:** Flask
- **Libraries:**
  - Flask-Session
  - Flask-CORS
  - SQLite3
  - Werkzeug.security
  - python-dotenv
  - Tempfile
  - Celery
  - FPDF
  - Crontab

### Frontend

- **Framework:** Vue.js
- **Libraries:**
  - Vue Router
  - Bootstrap
  - JavaScript Cookies

### Background Processing

- **Task Queue:** Celery
- **Message Broker:** Redis
- **Scheduled Tasks:** Celery Beat

### Additional Technologies

- **Caching:**
  - Redis
  - Flask-Caching
- **Email Services:**
  - Mailgun
  - Requests

## Prerequisites

Before installation, ensure you have the following installed:

- Python 3.x
- Node.js (Latest LTS version)
- Yarn package manager
- Redis server (for both caching and Celery broker)
- Git
- Celery

## Installation

### Backend Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Ajayaditya-Codes/Cocoon-V2.git
   ```

2. Navigate to the backend directory:

   ```bash
   cd code/backend-flask
   ```

3. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

4. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables:

   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

6. Start Redis server:

   ```bash
   redis-server
   ```

7. Start Celery worker:

   ```bash
   celery -A app.celery worker --loglevel=info
   ```

8. Start Celery beat for scheduled tasks:

   ```bash
   celery -A app.celery beat --loglevel=info
   ```

9. Start the backend server:
   ```bash
   python3 app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd code/frontend-vue
   ```

2. Install dependencies:

   ```bash
   yarn
   ```

3. Start the development server:
   ```bash
   yarn dev
   ```

## Configuration

### Mail Configuration

```python
# .env example
MAILGUN_API_KEY='your-mailgun-api-key'
MAILGUN_DOMAIN='your-mailgun-domain'
MAIL_DEFAULT_SENDER='noreply@yourdomain.com'
FLASK_SECURITY_KEY='yoursecretkey'
```

### Scheduled Tasks

1. **Daily Tasks**: Send service reminders
2. **Monthly Reports**: Generate monthly statistics

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure to:

- Follow the existing code style
- Write clear commit messages
- Add tests if applicable
- Update documentation as needed

## License

MIT License

Copyright (c) 2024 Cocoon V2

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
