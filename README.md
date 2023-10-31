<div align="center">

# Poof XRPL Payments
### _Empowering Open Source Payments on the XRP Ledger_

![Ledger Logo](https://foundation.xrpl.org/wp-content/uploads/2022/02/ledger_logo.png)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

</div>

---

**Poof** is the web3 developer infrastructure for money movement, facilitating an open-source suite of endpoints for XRPL. We're open sourcing an XRPL infra that enables wallet providers, payment gateways, and XRPL payment flows, to create their own self-hosted payment flows on top of XRPL Ledger. 

The set of functions are in **BETA** and will undergo rigurous testing for production usage in the upcoming month. 


![XRPL Logo](https://i.imgur.com/Gn5IvVF.png)

---

## Features

- **General Endpoints**: This library offers versatile crypto primitives for XRPL payment flows, accommodating various use cases from self-custody payment applications to transaction processing.
- 
![XRPL Logo](https://i.imgur.com/GSN9cu5.png)


- **Multiparty Computation (MPC) Endpoints**: We provide a Go-Python implementation that supports UC Non-Interactive, Proactive, Threshold ECDSA with Identifiable Aborts for robust, secure multi-party signing. 

- **Simplified Integration**: Built on the Flask microframework, this server is optimized for easy deployment on platforms like Heroku, making an easy self-hosted server to integrate with your own platform.

![XRPL Logo](https://i.imgur.com/AqaZZ9G.png)


---

## General Endpoints Overview

Poof's endpoints encompass self-custody payment applications, private key management, and XRPL payment transactions processing. Forthcoming documentation will highlight the integration of these functions within an XRP Ledger payment application.

The list of endpoints will improve in terms of ease of use and documentation as this repo updates 


- **Crypto Primitives**:
  - `/xrpl/generate-bip39-mnemonic`
  - `/xrpl/sss-keyshares-2-of-3`
  - `/xrpl/sss-keyshares-3-of-5`
  - `/xrpl/sss-recovery`
  - `/xrpl/generate-bip42-xpub`
  - `/xrpl/fernet_encryption`
  - `/xrpl/generate-address-from-xpub`

- **XRPL Primitives**:
  - `/xrpl/broadcast_transaction`
  - `/xrpl/get-transactions`
  - `/xrpl/create_wallet`
  - `/xrpl/create_wallet_by_index`
  - `/xrpl/check_address_balance`

- **Multiparty Computation (MPC)**:
  - `/ecsda/generate-shard`
  - `/ecsda/generate-pre-signature`
  - `/ecsda/generate-ecsda-signature`

- **General Functions**:
  - Webhook Notifications
  - External API: `api/v1/fetch-xrp-price`

## MPC Endpoints

Leveraging a Go-Python base, Poof implements the "CGGMP" protocol for threshold ECDSA signing, compatible with ECDSA-based cryptocurrencies and suitable for both cold-wallet and non-custodial applications.

The detailed paper is available here: [Threshold ECDSA Paper](https://eprint.iacr.org/2021/060.pdf).

- **`/generate-shard`**: Generate ECDSA private key shares for MPC.
- **`/generate-pre-signature `**: Generate a preprocessed ECDSA signature for later combination.
- **`/generate-ecsda-signature `**: Combine signature shares to create an ECDSA signature for XRPL transactions.



Additional resources for those interested in experimenting with a Python version for XRPL ECSDA signatures can be based off this paper: [Provable Secure Distributed Schnorr Signatures and a Threshold Scheme](https://eprint.iacr.org/2019/114.pdf).

## Getting Started

Poof is designed for simplicity with Flask, allowing you to quickly deploy to a hosting provider of your choice.

### Mac Installation

```bash
cd (XRP payment server)
virtualenv env
source env/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask run

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
