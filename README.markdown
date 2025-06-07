# Article Summary Generator for Telegram

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/release/python-380/)

A powerful Streamlit application that generates concise summaries of articles from Wikipedia and Medium based on user queries and automatically posts them to a Telegram channel. Perfect for researchers, students, and knowledge enthusiasts looking to quickly digest information from trusted sources.

## Features

- **Intuitive Web Interface**: Built with Streamlit for seamless user interaction.
- **Smart Article Search**: Uses the Serper API to find relevant articles on Wikipedia and Medium.
- **AI-Powered Summarization**: Leverages LangChain and Ollama to create concise, high-quality summaries.
- **Telegram Integration**: Automatically posts summaries to a specified Telegram channel.
- **Structured Workflow**: Managed by LangGraph for efficient and reliable processing.

## Technologies Used

| Technology          | Description                                                  |
|---------------------|--------------------------------------------------------------|
| **Python**          | Core programming language for the application.                |
| **Streamlit**       | Creates the interactive web-based user interface.             |
| **LangChain**       | Framework for building applications with language models.     |
| **LangChain-Ollama**| Integrates Ollama for advanced summarization tasks.           |
| **LangGraph**       | Manages the workflow of keyword suggestion, search, and more. |
| **Serper API**      | Enables web searches for relevant articles.                   |
| **Telegram API**    | Sends summaries to a Telegram channel.                        |

## Prerequisites

- **Python 3.8 or later**: Ensure you have Python installed ([Python Downloads](https://www.python.org/downloads/)).
- **Ollama**: A local AI server for running the "qwen2.5:latest" model. Install it from the [Ollama GitHub repository](https://github.com/ollama/ollama).

## Installation

1. **Install Ollama**:
   - Follow the instructions at the [Ollama GitHub repository](https://github.com/ollama/ollama).
   - Pull the required model:
     ```bash
     ollama pull qwen2.5:latest
     ```
   - Start the Ollama server:
     ```bash
     ollama serve
     ```

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/armanjscript/Article-Summary-Generator.git
   cd Article-Summary-Generator
   ```

3. **Install Python Libraries**:
   ```bash
   pip install streamlit langchain langchain-ollama langgraph python-telegram-bot python-dotenv nest_asyncio
   ```

4. **Set Up Environment Variables**:
   - Create a `.env` file in the project root with the following:
     ```
     SERPER_API_KEY=your_serper_api_key
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     TELEGRAM_CHANNEL_ID=your_telegram_channel_id
     ```
   - Obtain the keys:
     - **SERPER_API_KEY**: Sign up at [Serper API](https://serper.dev/) to get your API key.
     - **TELEGRAM_BOT_TOKEN**: Create a bot via [@BotFather](https://t.me/BotFather) on Telegram.
     - **TELEGRAM_CHANNEL_ID**: Find your channel ID using @RawDataBot by sending `/start` and `/id` in your channel.

## Running the Application

1. Ensure the Ollama server is running in the background:
   ```bash
   ollama serve
   ```
2. Start the Streamlit app:
   ```bash
   streamlit run main.py
   ```
3. Open your browser and navigate to `http://localhost:8501` to access the application.

## How It Works

The application uses LangGraph to orchestrate a workflow with the following steps:

1. **Keyword Suggestion**:
   - The user’s query is processed by the Ollama model ("qwen2.5:latest") to generate up to 3 relevant keywords.
2. **Article Search**:
   - The Serper API searches for articles on Wikipedia and Medium using the keywords, selecting up to 3 URLs per source.
3. **Article Loading**:
   - LangChain’s WebBaseLoader fetches the content of selected articles, adding metadata like source and title.
4. **Summarization**:
   - The Ollama model generates concise summaries (under 350 characters each) for each article, combining them into a final output with the query, keywords, and sources.
5. **Telegram Posting**:
   - The summary is sent to the specified Telegram channel via the Telegram Bot API.
6. **Result Display**:
   - The Streamlit interface shows the keywords, article URLs, summary, and a confirmation of the Telegram post.

## Example Usage

1. Run the app:
   ```bash
   streamlit run main.py
   ```
2. In the web interface at `http://localhost:8501`:
   - Enter a query, e.g., "Machine learning."
   - Click "Generate Summary."
3. View the results:
   - **Keywords**: e.g., "machine learning, artificial intelligence, deep learning."
   - **Article URLs**: Links to Wikipedia and Medium articles.
   - **Summary**: A concise summary of the articles.
4. Check your Telegram channel for the posted summary.

## Dependencies

| Library                | Purpose                                                  |
|------------------------|----------------------------------------------------------|
| `streamlit`            | Web interface creation                                   |
| `langchain`            | Language model framework                                 |
| `langchain-ollama`     | Ollama integration for summarization                     |
| `langgraph`            | Workflow management                                      |
| `python-telegram-bot`  | Telegram API interaction                                 |
| `python-dotenv`        | Environment variable management                          |
| `nest_asyncio`         | Asynchronous operation support                           |

## Environment Variables

| Variable               | Description                                                  |
|------------------------|--------------------------------------------------------------|
| `SERPER_API_KEY`       | API key for Serper ([Serper API](https://serper.dev/)).      |
| `TELEGRAM_BOT_TOKEN`   | Telegram bot token from [@BotFather](https://t.me/BotFather).|
| `TELEGRAM_CHANNEL_ID`  | Channel ID from @RawDataBot.                                 |

## Limitations

- Searches are limited to Wikipedia and Medium, with up to 3 articles per source.
- Summaries are capped at 350 characters to fit Telegram’s limits.
- Requires a running Ollama server with the "qwen2.5:latest" model.
- Ensure API keys and Telegram credentials are correctly configured to avoid errors.

## Contributing

Contributions are welcome! Fork the repository, make your changes, and submit a pull request. Please ensure your code follows the project’s style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact [armanjscript] at [armannew73@gmail.com].
