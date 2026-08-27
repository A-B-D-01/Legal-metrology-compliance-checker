# LegalGuard Deployment Guide

## 1. Project Overview

LegalGuard is a software-only Legal Metrology compliance checker consisting of:

- Flask backend API
- Next.js frontend
- MySQL database
- Selenium-based webpage scraper
- Automated pytest tests
- Browser extension

No physical hardware is required.

The project does not require Arduino, ESP32, Raspberry Pi, sensors, GPIO, BLE/Bluetooth hardware, serial/USB hardware, or other physical devices.

## 2. Prerequisites

Install:

- Python 3.12+
- Node.js 20+
- npm
- MySQL 8+
- Git

Verify:

```bash
python --version
node --version
npm --version
mysql --version