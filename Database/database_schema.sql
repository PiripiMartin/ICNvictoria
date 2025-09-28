-- Database Schema for ICN Database
-- Normalized structure with proper foreign key relationships

-- Items table - contains unique items
CREATE TABLE Items (
    itemId VARCHAR(50) PRIMARY KEY,
    itemName VARCHAR(255) NOT NULL
);

-- DetailedItems table - contains detailed item information
CREATE TABLE DetailedItems (
    detailedItemId VARCHAR(50) PRIMARY KEY,
    detailedItemName VARCHAR(500) NOT NULL,
    itemId VARCHAR(50),
    FOREIGN KEY (itemId) REFERENCES Items(itemId)
);

-- Sectors table - contains sector information
CREATE TABLE Sectors (
    sectorMappingId VARCHAR(50) PRIMARY KEY,
    sectorName VARCHAR(255) NOT NULL
);

-- Organisations table - contains basic organisation information
CREATE TABLE Organisations (
    organisationId VARCHAR(50) PRIMARY KEY,
    organisationName VARCHAR(500),
    billingStreet VARCHAR(500),
    billingCity VARCHAR(255),
    billingStateProvince VARCHAR(100),
    billingZipPostalCode VARCHAR(20),
    formattedAddress VARCHAR(1000),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

-- Capabilities table - contains organisation capabilities and relationships
CREATE TABLE Capabilities (
    organisationCapability VARCHAR(50) PRIMARY KEY,
    organisationId VARCHAR(50),
    itemId VARCHAR(50),
    detailedItemId VARCHAR(50),
    capabilityType VARCHAR(100),
    validationDate DATE,
    sectorMappingId VARCHAR(50),
    
    -- Foreign key constraints
    FOREIGN KEY (organisationId) REFERENCES Organisations(organisationId),
    FOREIGN KEY (itemId) REFERENCES Items(itemId),
    FOREIGN KEY (detailedItemId) REFERENCES DetailedItems(detailedItemId),
    FOREIGN KEY (sectorMappingId) REFERENCES Sectors(sectorMappingId)
);

-- Create indexes for better query performance
CREATE INDEX idxCapabilitiesOrganisation ON Capabilities(organisationId);
CREATE INDEX idxCapabilitiesItem ON Capabilities(itemId);
CREATE INDEX idxCapabilitiesDetailedItem ON Capabilities(detailedItemId);
CREATE INDEX idxCapabilitiesSector ON Capabilities(sectorMappingId);
CREATE INDEX idxDetailedItemsItem ON DetailedItems(itemId);
CREATE INDEX idxOrganisationsLocation ON Organisations(latitude, longitude);
CREATE INDEX idxCapabilitiesType ON Capabilities(capabilityType);
CREATE INDEX idxOrganisationsCity ON Organisations(billingCity);
CREATE INDEX idxOrganisationsState ON Organisations(billingStateProvince);
