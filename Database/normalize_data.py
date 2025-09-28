#!/usr/bin/env python3
"""
Data normalization script for ICN Database
Extracts data from alldata_with_coordinates.csv and creates normalized tables
"""

import csv
import json
from datetime import datetime
from typing import Dict, Set, List
import argparse

class DataNormalizer:
    def __init__(self):
        self.items = {}  # itemId -> itemName
        self.detailed_items = {}  # detailedItemId -> {detailedItemName, itemId}
        self.sectors = {}  # sectorMappingId -> sectorName
        self.organisations = {}  # organisationId -> organisation info
        self.capabilities = []  # List of capability records
        
    def process_csv(self, input_file: str):
        """Process the CSV file and extract normalized data"""
        
        print(f"Processing {input_file}...")
        
        # Keep track of the current detailed item ID and sector mapping ID for grouped rows
        current_detailed_item_id = None
        current_sector_mapping_id = None
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
                # Skip rows without valid organisation data
                if not row.get('Organisation: Organisation ID') or row.get('Organisation: Organisation ID').strip() == '':
                    continue
                
                # Extract and store Items
                item_id = row.get('Item ID', '').strip()
                item_name = row.get('Item Name', '').strip()
                if item_id and item_name:
                    self.items[item_id] = item_name
                
                # Handle grouped detailed item IDs (handle BOM in column name)
                detailed_item_id_raw = row.get('\ufeffDetailed Item ID  ↓', '') or row.get('Detailed Item ID  ↓', '')
                detailed_item_id_raw = detailed_item_id_raw.strip()
                detailed_item_name = row.get('Detailed Item Name', '').strip()
                
                # If we have a new detailed item ID, update our current one
                if detailed_item_id_raw and detailed_item_id_raw != 'Subtotal':
                    current_detailed_item_id = detailed_item_id_raw
                    # Store the detailed item when we first encounter it
                    if detailed_item_name:
                        self.detailed_items[current_detailed_item_id] = {
                            'detailedItemName': detailed_item_name,
                            'itemId': item_id if item_id else None
                        }
                
                # Use the current detailed item ID for this organisation
                detailed_item_id = current_detailed_item_id
                
                # Extract and store Sectors - handle grouped rows like detailed items
                sector_mapping_id_raw = row.get('Sector Mapping ID', '').strip()
                sector_name = row.get('Sector Name', '').strip()
                
                # If we have a new sector mapping ID, update current tracking
                if sector_mapping_id_raw:
                    current_sector_mapping_id = sector_mapping_id_raw
                    sector_mapping_id = sector_mapping_id_raw
                else:
                    # Use the current sector mapping ID from previous rows
                    sector_mapping_id = current_sector_mapping_id
                
                # Store sector if we have both ID and name
                if sector_mapping_id and sector_name:
                    self.sectors[sector_mapping_id] = sector_name
                
                # Extract Organisation and Capability data
                organisation_id_raw = row.get('Organisation: Organisation ID', '').strip()
                # Normalize organisation ID to handle case variations (treat as same organisation)
                organisation_id = organisation_id_raw.upper() if organisation_id_raw else ''
                if organisation_id:
                    # Parse validation date
                    validation_date = None
                    date_str = row.get('Validation Date', '').strip()
                    if date_str:
                        try:
                            # Handle different date formats
                            if '/' in date_str:
                                validation_date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                            else:
                                validation_date = date_str
                        except ValueError:
                            validation_date = None
                    
                    # Parse coordinates
                    latitude = None
                    longitude = None
                    try:
                        lat_str = row.get('Latitude', '').strip()
                        lon_str = row.get('Longitude', '').strip()
                        if lat_str and lat_str != '':
                            latitude = float(lat_str)
                        if lon_str and lon_str != '':
                            longitude = float(lon_str)
                    except (ValueError, TypeError):
                        pass
                    
                    # Store/update organisation info (merge data from multiple rows)
                    if organisation_id not in self.organisations:
                        # First time seeing this organisation
                        organisation = {
                            'organisationId': organisation_id,
                            'organisationName': row.get('Organisation: Organisation Name', '').strip() or None,
                            'billingStreet': row.get('Organisation: Billing Street', '').strip() or None,
                            'billingCity': row.get('Organisation: Billing City', '').strip() or None,
                            'billingStateProvince': row.get('Organisation: Billing State/Province', '').strip() or None,
                            'billingZipPostalCode': row.get('Organisation: Billing Zip/Postal Code', '').strip() or None,
                            'formattedAddress': row.get('Formatted_Address', '').strip() or None,
                            'latitude': latitude,
                            'longitude': longitude
                        }
                        self.organisations[organisation_id] = organisation
                    else:
                        # Update existing organisation with any missing data
                        existing = self.organisations[organisation_id]
                        
                        # Update fields if they're currently None/empty and we have new data
                        if not existing['organisationName']:
                            existing['organisationName'] = row.get('Organisation: Organisation Name', '').strip() or None
                        if not existing['billingStreet']:
                            existing['billingStreet'] = row.get('Organisation: Billing Street', '').strip() or None
                        if not existing['billingCity']:
                            existing['billingCity'] = row.get('Organisation: Billing City', '').strip() or None
                        if not existing['billingStateProvince']:
                            existing['billingStateProvince'] = row.get('Organisation: Billing State/Province', '').strip() or None
                        if not existing['billingZipPostalCode']:
                            existing['billingZipPostalCode'] = row.get('Organisation: Billing Zip/Postal Code', '').strip() or None
                        if not existing['formattedAddress']:
                            existing['formattedAddress'] = row.get('Formatted_Address', '').strip() or None
                        if not existing['latitude'] and latitude:
                            existing['latitude'] = latitude
                        if not existing['longitude'] and longitude:
                            existing['longitude'] = longitude
                    
                    # Store capability record
                    organisation_capability = row.get('Organisation Capability', '').strip()
                    if organisation_capability:
                        capability = {
                            'organisationCapability': organisation_capability,
                            'organisationId': organisation_id,  # Use normalized (uppercase) organisation ID
                            'itemId': item_id if item_id else None,
                            'detailedItemId': detailed_item_id if detailed_item_id else None,
                            'capabilityType': row.get('Capability Type', '').strip() or None,
                            'validationDate': validation_date,
                            'sectorMappingId': sector_mapping_id if sector_mapping_id else None
                        }
                        self.capabilities.append(capability)
                
                if row_num % 100 == 0:
                    print(f"Processed {row_num} rows...")
        
        print(f"Extraction complete!")
        print(f"Found {len(self.items)} unique items")
        print(f"Found {len(self.detailed_items)} unique detailed items")
        print(f"Found {len(self.sectors)} unique sectors")
        print(f"Found {len(self.organisations)} unique organisations")
        print(f"Found {len(self.capabilities)} capabilities")
    
    def generate_sql_inserts(self, output_file: str):
        """Generate SQL INSERT statements for all tables"""
        
        print(f"Generating SQL INSERT statements to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- SQL INSERT statements for ICN Database\n")
            f.write("-- Generated from alldata_with_coordinates.csv\n\n")
            
            # Items table inserts
            f.write("-- Items table inserts\n")
            for item_id, item_name in self.items.items():
                escaped_name = item_name.replace("'", "''")
                f.write(f"INSERT INTO Items (itemId, itemName) VALUES ('{item_id}', '{escaped_name}');\n")
            f.write("\n")
            
            # DetailedItems table inserts
            f.write("-- DetailedItems table inserts\n")
            for detailed_item_id, data in self.detailed_items.items():
                escaped_name = data['detailedItemName'].replace("'", "''")
                item_id_value = f"'{data['itemId']}'" if data['itemId'] else 'NULL'
                f.write(f"INSERT INTO DetailedItems (detailedItemId, detailedItemName, itemId) VALUES ('{detailed_item_id}', '{escaped_name}', {item_id_value});\n")
            f.write("\n")
            
            # Sectors table inserts
            f.write("-- Sectors table inserts\n")
            for sector_id, sector_name in self.sectors.items():
                escaped_name = sector_name.replace("'", "''")
                f.write(f"INSERT INTO Sectors (sectorMappingId, sectorName) VALUES ('{sector_id}', '{escaped_name}');\n")
            f.write("\n")
            
            # Escape string values and handle NULLs
            def format_value(value):
                if value is None or value == '':
                    return 'NULL'
                elif isinstance(value, (int, float)):
                    return str(value)
                else:
                    return f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"
            
            # Organisations table inserts
            f.write("-- Organisations table inserts\n")
            for org_id, org in self.organisations.items():
                values = [
                    format_value(org['organisationId']),
                    format_value(org['organisationName']),
                    format_value(org['billingStreet']),
                    format_value(org['billingCity']),
                    format_value(org['billingStateProvince']),
                    format_value(org['billingZipPostalCode']),
                    format_value(org['formattedAddress']),
                    format_value(org['latitude']),
                    format_value(org['longitude'])
                ]
                
                f.write(f"INSERT INTO Organisations (organisationId, organisationName, billingStreet, billingCity, billingStateProvince, billingZipPostalCode, formattedAddress, latitude, longitude) VALUES ({', '.join(values)});\n")
            f.write("\n")
            
            # Capabilities table inserts
            f.write("-- Capabilities table inserts\n")
            for cap in self.capabilities:
                values = [
                    format_value(cap['organisationCapability']),
                    format_value(cap['organisationId']),
                    format_value(cap['itemId']),
                    format_value(cap['detailedItemId']),
                    format_value(cap['capabilityType']),
                    format_value(cap['validationDate']),
                    format_value(cap['sectorMappingId'])
                ]
                
                f.write(f"INSERT INTO Capabilities (organisationCapability, organisationId, itemId, detailedItemId, capabilityType, validationDate, sectorMappingId) VALUES ({', '.join(values)});\n")
            
        print(f"SQL INSERT statements generated successfully!")
    
    def export_to_csv(self, output_dir: str):
        """Export normalized data to separate CSV files"""
        
        print(f"Exporting normalized data to CSV files in {output_dir}...")
        
        # Items CSV
        with open(f"{output_dir}/items.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['itemId', 'itemName'])
            for item_id, item_name in self.items.items():
                writer.writerow([item_id, item_name])
        
        # DetailedItems CSV
        with open(f"{output_dir}/detailed_items.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['detailedItemId', 'detailedItemName', 'itemId'])
            for detailed_item_id, data in self.detailed_items.items():
                writer.writerow([detailed_item_id, data['detailedItemName'], data['itemId']])
        
        # Sectors CSV
        with open(f"{output_dir}/sectors.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sectorMappingId', 'sectorName'])
            for sector_id, sector_name in self.sectors.items():
                writer.writerow([sector_id, sector_name])
        
        # Organisations CSV
        with open(f"{output_dir}/organisations.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'organisationId', 'organisationName', 'billingStreet', 'billingCity',
                'billingStateProvince', 'billingZipPostalCode', 'formattedAddress',
                'latitude', 'longitude'
            ])
            for org_id, org in self.organisations.items():
                writer.writerow([
                    org['organisationId'], org['organisationName'], org['billingStreet'],
                    org['billingCity'], org['billingStateProvince'], org['billingZipPostalCode'],
                    org['formattedAddress'], org['latitude'], org['longitude']
                ])
        
        # Capabilities CSV
        with open(f"{output_dir}/capabilities.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'organisationCapability', 'organisationId', 'itemId', 'detailedItemId',
                'capabilityType', 'validationDate', 'sectorMappingId'
            ])
            for cap in self.capabilities:
                writer.writerow([
                    cap['organisationCapability'], cap['organisationId'], cap['itemId'],
                    cap['detailedItemId'], cap['capabilityType'], cap['validationDate'],
                    cap['sectorMappingId']
                ])
        
        print(f"CSV files exported successfully!")

def main():
    parser = argparse.ArgumentParser(description='Normalize ICN database data')
    parser.add_argument('input_file', help='Input CSV file with coordinates')
    parser.add_argument('-s', '--sql', help='Output SQL file path', default='database_inserts.sql')
    parser.add_argument('-c', '--csv-dir', help='Output directory for CSV files', default='normalized_csv')
    parser.add_argument('--sql-only', action='store_true', help='Generate only SQL file')
    parser.add_argument('--csv-only', action='store_true', help='Generate only CSV files')
    
    args = parser.parse_args()
    
    normalizer = DataNormalizer()
    normalizer.process_csv(args.input_file)
    
    if not args.csv_only:
        normalizer.generate_sql_inserts(args.sql)
    
    if not args.sql_only:
        import os
        os.makedirs(args.csv_dir, exist_ok=True)
        normalizer.export_to_csv(args.csv_dir)

if __name__ == '__main__':
    main()
