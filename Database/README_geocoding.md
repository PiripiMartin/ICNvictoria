# Address Geocoding for alldata.csv

This script will add latitude and longitude coordinates to all addresses in your CSV file.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test with first 10 addresses:**
   ```bash
   python geocode_addresses.py alldata.csv --test
   ```

3. **Process all addresses:**
   ```bash
   python geocode_addresses.py alldata.csv -o alldata_with_coordinates.csv
   ```

## Features

- **Free geocoding**: Uses OpenStreetMap Nominatim and Photon (no API keys required)
- **Rate limiting**: Respects service limits (1 request per second)
- **Error handling**: Continues processing even if some addresses fail
- **Progress tracking**: Shows real-time progress and success rates
- **Fallback services**: Tries multiple geocoding services for better coverage
- **Australian focus**: Optimized for Australian addresses

## Output

The script adds these columns to your CSV:
- `Formatted_Address`: Clean formatted address string
- `Latitude`: Decimal latitude coordinate
- `Longitude`: Decimal longitude coordinate  
- `Geocoding_Service`: Which service provided the coordinates
- `Geocoding_Status`: success/failed/empty_address/skipped

## Options

```bash
python geocode_addresses.py INPUT_FILE [options]

Options:
  -o, --output OUTPUT_FILE    Output file name (default: alldata_with_coordinates.csv)
  -s, --start ROW_NUMBER     Start from specific row (useful for resuming)
  -m, --max NUMBER           Maximum addresses to process
  --test                     Test mode (process first 10 addresses only)
```

## Examples

**Test run:**
```bash
python geocode_addresses.py alldata.csv --test
```

**Process specific range:**
```bash
python geocode_addresses.py alldata.csv -s 100 -m 50 -o partial_results.csv
```

**Resume from row 500:**
```bash
python geocode_addresses.py alldata.csv -s 500 -o resumed_results.csv
```

## Performance

- **Speed**: ~1 address per second (due to rate limiting)
- **Estimated time**: ~5.7 hours for 20,486 addresses
- **Success rate**: Typically 85-95% for Australian addresses

## Tips

1. **Start with test mode** to verify everything works
2. **Run in batches** if you have a large dataset
3. **Check your internet connection** - the script needs stable internet
4. **Be patient** - geocoding takes time due to rate limits
5. **Resume capability** - use `-s` option to resume from where you left off

## Troubleshooting

- **Slow internet**: Increase timeout in script if needed
- **Rate limiting errors**: The script handles this automatically
- **Failed addresses**: Check the `Geocoding_Status` column for details
- **Interrupted process**: Use `-s` option to resume from last processed row
