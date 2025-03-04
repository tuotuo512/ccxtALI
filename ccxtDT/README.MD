# 数字货币交易系统

## 项目概述

本系统旨在通过多因子分析捕捉数字货币的单边趋势，提供自动化交易决策支持。

## 系统架构

系统分为以下几个主要模块：

- **数据层 (data_layer)**: 负责数据收集、处理和存储
- **策略层 (strategy_layer)**: 实现因子计算和信号生成
- **模型层 (model_layer)**: 处理特征工程和模型训练
- **执行层 (execution_layer)**: 管理交易执行和风险控制

## 使用说明

...

## 开发计划

...

DT/
├── data_layer/
│ ├── __init__.py
│ ├── config.py
│ ├── collectors/
│ │ ├── __init__.py
│ │ ├── historical.py
│ │ └── realtime.py
│ ├── processors/
│ │ ├── __init__.py
│ │ ├── cleaner.py
│ │ └── transformer.py
│ └── storage/
│ ├── __init__.py
│ ├── mysql_handler.py
│ └── mongodb_handler.py
├── strategy_layer/
│ ├── __init__.py
│ ├── factors/
│ │ ├── __init__.py
│ │ ├── technical_factors.py
│ │ └── fundamental_factors.py
│ ├── signals/
│ │ ├── __init__.py
│ │ ├── trend_signals.py
│ │ └── reversal_signals.py
│ └── backtest/
│ ├── __init__.py
│ ├── evaluator.py
│ └── visualizer.py
├── model_layer/
│ ├── __init__.py
│ ├── features/
│ │ ├── __init__.py
│ │ ├── engineer.py
│ │ └── selector.py
│ ├── training/
│ │ ├── __init__.py
│ │ ├── trainer.py
│ │ └── validator.py
│ └── inference/
│ ├── __init__.py
│ └── predictor.py
├── execution_layer/
│ ├── __init__.py
│ ├── trader.py
│ ├── risk_manager.py
│ └── performance_monitor.py
├── utils/
│ ├── __init__.py
│ ├── logger.py
│ ├── config_manager.py
│ └── visualization.py
├── config.py
└── main.py