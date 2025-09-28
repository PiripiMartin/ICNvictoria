#!/usr/bin/env python3
"""
Geocoding script for addresses in alldata.csv
Supports multiple geocoding services with fallback options
"""

import csv
import time
import requests
import json
from typing import Dict, List, Tuple, Optional
import argparse
import sys
from urllib.parse import quote

class AddressGeocoder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Address Geocoder 1.0'
        })
        
    def geocode_nominatim(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using OpenStreetMap Nominatim (free, no API key required)
        Rate limit: 1 request per second
        """
        try:
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'au'  # Limit to Australia based on your data
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
                
        except Exception as e:
            print(f"Nominatim error for '{address}': {e}")
            
        return None
    
    def geocode_photon(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using Photon (free, no API key required)
        Alternative to Nominatim
        """
        try:
            url = "https://photon.komoot.io/api/"
            params = {
                'q': address,
                'limit': 1,
                'osm_tag': 'place'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('features'):
                coords = data['features'][0]['geometry']['coordinates']
                # Photon returns [lon, lat], we want (lat, lon)
                return (coords[1], coords[0])
                
        except Exception as e:
            print(f"Photon error for '{address}': {e}")
            
        return None
    
    def format_address(self, street: str, city: str, state: str, postcode: str) -> str:
        """Format address components into a single string"""
        parts = []
        
        if street and street.strip() and street != '#N/A':
            parts.append(street.strip().rstrip(','))
        if city and city.strip() and city != '#N/A':
            parts.append(city.strip())
        if state and state.strip() and state != '#N/A':
            parts.append(state.strip())
        if postcode and postcode.strip() and postcode != '#N/A':
            parts.append(postcode.strip())
            
        return ', '.join(parts)
    
    def geocode_address(self, street: str, city: str, state: str, postcode: str) -> Dict:
        """
        Geocode a single address using multiple services with fallback
        """
        address = self.format_address(street, city, state, postcode)
        
        if not address or address.strip() == '':
            return {
                'formatted_address': '',
                'latitude': None,
                'longitude': None,
                'geocoding_service': None,
                'status': 'empty_address'
            }
        
        print(f"Geocoding: {address}")
        
        # Try Nominatim first
        coords = self.geocode_nominatim(address)
        if coords:
            return {
                'formatted_address': address,
                'latitude': coords[0],
                'longitude': coords[1],
                'geocoding_service': 'nominatim',
                'status': 'success'
            }
        
        # No wait between services for faster processing
        
        # Try Photon as fallback
        coords = self.geocode_photon(address)
        if coords:
            return {
                'formatted_address': address,
                'latitude': coords[0],
                'longitude': coords[1],
                'geocoding_service': 'photon',
                'status': 'success'
            }
        
        return {
            'formatted_address': address,
            'latitude': None,
            'longitude': None,
            'geocoding_service': None,
            'status': 'failed'
        }

def process_csv(input_file: str, output_file: str, start_row: int = 0, max_rows: int = None):
    """Process the CSV file and add geocoding results"""
    
    geocoder = AddressGeocoder()
    batch_results = []
    processed_count = 0
    success_count = 0
    batch_size = 10
    
    print(f"Reading {input_file}...")
    
    # Initialize output file with headers
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Read header row
        
        # Add new columns for geocoding results
        new_headers = headers + [
            'Formatted_Address',
            'Latitude', 
            'Longitude',
            'Geocoding_Service',
            'Geocoding_Status'
        ]
        
        # Write headers to output file
        with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(new_headers)
        
        # Skip to start row if specified
        for _ in range(start_row):
            try:
                next(reader)
            except StopIteration:
                break
        
        for row_num, row in enumerate(reader, start=start_row + 1):
            if max_rows and processed_count >= max_rows:
                break
                
            # Skip subtotal rows and rows with #N/A addresses
            if (len(row) > 10 and 
                row[10] not in ['#N/A', '', None] and 
                not row[0].startswith('Subtotal')):
                
                # Extract address components (columns 10-13 are indices 10-13)
                street = row[10] if len(row) > 10 else ''
                city = row[11] if len(row) > 11 else ''
                state = row[12] if len(row) > 12 else ''
                postcode = row[13] if len(row) > 13 else ''
                
                # Geocode the address
                geocode_result = geocoder.geocode_address(street, city, state, postcode)
                
                if geocode_result['status'] == 'success':
                    success_count += 1
                
                # Add geocoding results to the row
                new_row = row + [
                    geocode_result['formatted_address'],
                    geocode_result['latitude'],
                    geocode_result['longitude'],
                    geocode_result['geocoding_service'],
                    geocode_result['status']
                ]
                
                processed_count += 1
                print(f"Processed {processed_count} addresses, {success_count} successful")
                
                # No rate limiting for faster processing
                
            else:
                # For rows without addresses, add empty geocoding columns
                new_row = row + ['', '', '', '', 'skipped']
            
            batch_results.append(new_row)
            
            # Write batch when we reach batch_size
            if len(batch_results) >= batch_size:
                with open(output_file, 'a', encoding='utf-8', newline='') as out_f:
                    writer = csv.writer(out_f)
                    writer.writerows(batch_results)
                print(f"Wrote batch of {len(batch_results)} rows to {output_file}")
                batch_results = []  # Clear the batch
        
        # Write any remaining results in the final batch
        if batch_results:
            with open(output_file, 'a', encoding='utf-8', newline='') as out_f:
                writer = csv.writer(out_f)
                writer.writerows(batch_results)
            print(f"Wrote final batch of {len(batch_results)} rows to {output_file}")
    
    print(f"\nCompleted!")
    print(f"Total addresses processed: {processed_count}")
    print(f"Successfully geocoded: {success_count}")
    print(f"Success rate: {success_count/processed_count*100:.1f}%" if processed_count > 0 else "No addresses processed")

def main():
    parser = argparse.ArgumentParser(description='Geocode addresses in CSV file')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('-o', '--output', help='Output CSV file path', 
                       default='alldata_with_coordinates.csv')
    parser.add_argument('-s', '--start', type=int, default=0,
                       help='Start row number (0-based, default: 0)')
    parser.add_argument('-m', '--max', type=int, 
                       help='Maximum number of addresses to process')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - process only first 10 addresses')
    
    args = parser.parse_args()
    
    if args.test:
        args.max = 10
        args.output = 'test_geocoding_results.csv'
        print("Running in test mode - processing first 10 addresses only")
    
    try:
        process_csv(args.input_file, args.output, args.start, args.max)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
