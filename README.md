# LeanIX Description for OpenAI ChatGPT

![License](https://img.shields.io/badge/license-MIT-blue.svg)

This is a Flask application designed to handle webhook from LeanIX. It includes rate limiting, user authentication, and security headers for enhanced security.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Security](#security)
- [License](#license)

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.x installed
- Dependencies listed in `requirements.txt` installed
- API keys and configuration set up (OpenAI, LeanIX, Basic Auth.)

## Installation

1. Clone this repository:

   ```bash
   git clone git@github.com:bc-bjoern/leanix_description.git ld
   cd ld
   ```

2. Create environment if needed:

  ```
  virtualenv venv
  . venv/bin/activate
  ```

3. Install requirements: 

  ```
  pip install -r requirements.txt
  ```
4. Setup Webhook in LeanIX with Basic Auth
5. Configure your API keys and application settings in the appropriate sections of .env
  ```
  cp .env.example .env
  vi .env
  ```

## Usage

Start the Flask application:

```
python leanix_description/ld.py
```

Your webhook server should now be running on http://localhost:5000/webhook. Ensure you have configured your webhook provider (e.g., LeanIX) to send webhooks to this URL.

## Security

- This application enforces rate limiting to protect against abuse.
- User authentication is required for access.
- Security headers are in place to mitigate common web security vulnerabilities.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
