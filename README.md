# Personalized GAI News-Letter

[Live App!](https://gai-personalize-news-letter-896897809220.us-central1.run.app/)!

This repository contains a Streamlit app that allows users to upload a PDF resource and input their user profile text. The app then generates a custom Word document using `python-docx` based on the inputs. The app is containerized with Docker and is ready for deployment on Google Cloud Run.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation and Running Locally](#installation-and-running-locally)
- [Docker Setup](#docker-setup)
- [Deployment on Google Cloud Run](#deployment-on-google-cloud-run)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- Upload a PDF resource.
- Input a user profile text.
- Generate a custom Word document (DOCX) using `python-docx`.
- Download the generated document.
- Modern, responsive UI styled with custom CSS.

## Prerequisites

- **Python 3.9+**  
- **pip** package manager  
- **Docker** (for containerization)
- A **Google Cloud** account with billing enabled and Cloud Run API activated (for deployment).

## Installation and Running Locally

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo


## Next Steps
- Add an API for the user to be able to trigger a generation of the news letter
- Send emails with reports to designated recipients
- Add a persistence layer and UI for the user to be able to input and modify their user profile
