# Term-swords

## Description

Term Swords is a command-line tool developed to replace prohibited stop words in video titles, specifically tailored for compliance with TikTok's guidelines. 

## Key Features

- Stop-word replacement in video titles
- Configurable through command line arguments
- Easily deployable

## Dependencies

To run this project, ensure you have the following Python libraries installed:

```bash
pip install aiogram asyncio argparse langdetect psutil pynvml SQLAlchemy chardet
```

## Usage

### macOS, Linux

#### Default Startup

```bash
python3 term_swords.py
```

or

```bash
python term_swords.py
```

### Customized Startup

- `-fs, --folder_swords`: Folder for stop-word files
- `-ns, --pattern_name_swords`: Pattern name for stop-word files
- `-fl, --folder_logfile`: Folder for log files
- `-lf, --logfile`: Log file name
- `-ll, --loglevel`: Logging level

```bash
python term_swords.py -fs swords -ns swords_ -lf logs.md -ll info
```

### Windows

```bash
start_term_swords.bat
```

## Examples

(TO-DO: Add examples demonstrating the tool's features)

## License

This project is licensed under the MIT License.

## Support

For more information or questions, please feel free to reach out:

- **Contact Person**: Arthur
- **Email**: [kongotoken@gmail.com](mailto:kongotoken@gmail.com)