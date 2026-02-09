# TariqAI - Intelligent UI Automation Framework

TariqAI is a sophisticated UI automation framework that combines multiple automation tools with AI-driven repair and adaptation capabilities. It provides a robust solution for automating complex UI interactions across different platforms and applications.

## Features

- **Multi-Tool Support**: Integrates multiple automation tools including:
  - SikuliX for image-based automation
  - PyAutoGUI for basic UI interactions
  - AutoHotkey for Windows automation
  - Selenium for web automation
  - RPA for robotic process automation

- **Intelligent Repair**: LLM-guided repair and adaptation layer that:
  - Detects and diagnoses automation failures
  - Suggests and implements repair strategies
  - Adapts to UI changes and inconsistencies
  - Maintains execution history for analysis

- **Flexible Tool Selection**: Automatically selects the most appropriate tool based on:
  - Task requirements
  - UI context
  - Historical success rates
  - Environmental constraints

- **Robust Error Handling**:
  - Exponential backoff for retries
  - Tool switching on failures
  - Context preservation
  - Detailed error logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TariqAI.git
cd TariqAI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install external tools:
- SikuliX: Download from [sikulix.com](https://sikulix.github.io/)
- AutoHotkey: Download from [autohotkey.com](https://www.autohotkey.com/)
- Chrome WebDriver (for Selenium): Download matching version from [chromedriver.chromium.org](https://chromedriver.chromium.org/)

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

1. Basic automation:
```python
from src.core.task_compiler import CompiledTask, TaskStep
from src.agents.planner import Planner

# Create a task
task = CompiledTask(
    id="example_task",
    steps=[
        TaskStep(
            step_id="step1",
            description="Click login button",
            tool_name="PyAutoGUI",
            instruction="click login.png",
            confidence=0.9
        )
    ]
)

# Execute task
planner = Planner(adaptive=True)
success, exit_code = planner.execute_task(task)
```

2. Simulation mode:
```python
# Run in simulation mode
planner = Planner(adaptive=True, simulate=True)
success, exit_code = planner.execute_task(task)
```

3. Tool-specific usage:
```python
from src.tools import sikulix_runner, pyautogui_runner, browser_runner

# Use SikuliX
result = sikulix_runner.runner.run({
    "instruction": "click login.png",
    "confidence": 0.9
})

# Use PyAutoGUI
result = pyautogui_runner.runner.run({
    "instruction": "click(100, 200)",
    "timeout": 5
})

# Use Selenium
result = browser_runner.runner.run({
    "instruction": "click #login-button",
    "timeout": 10
})
```

## Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for LLM support
- SikuliX, PyAutoGUI, AutoHotkey, and other tool creators
- Contributors and testers
