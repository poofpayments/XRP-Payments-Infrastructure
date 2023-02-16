# XRP Pay
## Open Source payments infrastructure for XRP 

[![N|Solid](https://files.readme.io/e8f0024-poof_logo.svg)](https://www.poof.io/)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Poof is the fastest web3 developer infrastructure for money movement.Our vision is to empower developers and small businesses with self-service payment tools that they can use to build decentralized payment applications and financial services.

This includes an end-to-end crypto & banking framework that enables developers to create their own payment application, such as Venmo or Coinbase, without barrier to entry or setup fees. 


## Features (coming soon)

- Create XRP HD wallet for each user of a crypto exchange or payment system. 
- Optional rebalancing of root of each wallet with account deletions
- Create destination tags for each payment for tracking.
- Balance queries for groups of wallet addresses
- Webhooks when XRP payments are complete
- Transaction broadcasting
- XRP Pay - Payment Links and invoices
- E-Commerce XRP Checkout 

> Current Endpoints:
> /generate-address
-> returns JSON of payment addresses
> /generate_invoice
-> Returns JSON of payment info and payment links
> /fetch-price
-> Fetches USD price of XRP from an aggregate of exchanges




## Demo
This simple demo is build on Flask! Our project plan is to open source the XRP portion of https://docs.poof.io/reference/poof-api for community payment systems. 

## Mac Installation

Flask requires [Python](https://www.python.org//) v3.6.1+ and [Virtualenv](https://virtualenv.pypa.io/en/latest/) to run.
Install the dependencies and start the server.

```sh
cd (XRP payment server)
virtualenv env
source env/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask run
```
## Windows Installation

Flask requires [Python](https://www.python.org//) v3.6.1+ and [Virtualenv](https://virtualenv.pypa.io/en/latest/) to run.
Install the dependencies and start the server.

```sh
cd (XRP payment server)
virtualenv env
source .\env\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=run.py
flask run
```


Verify the deployment by navigating to your server address in
your preferred browser.

```sh
< PROJECT ROOT >
   |
   |-- apps/
   |    |
   |    |-- home/       # A simple app that serve HTML files
   |    |    |-- routes.py                  # Define app routes
   |    |
   |    |-- authentication/ # Handles auth routes 
   |    |    |-- routes.py                  # Define authentication routes  
   |    |    |-- models.py                  # Defines models  
   |    |    |-- forms.py                   # Define auth forms (login and register) 
   |    |
   |    |-- static/
   |    |    |-- <css, JS, images>    # CSS files, Javascripts files
   |    |
   |    |-- templates/        # Templates used to render pages
   |    |    |-- includes/         # HTML chunks and components
   |    |    |    |-- navigation.html       # Top menu component
   |    |    |    |-- sidebar.html          # Sidebar component
   |    |    |    |-- footer.html           # App Footer
   |    |    |    |-- scripts.html # Scripts common to all pages
   |    |    |
   |    |    |-- layouts/                   # Master pages
   |    |    |    |-- base-fullscreen.html  # Used by Authentication
   |    |    |    |-- base.html             # Used by common pages
   |    |    |
   |    |    |-- accounts/                  # Authentication pages
   |    |    |    |-- login.html            # Login page
   |    |    |    |-- register.html         # Register page
   |    |    |
   |    |    |-- home/                      # UI Kit Pages
   |    |         |-- index.html            # Index page
   |    |         |-- 404-page.html         # 404 page
   |    |         |-- *.html                # All other pages
   |    |    
   |  config.py                             # Set up the app
   |    __init__.py                         # Initialize the app
   |
   |-- requirements.txt                     # App Dependencies
   |
   |-- .env      # Inject Configuration via Environment
   |-- run.py           # Start the app - WSGI gateway
   |
   |-- ************************************************************************```

## License
MIT

**Free Software!**
