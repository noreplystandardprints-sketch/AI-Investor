# AI-Investor

⚠️ **BETA STATUS**: This project is in active development. Use with caution, especially for live trading.

An advanced reinforcement learning-powered trading bot that uses Proximal Policy Optimization (PPO) to learn trading strategies. Features real-time integration with Interactive Brokers (IBKR) for live and paper trading, comprehensive market analysis, and intelligent position management.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Trading Modes](#trading-modes)
- [RL Training](#rl-training)
- [IBKR Integration](#ibkr-integration)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Features

### 🤖 Reinforcement Learning
- **PPO (Proximal Policy Optimization)** for stable, sample-efficient learning
- Multi-ticker support with individual models per symbol
- Incremental training with checkpoints
- Deterministic and stochastic action modes

### 📊 Trading Capabilities
- **Long & Short Positions**: Buy/sell long, short sell, and cover short
- **Smart Position Management**: Automatic entry/exit based on learned policies
- **Risk Controls**: 
  - Position sizing relative to account balance
  - Trade permission system (buy/sell/short/cover)
  - IBKR account capability detection

### 🔗 IBKR Integration
- **Paper Trading**: Full simulation with persistent account state
- **Live Trading**: Real-time order execution (with safety guards)
- **Market Data**: Real-time pricing from IBKR or yfinance fallback
- **Account Monitoring**: Live balance and position tracking

### 📈 Analysis & Visualization
- Live dashboard with real-time P&L tracking
- Per-year profit/loss reporting
- Detailed trade history logging
- Market research sessions with configurable duration

### 💾 Persistence
- Model checkpointing and incremental training
- Paper account state saved to JSON
- Trade history and performance metrics stored
- Knowledge files in JSON and Parquet formats

## Architecture

```
AI-Investor/
├── TradeAI.py                 # Main application
├── tickers.py                 # Ticker list configuration
├── models/                    # Trained PPO models (.zip format)
├── logs/                      # Training logs
├── data/                      # Historical price data (cached CSVs)
├── knowledge/                 # Market research outputs
├── simulation_results/        # Trading simulation results
└── ibkr_account.json         # Paper account persistence
```

### Core Classes

- **TradingEnv**: Gymnasium environment for RL training
  - 5-action space: [Sell Long, Hold, Buy Long, Cover Short, Short Sell]
  - Continuous observation space: balance + positions + price windows
  - Reward signal: portfolio value change

- **MockBroker**: Simulated trading with paper account
- **IBKRBroker**: Live IBKR integration via `ib_insync`
- **Broker Protocol**: Abstract interface for seamless switching

## Installation

### Prerequisites
- Python 3.10+
- IBKR TWS (7497) or Gateway (4001) running locally
- pip or conda

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd AI-Investor

# Install dependencies
pip install -r requirements.txt

# Optional: Install IBKR connector (for live trading)
pip install ib_insync

# Download initial data
python TradeAI.py
```

### Requirements

Key dependencies:
- `gymnasium`: RL environment framework
- `stable-baselines3`: PPO implementation
- `pandas`, `numpy`: Data processing
- `yfinance`: Market data
- `ib_insync`: IBKR integration
- `curl_cffi`: Anti-blocking HTTP client

## Quick Start

### 1. Interactive Menu
```bash
python TradeAI.py --menu
```

Menu options:
1. Save market knowledge
2. Run customizable research session
3. Resimulate trading
4. Live dashboard
5. Paper trading account
6. Trade permissions
7. IBKR settings
8. IBKR AI bot
9. Exit

### 2. Paper Trading Demo
```bash
python TradeAI.py --menu
# Select "5) Paper trading account"
# Option "ai" to have PPO control trades
```

### 3. Live Trading (with IBKR)
```bash
python TradeAI.py --menu
# Select "7) IBKR settings"
# Enable IBKR pricing and execution
# Select "8) IBKR AI bot"
# Choose "auto-threshold" or "ppo-policy"
```

## Core Components

### RL Training (PPO)

The model learns to maximize portfolio value through:
- **State**: [balance, long/short positions, price windows (30-step history)]
- **Actions**: 5 discrete actions × number of tickers
- **Reward**: Portfolio value delta + trading incentives

```python
# Training a model
from TradeAI import start_training

start_training(total_timesteps=50000, tickers=['SPY', 'AAPL'])
```

### Trading Environment

```python
from TradeAI import TradingEnv

env = TradingEnv(
    tickers=['SPY', 'AAPL'],
    start='2010-01-01',
    end='2019-12-31',
    window_size=30
)
```

**Action Mapping** (per ticker):
- `0`: Sell long positions
- `1`: Hold
- `2`: Buy long
- `3`: Cover short positions
- `4`: Short sell

### Paper Trading

Persistent account with JSON state:
- Buy/sell at live prices (with override option)
- Track average cost per position
- Maintain cash balance
- Export trade history

```bash
python TradeAI.py --paper-op init --balance 100000
python TradeAI.py --paper-op buy --symbol AAPL --shares 10
python TradeAI.py --paper-op view
```

### Live Dashboard

Real-time monitoring with position tracking:
```bash
python TradeAI.py --live-dashboard --tickers AAPL,MSFT,SPY \
  --positions "AAPL:10:180,MSFT:5:300" \
  --poll-interval 1
```

## Trading Modes

### 1. **Simulation**
- Backtesting using historical data (2010-2023)
- No real capital at risk
- Useful for model development

### 2. **Paper Trading**
- Local simulation with persistent state
- Tracks P&L separately
- Full order history

### 3. **Live Trading (IBKR)**

#### Auto-Threshold Bot
- Simple anchored threshold strategy
- Buy/sell based on % deviation from anchor
- Good for conservative strategies

```bash
python TradeAI.py --ibkr-ai-bot auto-threshold \
  --watchlist SPY,QQQ \
  --buy-threshold 0.98 \
  --sell-threshold 1.02
```

#### PPO Policy Bot
- Uses trained PPO models
- Continuous learning possible
- Adaptive to market conditions

```bash
python TradeAI.py --ibkr-ai-bot ppo-policy \
  --watchlist AAPL,TSLA,MSFT \
  --max-order-shares 10 \
  --poll-interval 60
```

## RL Training

### Training from Scratch

```python
python TradeAI.py --action research --tickers SPY,AAPL \
  --minutes 30 --start 2010-01-01 --end 2019-12-31
```

### Incremental Training

Models automatically load and continue training:
```python
start_training(total_timesteps=100000, tickers=['SPY'])
# Subsequent calls will resume from last checkpoint
```

### Custom Training

```python
from stable_baselines3 import PPO
from TradeAI import TradingEnv, make_vec_env

env = make_vec_env(
    lambda: TradingEnv(tickers=['AAPL'], start='2015-01-01', end='2020-12-31'),
    n_envs=4  # Vectorized for faster training
)

model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=100000)
model.save('models/custom_model')
```

## IBKR Integration

### Setup

1. Install and run IBKR TWS or Gateway
   - TWS: Runs on `127.0.0.1:7497`
   - Gateway: Runs on `127.0.0.1:4001`

2. Enable API in settings:
   - TWS: Edit → Settings → API → Enable ActiveX and Socket Clients
   - Gateway: Configure API settings

3. Ensure paper trading account is active

### Configuration

```bash
python TradeAI.py --use-ibkr --ib-host 127.0.0.1 --ib-port 7497 \
  --ib-client-id 1 --ib-exec
```

CLI arguments:
- `--use-ibkr`: Enable IBKR pricing
- `--ib-host`: IBKR host (default: 127.0.0.1)
- `--ib-port`: IBKR port (7497 TWS, 4001 Gateway)
- `--ib-client-id`: Client ID (default: 1)
- `--ib-exec`: Execute live orders

### Trade Permissions

Control what trades are allowed:

```bash
python TradeAI.py --menu
# Select "6) Trade Permissions"
# Toggle BUY, SELL, SELL_SHORT, BUY_TO_COVER
```

Auto-detect from IBKR account type:
```bash
# Permissions automatically updated based on account shorting capability
```

## Usage Examples

### Example 1: Train & Backtest

```bash
# Train PPO model
python TradeAI.py --action research --tickers SPY \
  --minutes 60 --window-size 30

# Backtest the trained model
python TradeAI.py --action resimulate --tickers SPY
```

### Example 2: Live Trading with Auto-Threshold

```bash
# View current portfolio
python TradeAI.py --paper-op view

# Start auto-threshold IBKR bot
python TradeAI.py --use-ibkr --ib-exec \
  --ibkr-ai-bot auto-threshold \
  --watchlist AAPL,MSFT,GOOGL \
  --buy-pct 0.02 --sell-pct 0.03 --order-shares 1
```

### Example 3: Paper Account Simulation

```bash
# Initialize paper account
python TradeAI.py --paper-op init --balance 50000

# Manual trades
python TradeAI.py --paper-op buy --symbol AAPL --shares 5 --price 150
python TradeAI.py --paper-op sell --symbol AAPL --shares 2 --price 155

# AI-controlled trading
python TradeAI.py --paper-op ai --tickers AAPL,MSFT --trade-shares 5

# Watch live
python TradeAI.py --paper-op live --poll-interval 1
```

### Example 4: Dashboard Monitoring

```bash
# Real-time P&L dashboard
python TradeAI.py --live-dashboard \
  --tickers AAPL,MSFT,SPY,QQQ \
  --positions "AAPL:10:150,MSFT:5:330,SPY:3:450" \
  --poll-interval 1 --compact
```

## Configuration

### Environment Variables

```bash
# Model save directory
export MODELS_DIR="./models"

# Data cache directory
export DATA_DIR="./data"

# Logs directory
export LOG_DIR="./logs"

# IBKR connection
export IB_HOST="127.0.0.1"
export IB_PORT="7497"
```

### Model Architecture

PPO policy configuration in code:
```python
policy_kwargs = dict(
    net_arch=[64, 64],  # 2 layers, 64 units each
    activation_fn=torch.nn.ReLU,
    lr_schedule='constant'
)
```

## Troubleshooting

### IBKR Connection Issues

**Problem**: "IBKR not connected"
```
Solution:
1. Verify TWS/Gateway is running
2. Check port number (7497 TWS, 4001 Gateway)
3. Enable API in account settings
4. Ensure client ID is available (no duplicate connections)
```

**Problem**: "ib_insync not installed"
```bash
pip install ib_insync
```

### Model Loading Errors

**Problem**: "Failed to load existing model"
```
Solution:
1. Delete corrupted .zip file in models/
2. Delete .meta.json metadata
3. Retrain from scratch
```

### Data Download Issues

**Problem**: yfinance download fails
```
Solution:
1. Already downloaded CSVs cached in data/
2. Manual fallback to yfinance API
3. Check internet connection
```

### Paper Account Issues

**Problem**: "Insufficient balance"
```bash
# Reset/increase balance
python TradeAI.py --paper-op set-balance --balance 100000
```

## Performance Metrics

Backtest results are saved to `simulation_results/`:
- `trade_results.json`: Detailed trade log
- `pl_per_year.txt`: Annual P&L
- `detailed_trade_profits.json`: Per-trade PnL analysis

Example output:
```
Year 2020: +$5,342.50
Year 2021: +$12,891.23
Year 2022: -$2,145.67
Year 2023: +$8,756.34
```

## Advanced Features

### Market Research Sessions

Extended market analysis with periodic saves:
```bash
python TradeAI.py --action research \
  --tickers AAPL,MSFT,GOOGL,AMZN \
  --minutes 120 --save-every-secs 30 --format parquet
```

Outputs:
- `knowledge/market_knowledge_*.json`: Tick-level data
- `knowledge/market_knowledge_big_*.parquet`: Full OHLCV history

### Stop Training Signal

Create `STOP_TRAINING` file to gracefully halt ongoing training:
```bash
touch STOP_TRAINING
```

Training will checkpoint and exit within seconds.

## Contributing

Contributions welcome! Areas for enhancement:
- Multi-factor reward shaping
- Options trading strategies
- Risk management improvements
- Alternative RL algorithms (SAC, TD3)
- Integration with other brokers

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International
license (CC BY-NC 4.0). You are free to share and adapt the material provided you give appropriate
credit, provide a link to the license, and indicate if changes were made. You may not use the
material for commercial purposes.

Full license text is available in the `LICENSE` file. For details see:
https://creativecommons.org/licenses/by-nc/4.0/

## Disclaimer

**Risk Warning**: Trading involves substantial risk of loss. This software is provided for educational and research purposes only.

- Past performance does not guarantee future results
- Use paper trading to validate strategies before live trading
- Never risk capital you cannot afford to lose
- The authors are not responsible for financial losses
- Ensure compliance with all applicable trading regulations
- Always enable trade permissions and safety checks
- Test thoroughly in simulation before going live
- This is BETA software and may contain bugs or unexpected behavior

## Support

For issues and questions:
1. Check the Troubleshooting section
2. Review IBKR API documentation
3. Consult Gymnasium and Stable-Baselines3 docs
4. Open a GitHub issue