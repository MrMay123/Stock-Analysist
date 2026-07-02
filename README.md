# Stock Analysist

ReAct agent that reads financial RSS feeds, looks up mentioned tickers via yfinance, and summarizes market-relevant news via DeepSeek.

## Daily Telegram digest (GitHub Actions)

`.github/workflows/daily-news.yml` runs `run_scheduled.py` once a day, combining the "财经（综合）" and "财经（美股重点）" presets, and pushes the resulting report to Telegram.

Required repository secrets:

- `DEEPSEEK_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID` (personal chat or group; group IDs are negative numbers)

Trigger a test run manually from the Actions tab (`workflow_dispatch`) before waiting for the daily schedule.
