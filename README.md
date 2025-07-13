
-----

# Capital Hook: TradingView to Capital.com Webhook Automation

[](https://www.google.com/search?q=https://github.com/danieltonad/capital-hook)
[](https://www.python.org/downloads/)
[](https://www.google.com/search?q=https://github.com/danieltonad/capital-hook/blob/main/LICENSE)

Capital Hook is a powerful, self-hosted FastAPI application designed for algorithmic traders. It acts as a **bridge between TradingView alerts (signals, screeners, Pine Script strategies) and Capital.com's CFD/forex execution API**, allowing you to automatically execute trades based on your predefined strategies. Say goodbye to manual trade execution and leverage the power of automation to react instantly to market opportunities\!

-----

## 🗒️ Table of Contents

  * [✨ Features](https://www.google.com/search?q=%23-features)
  * [⚠️ Known Limitations](https://www.google.com/search?q=%23%EF%B8%8F-known-limitations)
  * [🛠️ Tech Stack](https://www.google.com/search?q=%23%EF%B8%8F-tech-stack)
  * [🚀 Installation & Environment Setup](https://www.google.com/search?q=%23-installation--environment-setup)
      * [Prerequisites](https://www.google.com/search?q=%23prerequisites)
      * [1. Clone the Repository](https://www.google.com/search?q=%231-clone-the-repository)
      * [2. Set Up a Virtual Environment (Recommended)](https://www.google.com/search?q=%232-set-up-a-virtual-environment-recommended)
      * [3. Install Dependencies](https://www.google.com/search?q=%233-install-dependencies)
      * [4. Configure Capital.com API Credentials](https://www.google.com/search?q=%234-configure-capitalcom-api-credentials)
  * [⚙️ Usage Guide](https://www.google.com/search?q=%23%EF%B8%8F-usage-guide)
      * [Running the Application](https://www.google.com/search?q=%23running-the-application)
      * [Accessing the Dashboard & Config Page](https://www.google.com/search?q=%23accessing-the-dashboard--config-page)
      * [Configuring TradingView Webhooks](https://www.google.com/search?q=%23configuring-tradingview-webhooks)
  * [🤝 Contributing](https://www.google.com/search?q=%23-contributing)
  * [📄 License](https://www.google.com/search?q=%23-license)

-----

## ✨ Features

Capital Hook provides a robust set of features designed to empower algorithmic traders with seamless automation and real-time insights:

  * **Automated Trade Execution**: Automatically execute trades on your Capital.com account when triggered by alerts from TradingView. This includes signals from indicators, screener results, and complex Pine Script strategies.
  * **Real-time Dashboard**:
      * **Portfolio Balance**: Monitor your Capital.com account's real-time balance directly within the application's dashboard.
      * **Live Positions**: View all trades currently in execution or managed by Capital Hook, providing immediate oversight of your active strategies.
      * **Demo & Live Mode Toggle**: Easily switch between your Capital.com demo and live accounts to test strategies risk-free or deploy them confidently to real markets.
  * **Dynamic Configuration**: A dedicated configuration page allows you to tailor the webhook behavior and trade parameters without modifying code:
      * **Payload Setup**: Define custom JSON payloads for incoming TradingView webhooks to perfectly match your strategy's needs.
      * **Stop Loss (SL) & Take Profit (TP)**: Set default or dynamic SL/TP levels for automated trade management.
      * **Market Closed Handling (`MKT_CLOSED`)**: Configure how the hook should behave if a trade signal arrives when the market for the instrument is closed.
      * **Strategy (`STRATEGY`) & Hook Name (`HOOKNAME`) Switches**: Use these to differentiate between various strategies or instances of the hook, enabling more granular control and logging.
  * **Comprehensive Trade History**: Gain detailed insights into your performance with a real-time view of all closed trades, including:
      * **Detailed PnL (Profit & Loss)**: Analyze the profitability of individual trades and overall strategies.
      * **Execution Timestamps**: Track when trades were opened and closed.
      * **Associated Strategy Data**: Link closed trades back to the specific strategies that initiated them.

-----

## ⚠️ Known Limitations

  * **Epic Subscription Limit**: Currently, Capital Hook can subscribe to a maximum of **40 unique epics (trading instruments)** at any given time. While you can initiate and manage an unlimited number of trades, all concurrently active trades must fall within this limit of 40 subscribed epics. This means your diverse strategies should consider this constraint on the number of distinct instruments traded simultaneously.

-----

## 🛠️ Tech Stack

  * **Backend Framework**: **FastAPI** (Python) - A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
  * **Asynchronous Operations**: Likely leverages **`asyncio`** built into Python and FastAPI's native asynchronous capabilities for handling multiple requests efficiently.
  * **HTTP Requests**: **`httpx`** - A powerful, user-friendly HTTP client for Python, used for making requests to the Capital.com API.
  * **Configuration Management**: **Environment variables** and potentially **`python-dotenv`** for loading configurations from a `.env` file, ensuring sensitive information is kept secure.
  * **Web Server**: **`Uvicorn`** - An ASGI web server, recommended for running FastAPI applications due to its speed and asynchronous nature.

-----

## 🚀 Installation & Environment Setup

This guide will walk you through setting up and running Capital Hook on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

  * **Python 3.9+**: The project relies on features available in newer Python versions. [Download Python](https://www.python.org/downloads/)
  * **`pip`**: The standard Python package installer. This usually comes pre-installed with Python.
  * **`git`**: A version control system used for cloning the project repository. If you don't have it, [install Git](https://git-scm.com/downloads).

### 1\. Clone the Repository

First, open your terminal or command prompt and clone the Capital Hook repository to your local machine:

```bash
git clone https://github.com/danieltonad/capital-hook.git
cd capital-hook
```

### 2\. Set Up a Virtual Environment (Recommended)

It's highly recommended to use a **virtual environment** for your project. This creates an isolated Python environment, preventing dependency conflicts with other Python projects on your system.

```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# .\venv\Scripts\activate  # On Windows (use PowerShell or Git Bash for 'source' or just type the path)
```

You should see `(venv)` prepended to your terminal prompt, indicating that the virtual environment is active.

-----

### 3\. Install Dependencies

With your virtual environment activated, install all the required Python packages listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command will download and install all necessary libraries for Capital Hook to run.

-----

### 4\. Configure Capital.com API Credentials

Capital Hook needs your Capital.com API credentials to securely log in and execute trades on your behalf. For security best practices, these credentials should be stored as **environment variables** and never hardcoded directly into your application's source code.

Create a new file named `.env` in the root directory of your project (the same directory where `main.py` is located). Add the following lines, replacing the placeholder values with your actual Capital.com API credentials:

```ini
CAPITAL_IDENTITY="YOUR_CAPITAL_COM_IDENTITY"
CAPITAL_PASSWORD="YOUR_CAPITAL_COM_PASSWORD"
CAPITAL_API_KEY="YOUR_CAPITAL_COM_API_KEY"
CAPITAL_COM_DEMO_MODE="True" # Set to "False" for live trading
```

  * Replace `"YOUR_CAPITAL_COM_IDENTITY"`, `"YOUR_CAPITAL_COM_PASSWORD"`, and `"YOUR_CAPITAL_COM_API_KEY"` with the respective values obtained from your Capital.com account.
  * Set `CAPITAL_COM_DEMO_MODE` to `"True"` if you want the hook to interact with your Capital.com demo account for testing. Change it to `"False"` when you are ready to use your live trading account.

-----

## ⚙️ Usage Guide

### Running the Application

To start the Capital Hook FastAPI application, ensure your virtual environment is activated and then run the following command from the project's root directory:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

  * `main:app`: This specifies that Uvicorn should run the FastAPI application instance named `app` found within `main.py`.
  * `--host 0.0.0.0`: Makes the application accessible from all network interfaces on your machine. This is important if you plan to access the dashboard or send webhooks from another device or a deployed server.
  * `--port 8000`: The port number on which the application will listen for incoming requests. You can change this if port 8000 is already in use.
  * `--reload`: (Useful for development) This flag tells Uvicorn to automatically reload the application whenever it detects changes in your code, so you don't have to restart it manually.

Once the application is running, you should see output in your terminal indicating that Uvicorn is serving on the specified address and port.

### Accessing the Dashboard & Config Page

Once the Capital Hook application is running, you can access its web-based interfaces through your browser:

  * **Dashboard**: Navigate to `http://localhost:8000/dashboard`
      * Here you can monitor your **real-time portfolio balance**, view **live positions**, and observe the status of your trades.
  * **Config Page**: Navigate to `http://localhost:8000/config`
      * This page allows you to dynamically adjust various settings, including **webhook payload structures, Stop Loss/Take Profit defaults, and behavior switches** for market conditions or strategy identification.

### Configuring TradingView Webhooks

To automate your trades, you need to set up alerts in TradingView that send data to your Capital Hook instance via webhooks.

1.  **Determine your Capital Hook's Webhook URL**: This will be the public-facing URL of your deployed Capital Hook instance, followed by the webhook endpoint. Assuming your hook is running locally on port 8000, the default webhook URL would be `http://your-machine-ip:8000/webhook` (replace `your-machine-ip` with your computer's actual IP address if accessing from another device on your network, or your domain if deployed).

2.  **Create a TradingView Alert**:

      * Open TradingView and navigate to the chart or strategy from which you want to send alerts.
      * Click the "Alert" icon (the bell icon, typically on the right sidebar or from the top menu).
      * Configure your **Condition** (e.g., "Crossing," "Strategy Alert") and **Frequency** as needed for your strategy.
      * Under the "Notifications" tab, **check the "Webhook URL" box**.
      * In the "Webhook URL" field, enter the URL you determined in step 1 (e.g., `http://your-machine-ip:8000/webhook`).
      * In the **"Message"** field, you need to construct a **JSON payload** that Capital Hook expects. This payload will carry the necessary information for the trade (e.g., instrument, action, quantity, stop loss, take profit).

    **Example TradingView Alert Message (JSON Payload):**

    ```json
    {
      "symbol": "{{ticker}}",
      "action": "buy",
      "quantity": 1,
      "strategy_name": "MyMACDStrategy",
      "sl_points": 50,
      "tp_points": 100,
      "account_type": "demo" // or "live" if you want to override the global setting
    }
    ```

      * **`{{ticker}}`**: This is a TradingView placeholder that will automatically be replaced with the symbol of the instrument triggering the alert (e.g., `EURUSD`, `AAPL`).
      * `"action"`: Specifies the trade direction (`"buy"` or `"sell"`).
      * `"quantity"`: The number of units or lots for the trade.
      * `"strategy_name"`: A custom string to identify the strategy that sent the alert (useful for logging and filtering trades in the dashboard).
      * `"sl_points"`: (Optional) The Stop Loss level in points from the entry price. If omitted, your default settings from the config page might apply, or no SL will be set.
      * `"tp_points"`: (Optional) The Take Profit level in points from the entry price. If omitted, your default settings from the config page might apply, or no TP will be set.
      * `"account_type"`: (Optional) You can override the global `CAPITAL_COM_DEMO_MODE` environment variable for specific alerts if needed. If omitted, the environment variable setting will be used.

    **Important**: The exact keys expected in the JSON payload (e.g., `symbol`, `action`, `quantity`) depend on how your Capital Hook's webhook endpoint (`/webhook`) is implemented to parse incoming data. **Refer to your project's `main.py` or associated webhook handler code for the precise payload structure it expects.** Ensure your TradingView alert message is valid JSON.

-----

## 🤝 Contributing

We welcome contributions to make Capital Hook even better\! If you have ideas for improvements, new features, or bug fixes, please consider:

1.  **Forking the repository**: Create your own copy of the project.
2.  **Creating a new branch**: For each new feature or fix, create a dedicated branch (e.g., `git checkout -b feature/new-dashboard-metric` or `bugfix/login-issue`).
3.  **Making your changes**: Implement your enhancements or corrections.
4.  **Committing your changes**: Write clear and concise commit messages (`git commit -m 'feat: Add real-time PnL to dashboard'`).
5.  **Pushing to your branch**: Push your local changes to your forked repository (`git push origin feature/your-feature-name`).
6.  **Opening a Pull Request**: Submit a Pull Request to the `main` branch of this repository, describing your changes and their benefits.

Please ensure your code adheres to standard Python best practices and includes appropriate tests where applicable.

-----

## 📄 License

This project is licensed under the **MIT License**. You can find the full text of the license in the [LICENSE](https://www.google.com/search?q=https://github.com/danieltonad/capital-hook/blob/main/LICENSE) file in this repository. This open-source license allows you to use, modify, and distribute the software freely, subject to its terms.