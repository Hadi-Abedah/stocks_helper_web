# Stocks Helper Web

A personal stock tracking and portfolio workflow project that combines:

- an **automation pipeline** for collecting, parsing, and processing stock-related data
- a **Django web application** for browsing, visualizing, and working with the resulting data

The repository is organized as a **monorepo** with two main parts:

- `stocks_helper/` → automation and data-processing logic
- `web/` → Django web application

Both parts are designed to run with Docker, typically as **separate containers/services** defined in `docker-compose.yml`, while sharing one codebase.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Docker Setup](#docker-setup)
- [Quick Start](#quick-start)
- [Automation Component](#automation-component)
- [Web Component](#web-component)
- [Environment and Secrets](#environment-and-secrets)
- [Development Notes](#development-notes)
- [Roadmap](#roadmap)

---

## Overview

This project is intended to help manage and analyze stock and portfolio data in a structured way.

It combines two connected systems:

### 1. Automation layer
The automation side is responsible for tasks such as:

- importing and parsing transaction data
- cleaning and transforming portfolio records
- generating local artifacts such as CSV and JSON files
- integrating with third-party services such as SnapTrade and Google-based tools
- preparing data for storage in the database

### 2. Web layer
The web side provides a Django-based interface for:

- viewing tracked data
- exploring journal or transaction records
- browsing stock-related pages
- building dashboards and summary pages

The long-term goal is to keep the project as a unified codebase where automation and the web application can share models, logic, and database access where appropriate.

---

## Architecture

At a high level, the project uses a monorepo layout with two major application areas.

```text
stocks_helper_web/
├── stocks_helper/    # automation, integrations, scripts, generated artifacts
├── web/              # Django project and app
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md