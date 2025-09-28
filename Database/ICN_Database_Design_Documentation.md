# ICN Database Design Documentation

## Overview

The ICN (Industrial Capability Network) Database is a normalized relational database designed to store and manage information about industrial organizations, their capabilities, items, and geographical locations. The database has been designed with proper normalization principles to eliminate data redundancy and ensure data integrity.

## Database Architecture

### Design Principles
- **Normalization**: The database follows 3NF (Third Normal Form) principles to minimize data redundancy
- **Referential Integrity**: Foreign key relationships ensure data consistency across tables
- **Scalability**: Indexed columns provide optimal query performance
- **Data Quality**: Proper data types and constraints ensure data accuracy

### Technology Stack
- **Database Engine**: Compatible with MySQL, PostgreSQL, SQL Server, and other ANSI SQL databases
- **Character Encoding**: UTF-8 for international character support
- **Naming Convention**: camelCase for all column names

## Table Structure

### 1. Items Table
**Purpose**: Stores high-level item categories and types

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| itemId | VARCHAR(50) | PRIMARY KEY | Unique identifier for each item type (e.g., ITM-002348) |
| itemName | VARCHAR(255) | NOT NULL | Descriptive name of the item category (e.g., "instrumentation") |

**Sample Data**:
```
ITM-002348 | instrumentation
ITM-002726 | dust and fume extraction system
ITM-002397 | tanks
```

**Record Count**: 28 unique items

---

### 2. DetailedItems Table
**Purpose**: Stores specific detailed descriptions of items with relationships to parent items

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| detailedItemId | VARCHAR(50) | PRIMARY KEY | Unique identifier for detailed item (e.g., DITM-000530) |
| detailedItemName | VARCHAR(500) | NOT NULL | Specific description of the detailed item |
| itemId | VARCHAR(50) | FOREIGN KEY | References Items.itemId - links to parent item category |

**Sample Data**:
```
DITM-000530 | Process control & instrumentation (PLC/SCADA) | ITM-002348
DITM-000529 | Dust collectors, scrubbers, and gas handling | ITM-002726
DITM-000528 | Precipitation Tanks | ITM-002397
```

**Record Count**: 51 unique detailed items

**Relationships**:
- Many-to-One relationship with Items table
- One detailed item belongs to one item category
- One item category can have multiple detailed items

---

### 3. Sectors Table
**Purpose**: Stores industry sector classifications

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| sectorMappingId | VARCHAR(50) | PRIMARY KEY | Unique identifier for sector (e.g., SM-000524) |
| sectorName | VARCHAR(255) | NOT NULL | Name of the industry sector |

**Sample Data**:
```
SM-000524 | Critical Minerals
SM-000521 | Critical Minerals
SM-000515 | Critical Minerals
```

**Record Count**: 51 unique sectors

---

### 4. Organisations Table
**Purpose**: Central table storing all organization information with geographical coordinates

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| organisationId | VARCHAR(50) | PRIMARY KEY | Unique identifier for organization |
| itemId | VARCHAR(50) | FOREIGN KEY | References Items.itemId |
| detailedItemId | VARCHAR(50) | FOREIGN KEY | References DetailedItems.detailedItemId |
| organisationCapability | VARCHAR(50) | | Organization capability identifier |
| organisationName | VARCHAR(500) | | Full name of the organization |
| capabilityType | VARCHAR(100) | | Type of capability (e.g., Supplier, Manufacturer) |
| validationDate | DATE | | Date when the information was validated |
| billingStreet | VARCHAR(500) | | Street address for billing |
| billingCity | VARCHAR(255) | | City for billing address |
| billingStateProvince | VARCHAR(100) | | State or province |
| billingZipPostalCode | VARCHAR(20) | | ZIP or postal code |
| sectorMappingId | VARCHAR(50) | FOREIGN KEY | References Sectors.sectorMappingId |
| formattedAddress | VARCHAR(1000) | | Complete formatted address string |
| latitude | DECIMAL(10, 8) | | Geographical latitude coordinate |
| longitude | DECIMAL(11, 8) | | Geographical longitude coordinate |

**Record Count**: 2,840 organizations with geocoded locations

**Sample Data**:
```
0017F00001ueIkz | ITM-002348 | DITM-000530 | OC-018234 | [Org Name] | Supplier | 2025-07-01 | 885 Mountain Highway | Bayswater | VIC | 3153 | SM-000524 | 885 Mountain Highway, Bayswater, VIC, 3153 | -37.8377841 | 145.2801042
```

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   Items     │       │  DetailedItems   │       │   Organisations │
├─────────────┤       ├──────────────────┤       ├─────────────────┤
│ itemId (PK) │◄──────┤ detailedItemId   │◄──────┤ organisationId  │
│ itemName    │       │ (PK)             │       │ (PK)            │
└─────────────┘       │ detailedItemName │       │ itemId (FK)     │
                      │ itemId (FK)      │       │ detailedItemId  │
                      └──────────────────┘       │ (FK)            │
                                                 │ ...             │
┌─────────────┐                                 │ sectorMappingId │
│  Sectors    │                                 │ (FK)            │
├─────────────┤                                 │ latitude        │
│ sectorMap-  │◄────────────────────────────────┤ longitude       │
│ pingId (PK) │                                 │ ...             │
│ sectorName  │                                 └─────────────────┘
└─────────────┘
```

## Relationships and Constraints

### Foreign Key Relationships

1. **DetailedItems → Items**
   - `DetailedItems.itemId` references `Items.itemId`
   - Ensures every detailed item belongs to a valid item category

2. **Organisations → Items**
   - `Organisations.itemId` references `Items.itemId`
   - Links organizations to their primary item categories

3. **Organisations → DetailedItems**
   - `Organisations.detailedItemId` references `DetailedItems.detailedItemId`
   - Links organizations to specific detailed item capabilities

4. **Organisations → Sectors**
   - `Organisations.sectorMappingId` references `Sectors.sectorMappingId`
   - Associates organizations with industry sectors

### Data Integrity Rules

- All primary keys are non-null and unique
- Foreign key constraints prevent orphaned records
- Date fields use ISO 8601 format (YYYY-MM-DD)
- Coordinate precision: Latitude (10,8), Longitude (11,8) for accurate geolocation

## Indexing Strategy

### Primary Indexes
- All primary keys are automatically indexed

### Performance Indexes
```sql
-- Foreign key indexes for join performance
CREATE INDEX idxOrganisationsItem ON Organisations(itemId);
CREATE INDEX idxOrganisationsDetailedItem ON Organisations(detailedItemId);
CREATE INDEX idxOrganisationsSector ON Organisations(sectorMappingId);
CREATE INDEX idxDetailedItemsItem ON DetailedItems(itemId);

-- Geographic and search indexes
CREATE INDEX idxOrganisationsLocation ON Organisations(latitude, longitude);
CREATE INDEX idxOrganisationsCapabilityType ON Organisations(capabilityType);
CREATE INDEX idxOrganisationsCity ON Organisations(billingCity);
CREATE INDEX idxOrganisationsState ON Organisations(billingStateProvince);
```

## Data Sources and Processing

### Source Data
- **Original Dataset**: 20,486 rows from alldata.csv
- **Geocoded Dataset**: 3,262 rows with coordinates from alldata_with_coordinates.csv
- **Processing Success Rate**: ~87% geocoding success rate

### Data Processing Pipeline

1. **Geocoding Process**
   - Used OpenStreetMap Nominatim API for address geocoding
   - Batch processing with 10-record increments
   - Fallback to Photon geocoding service
   - Rate limiting removed for faster processing

2. **Normalization Process**
   - Extracted unique items, detailed items, and sectors
   - Handled grouped data structure (detailed item IDs span multiple rows)
   - Resolved UTF-8 BOM character encoding issues
   - Generated foreign key relationships

3. **Data Quality Measures**
   - Skipped rows without valid organization IDs
   - Handled missing or null values appropriately
   - Validated coordinate ranges and formats

## Geographic Coverage

### Coordinate System
- **Format**: Decimal degrees (WGS84)
- **Precision**: 8 decimal places for latitude, 8 decimal places for longitude
- **Coverage**: Primarily Australian addresses

### Geographic Distribution
- **States Covered**: VIC, NSW, QLD, WA, SA, TAS, NT, ACT
- **Address Types**: Street addresses, unit numbers, PO boxes, industrial complexes
- **Geocoding Accuracy**: Street-level precision for most addresses

## Usage Examples

### Common Queries

**Find all organizations in a specific sector:**
```sql
SELECT o.organisationName, o.billingCity, o.billingStateProvince
FROM Organisations o
JOIN Sectors s ON o.sectorMappingId = s.sectorMappingId
WHERE s.sectorName = 'Critical Minerals';
```

**Get organizations by item category:**
```sql
SELECT o.organisationName, i.itemName, di.detailedItemName
FROM Organisations o
JOIN Items i ON o.itemId = i.itemId
JOIN DetailedItems di ON o.detailedItemId = di.detailedItemId
WHERE i.itemName = 'instrumentation';
```

**Geographic proximity search:**
```sql
SELECT organisationName, billingCity, 
       SQRT(POW(latitude - (-37.8377841), 2) + POW(longitude - (145.2801042), 2)) as distance
FROM Organisations
WHERE latitude BETWEEN -38.0 AND -37.5
  AND longitude BETWEEN 145.0 AND 145.5
ORDER BY distance;
```

## Deployment Information

### Database Files Generated
- **Schema**: `database_schema.sql` - Complete DDL statements
- **Data**: `database_inserts.sql` - All INSERT statements (2,981 lines)
- **CSV Exports**: Individual table exports in `normalized_csv/` directory

### System Requirements
- Database server with UTF-8 support
- Minimum 100MB storage for data and indexes
- Support for DECIMAL data types for coordinates

### Backup and Maintenance
- Regular backups recommended due to geocoded coordinate data
- Index maintenance for optimal query performance
- Consider partitioning Organisations table if dataset grows significantly

## Data Governance

### Data Quality Metrics
- **Completeness**: 100% for required fields
- **Accuracy**: 87% successful geocoding rate
- **Consistency**: Normalized structure eliminates redundancy
- **Timeliness**: Validation dates tracked per organization

### Privacy and Security
- No personally identifiable information (PII) stored
- Business addresses are public information
- Consider access controls for sensitive capability information

---

*Last Updated: [Current Date]*  
*Database Version: 1.0*  
*Total Records: 2,840 organizations across 4 normalized tables*
