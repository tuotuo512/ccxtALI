import os


def create_project_structure():
    # 定义项目结构
    structure = {
        "ccxtDT": {
            "data_layer": {
                "__init__.py": "",
                "config.py": "",
                "collectors": {
                    "__init__.py": "",
                    "historical.py": "",
                    "realtime.py": ""
                },
                "processors": {
                    "__init__.py": "",
                    "cleaner.py": "",
                    "transformer.py": ""
                },
                "storage": {
                    "__init__.py": "",
                    "mysql_handler.py": "",
                    "mongodb_handler.py": ""
                }
            },
            "strategy_layer": {
                "__init__.py": "",
                "factors": {
                    "__init__.py": "",
                    "technical_factors.py": "",
                    "fundamental_factors.py": ""
                },
                "signals": {
                    "__init__.py": "",
                    "trend_signals.py": "",
                    "reversal_signals.py": ""
                },
                "backtest": {
                    "__init__.py": "",
                    "evaluator.py": "",
                    "visualizer.py": ""
                }
            },
            "model_layer": {
                "__init__.py": "",
                "features": {
                    "__init__.py": "",
                    "engineer.py": "",
                    "selector.py": ""
                },
                "training": {
                    "__init__.py": "",
                    "trainer.py": "",
                    "validator.py": ""
                },
                "inference": {
                    "__init__.py": "",
                    "predictor.py": ""
                }
            },
            "execution_layer": {
                "__init__.py": "",
                "trader.py": "",
                "risk_manager.py": "",
                "performance_monitor.py": ""
            },
            "utils": {
                "__init__.py": "",
                "logger.py": "",
                "config_manager.py": "",
                "visualization.py": ""
            },
            "config.py": "",
            "main.py": ""
        }
    }

    # 递归创建目录和文件
    def create_structure(structure, current_path=""):
        for name, content in structure.items():
            path = os.path.join(current_path, name)
            if isinstance(content, dict):
                # 如果是目录
                if not os.path.exists(path):
                    os.makedirs(path)
                create_structure(content, path)
            else:
                # 如果是文件
                with open(path, 'w') as f:
                    f.write(content)

    create_structure(structure)
    print("项目结构创建完成！")


if __name__ == "__main__":
    create_project_structure()