# 🚀 Claudeworks - AI Development Workspace

Welcome to Claudeworks - A organized workspace for AI-powered applications and experiments.

## 📁 Directory Structure

```
Claudeworks/
├── projects/              # Individual project folders
│   ├── wildlife-detector/ # Wildlife detection app using SpeciesNet
│   ├── kankyo-news/      # Environmental news aggregator
│   └── teams-ai-bot/     # Microsoft Teams AI chatbot
│
├── environments/         # Python virtual environments
│   └── wildlife_env_312/ # Python 3.12 environment
│
├── shared/              # Shared resources across projects
│   ├── testimages/      # Test images for various projects
│   └── results/         # Output results directory
│
├── docs/                # Documentation
│   ├── QUICKSTART.md    # Quick start guide
│   └── CONTRIBUTING.md  # Contribution guidelines
│
└── scripts/             # Utility scripts
```

## 🎯 Projects Overview

### 1. Wildlife Detector 🦅
- **Description**: Desktop application for detecting wildlife in images
- **Tech Stack**: Python, PySide6, Google SpeciesNet
- **Status**: Active development
- **Repository**: [GitHub](https://github.com/w-udagawa/wildlife-speciesnet-detector)

### 2. Kankyo News 📰
- **Description**: Environmental news aggregator and analyzer
- **Tech Stack**: Python, Web scraping
- **Status**: In development

### 3. Teams AI Bot 🤖
- **Description**: AI-powered chatbot for Microsoft Teams
- **Tech Stack**: Python, Microsoft Bot Framework
- **Status**: Prototype

## 🛠️ Getting Started

### Prerequisites
- Python 3.12+
- Git
- Virtual environment tool (venv)

### Setting Up a Project

1. Navigate to the project directory:
   ```bash
   cd projects/[project-name]
   ```

2. Activate the appropriate virtual environment:
   ```bash
   # For wildlife-detector
   ..\..\environments\wildlife_env_312\Scripts\activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the project:
   ```bash
   python main.py
   ```

## 📝 Development Guidelines

### Project Structure
Each project should follow this structure:
```
project-name/
├── src/           # Source code
├── tests/         # Unit tests
├── docs/          # Project documentation
├── requirements.txt
├── README.md
└── .gitignore
```

### Virtual Environments
- Create separate environments for projects with different dependencies
- Name format: `{project}_env_{python_version}`
- Store in `environments/` directory

### Shared Resources
- Test data goes in `shared/testimages/`
- Output files go in `shared/results/`
- Don't store sensitive data in shared folders

## 🤝 Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## 📄 License

Individual projects may have their own licenses. Check each project's LICENSE file.

## 🔗 Quick Links

- [Wildlife Detector README](projects/wildlife-detector/README.md)
- [Quick Start Guide](docs/QUICKSTART.md)
- [Python Setup Guide](docs/python_setup.md)

---
*Last updated: June 2025*
