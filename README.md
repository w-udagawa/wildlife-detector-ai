# Wildlife Detector AI v2.0

AI-powered wildlife species detection application using Google SpeciesNet.

## 🌟 Features

- **High Accuracy**: 94.5% species-level classification accuracy using Google SpeciesNet
- **Batch Processing**: Process thousands of images efficiently
- **Multiple Output Formats**: CSV export with detailed detection results
- **Automatic File Organization**: Organize images by detected species
- **GUI and CLI**: User-friendly desktop interface and command-line tools
- **Research-Ready**: English/scientific names for academic use

## 📋 Requirements

- Python 3.12.10+
- Windows 10/11 (Linux/macOS support coming soon)
- 4GB+ RAM recommended
- GPU optional (for faster processing)

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wildlife-detector.git
cd wildlife-detector
```

2. Run the setup script:
```bash
scripts\quick_setup.bat
```

Or manually:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

#### GUI Mode (Recommended)
```bash
python main.py
```

#### CLI Mode
```bash
# Single image
python main.py --image path/to/image.jpg

# Batch processing
python main.py --batch path/to/image/folder --output results/
```

## 📁 Project Structure

```
wildlife-detector/
├── core/               # Core detection modules
├── gui/                # GUI components
├── utils/              # Utility functions
├── scripts/            # Setup and utility scripts
├── tests/              # Test files and scripts
├── docs/               # Documentation
│   ├── development/    # Development notes
│   └── user/           # User guides
├── config.yaml         # Configuration file
├── main.py             # Main entry point
└── requirements.txt    # Python dependencies
```

## 🔧 Configuration

Edit `config.yaml` to customize:
- Detection confidence threshold
- Output formats
- Processing options
- GUI preferences

## 📊 Output Format

Detection results are exported as CSV with the following columns:
- **Image File**: Source image filename
- **Species Name**: Detected species (scientific/common name)
- **Confidence**: Detection confidence (0-1)
- **Category**: Animal category (bird, mammal, etc.)
- **Bounding Box**: Object location coordinates

## 🗂️ File Organization

The application can automatically organize detected images into species folders:
```
output/
├── Corvus_macrorhynchos/    # Large-billed crow
├── Ardea_sp/                # Heron species
├── Sus_scrofa/              # Wild boar
├── no_detection/            # No animals detected
└── low_confidence/          # Below threshold
```

## 🧪 Testing

Run tests using the provided scripts:
```bash
# Test CLI functionality
tests\scripts\test_cli.bat

# Test with sample images
tests\scripts\test_crow.bat
```

## 📝 Documentation

- [CLAUDE.md](CLAUDE.md) - Development guide
- [SPECIESNET_GUIDE.md](SPECIESNET_GUIDE.md) - SpeciesNet usage guide
- [docs/](docs/) - Additional documentation

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google SpeciesNet team for the amazing wildlife detection model
- All contributors and testers

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder

---

**Version**: 2.0.0  
**Last Updated**: 2025-06-25  
**Status**: Production Ready
