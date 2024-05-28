<div id="top"></div>

<br />
<div align="center">
  <img src="header.png">

  <h1 align="center">Shopping Assistant</h1>
  <p align="center">
    A chat assistent giving shopping recomndations by analyzing an uploaded image.
    <br />
    <br />
    <a href="https://github.com/yllnoreshehi/shopping_assistant/issues">Report Bug</a>
    ·
    <a href="https://github.com/yllnoreshehi/shopping_assistant/issues">Request Feature</a>
  </p>
</div>
<br />
<!--  credit picture: Photo by Godisable Jacob: https://www.pexels.com/photo/woman-wearing-multicolored-top-while-holding-red-leather-sling-bag-1501215/-->
# Shopping Assistant

This repository contains a Gradio-based web application for a Shopping Assistant. The application uses OpenAI's GPT-4 model to analyze images of products and provide shopping recommendations. It can process user queries to assist in making informed purchasing decisions by providing product comparisons, features, advantages, and disadvantages.

## Features

- Analyze images to list products and associated search queries.
- Interactive chat interface for personalized shopping assistance.
- Fetch top product results from Google Shopping based on user queries.
- User-friendly interface with Gradio.

## Installation

### Prerequisites

- Python 3.7+
- OpenAI API key
- SerpAPI key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shopping-assistant.git
   cd shopping-assistant
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
4. Set your OpenAI and SerpAPI keys as environment variables:
   ```bash
   export OPENAI_API_KEY='your-openai-api-key'
   export SERPAPI='your-serpapi-key'