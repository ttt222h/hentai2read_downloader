# Hentai2Read Downloader

A modern, modular Python application for downloading manga from hentai2read with both CLI and GUI interfaces.

![GUI Screenshot](gui/gui.PNG)

## Features

- **Dual Interface**: Choose between a beautiful GUI or powerful CLI
- **Parallel Downloads**: Download multiple manga simultaneously with multi-threading
- **Multiple Formats**: Save as images, PDF, or CBZ archives
- **Search Functionality**: Find manga directly within the application
- **Format Conversion**: Convert between formats after downloading
- **Modern UI**: Sleek PyQt6 interface with glass morphism design
- **Configurable**: Customize download paths, performance settings, and more

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yui007/hentai2read_downloader.git
   cd hentai2read_downloader
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode (Recommended)

Launch the graphical user interface:
```bash
python main.py --gui
```
or the shorthand version:
```bash
python main.py -g
```

### CLI Mode

For command-line usage:
```bash
python main.py [COMMAND]
```

To see all available commands:
```bash
python main.py --help
```

### Detailed Usage Guide

For comprehensive instructions on using both the GUI and CLI interfaces, please refer to the [Usage Guide](usage.md).

## Configuration

The application can be configured via:
1. The GUI's Settings tab
2. Editing the `.env` file directly

Key configuration options include:
- Download directory
- Default output format (images, PDF, CBZ)
- Concurrent download limits
- Performance tuning
- Logging options

## Output Formats

- **Images**: Save raw image files in organized folder structure
- **PDF**: Convert images to searchable PDF documents
- **CBZ**: Create comic book archives for readers

## Requirements

- Python 3.8+
- PyQt6
- httpx
- Pillow
- reportlab
- And other dependencies listed in `requirements.txt`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.