# ketoApp 
<h1>KETO CALCULATOR</h1>
<img src="ketoapp.png" width="800px">

## Description

This repository is a Django application that enables the user to:

- Create a profile 
- Calculate daily calorie requirements
- Download the caloric value of individual products from an external API
- Summing up the calories of all consumed products during the day
- See a profile with saved information
- See full calendar with daily calorie summary
- Generate pdf report for specific date with daily summary all eaten products
- Send user an email with generated pdf report using Celery task.
- The project includes unit tests to ensure code reliability and correctness.
- The project utilizes Docker for containerization and Docker Compose for managing 
  multi-container application environments. This ensures consistent and reliable 
  deployment and simplifies application setup.

### Technologies Used:

- **Python 3.11**
- **Django 5.3** - Web framework for development. 
- **Celery 5.4.0** - For asynchronous task processing.
- **Postgres 15.4** - Database for storing application data.
- **Docker 24.0.7** - For containerization.
- **Docker-compose v2.23.3-desktop.2** - To manage multi-container environments.
- **JavaScript** - For dynamic web components.
- **Bootstrap 5.3** - For responsive UI design.
- **fullcalendar.io** - For calendar integration and visualization.
- **unittest** - For unit testing application functionality.

### How to run locally:

1. Clone the repo

    git clone https://github.com/pStojczyk/ketoApp.git
   
    cd ketoApp

2. Install requirements
 
    _pip install -r requirements.txt_

3. Run Docker

    `docker-compose up --build`

4. Open localhost in your browser

    _http://localhost:8000_
