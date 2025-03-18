# Hikvision Device Info

A Python utility to retrieve and display detailed information from Hikvision surveillance devices using their ISAPI interface.

## Overview

hikvision-device-info is a command-line tool that connects to Hikvision Network Video Recorders (NVRs) and IP cameras to extract comprehensive device information including firmware versions, hardware details, serial numbers, and capabilities. This tool is useful for system administrators, security professionals, and technicians who manage Hikvision surveillance equipment.

## Features

- Retrieve device information via Hikvision's ISAPI REST interface
- Support for digest authentication
- Detailed parsing of XML device information
- Formatted display of device details with logical grouping
- JSON export for integration with other tools
- Error handling with helpful troubleshooting suggestions

## Requirements

- Python 3.6+
- Required Python packages:
  - requests
  - urllib3

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/reiarseni/hikvision-device-info.git
   cd hikvision-device-info
   ```

2. Install required dependencies:
   ```
   pip install requests urllib3
   ```

## Usage

Basic command structure:

```
python hikvision_device_info.py <IP> <username> <password> [port]
```

Example:

```
python3 hikvision_device_info.py 192.168.1.100 admin password123 80
```

By default, port 80 is used if not specified.

## Output

The script outputs device information in three sections:
1. Basic device information (name, model, serial number, etc.)
2. Firmware information (versions and release dates)
3. Additional technical details

Results are also saved to a JSON file (`device_info_result.json`) in the current directory.

## Troubleshooting

If the connection fails, the script provides several troubleshooting suggestions:
- Verify IP address and port
- Check username and password
- Ensure network connectivity to the device
- Try alternative ports (80, 8000)
- Check if HTTPS is required instead of HTTP

## Security Notes

- SSL certificate warnings are disabled by default for compatibility with self-signed certificates
- Credentials are passed via command line arguments, use with caution in shared environments
- Consider using environment variables or a configuration file for credentials in production environments

## License

[MIT License](LICENSE)

## Disclaimer

This tool is not affiliated with or endorsed by Hikvision. Use at your own risk and responsibility.
