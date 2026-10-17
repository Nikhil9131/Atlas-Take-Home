-- Project Atlas: Seed Data
-- Cognitive Market Research and Consulting

USE `atlas_db`;

-- Insert Reports
INSERT INTO `reports` (`id`, `title`, `publisher`, `published`, `sector`, `access`, `summary`, `metadata_json`) VALUES
('R-101', 'Global Smart Water Meter Market 2025', 'CMR', '2025-03-10', 'Utilities', 'paid', 
 'Comprehensive global analysis of smart water metering solutions covering AMR/AMI hardware, analytics software, and field deployment services.', 
 '{"pages": 42, "focus": "Hardware, software, and services", "forecast_years": "2025-2030"}'),

('R-102', 'Smart Water Metering: Industry Outlook 2024', 'Aquila Insights (third party)', '2024-06-18', 'Utilities', 'public excerpt', 
 'Third-party benchmarking report dedicated strictly to residential and commercial AMR/AMI metering hardware shipments and unit economics.', 
 '{"pages": 28, "focus": "AMR/AMI hardware only", "forecast_years": "2024-2029"}'),

('R-103', 'Residential Water Purifier Market 2025', 'CMR', '2025-01-22', 'Consumer Durables', 'paid', 
 'Market assessment for household water purification technologies across point-of-use reverse osmosis, UV filtration, and multi-stage gravity filters.', 
 '{"pages": 36, "focus": "Point-of-use residential purification systems", "forecast_years": "2025-2030"}'),

('R-104', 'Commercial EV Fleet Charging Infrastructure 2025', 'CMR', '2025-02-14', 'Automotive & Energy', 'paid', 
 'Strategic outlook for commercial fleet electrification, depot megawatt charging stations, and charging management software.', 
 '{"pages": 50, "focus": "Fleet charging depots and high-power DC infrastructure", "forecast_years": "2025-2030"}'),

('R-105', 'AI-Powered Diagnostic Imaging Market 2024', 'MedTech Analytics', '2024-11-05', 'Healthcare', 'paid', 
 'Clinical AI applications in radiology, MRI, CT scanning, and automated lesion detection.', 
 '{"pages": 34, "focus": "Radiology and diagnostic computer vision software", "forecast_years": "2024-2029"}'),

('R-106', 'Cloud-Native Data Security Market 2025', 'CyberShield Research', '2025-04-02', 'Cybersecurity & Cloud', 'paid', 
 'Data security posture management (DSPM), multi-cloud tokenization, and confidential computing systems.', 
 '{"pages": 46, "focus": "Enterprise cloud data discovery and protection", "forecast_years": "2025-2030"}')
ON DUPLICATE KEY UPDATE `title`=VALUES(`title`);

-- Insert Clients (Confidential emails must never be leaked to LLM or public responses)
INSERT INTO `clients` (`id`, `company`, `contact_email`) VALUES
('C-01', 'Northwind Utilities', 'ops@example.com'),
('C-02', 'Blue Delta Infra', 'procurement@example.com')
ON DUPLICATE KEY UPDATE `company`=VALUES(`company`);

-- Insert Client Report Entitlements (Entitlement Boundary)
-- C-01 purchased R-101 and R-103
-- C-02 purchased R-103 ONLY (strictly unauthorized for R-101)
INSERT INTO `client_report_entitlements` (`client_id`, `report_id`, `status`) VALUES
('C-01', 'R-101', 'active'),
('C-01', 'R-103', 'active'),
('C-02', 'R-103', 'active')
ON DUPLICATE KEY UPDATE `status`=VALUES(`status`);

-- Insert Market Metrics
INSERT INTO `market_metrics` (`report_id`, `metric`, `region`, `year_period`, `value_text`, `numeric_value`, `unit`, `scope_note`, `source_page`) VALUES
-- R-101 Exact Seed Metrics
('R-101', 'Market size', 'Global', '2024', 'USD 4.21 B', 4.2100, 'USD Billion', 'Includes hardware, software and services', 8),
('R-101', 'CAGR', 'Global', '2025-2030', '11.2 %', 11.2000, '%', 'Forecast period stated as 2025-2030', 8),
('R-101', 'Regional share', 'APAC', '2024', '38 %', 38.0000, '%', 'Share of global market size', 8),

-- R-102 Exact Seed Metrics
('R-102', 'Market size', 'Global', '2024', 'USD 3.87 B', 3.8700, 'USD Billion', 'AMR / AMI hardware only', 14),
('R-102', 'CAGR', 'Global', '2024-2029', '9.8 %', 9.8000, '%', 'Different forecast window from R-101', 14),
('R-102', 'Regional share', 'APAC', '2024', '41 %', 41.0000, '%', 'Share of hardware market', 14),

-- R-103 Metrics
('R-103', 'Market size', 'Global', '2024', 'USD 9.55 B', 9.5500, 'USD Billion', 'Includes RO, UV, and Gravity residential purifiers', 6),
('R-103', 'CAGR', 'Global', '2025-2030', '7.8 %', 7.8000, '%', 'Forecast period 2025-2030', 6),
('R-103', 'Regional share', 'APAC', '2024', '52 %', 52.0000, '%', 'Share of global water purifier market', 7),

-- R-104 Metrics
('R-104', 'Market size', 'Global', '2024', 'USD 5.10 B', 5.1000, 'USD Billion', 'Commercial fleet charging stations and depot software', 10),
('R-104', 'CAGR', 'Global', '2025-2030', '18.5 %', 18.5000, '%', 'Commercial fleet electrification forecast 2025-2030', 10),

-- R-105 Metrics
('R-105', 'Market size', 'Global', '2024', 'USD 2.45 B', 2.4500, 'USD Billion', 'Radiology AI, automated detection, and oncology imaging', 12),
('R-105', 'CAGR', 'Global', '2024-2029', '24.1 %', 24.1000, '%', 'Clinical adoption window 2024-2029', 12),

-- R-106 Metrics
('R-106', 'Market size', 'Global', '2024', 'USD 3.60 B', 3.6000, 'USD Billion', 'DSPM, cloud data discovery, tokenization, and encryption', 9),
('R-106', 'CAGR', 'Global', '2025-2030', '16.2 %', 16.2000, '%', 'Enterprise cloud security forecast 2025-2030', 9);
