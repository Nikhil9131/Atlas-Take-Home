-- Project Atlas: Cognitive Market Research and Consulting
-- Production-Style MySQL Database Schema

CREATE DATABASE IF NOT EXISTS `atlas_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `atlas_db`;

-- Drop existing tables if re-initializing
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `audit_events`;
DROP TABLE IF EXISTS `escalations`;
DROP TABLE IF EXISTS `feedback`;
DROP TABLE IF EXISTS `conversation_messages`;
DROP TABLE IF EXISTS `conversations`;
DROP TABLE IF EXISTS `market_metrics`;
DROP TABLE IF EXISTS `client_report_entitlements`;
DROP TABLE IF EXISTS `clients`;
DROP TABLE IF EXISTS `reports`;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Reports Catalog
CREATE TABLE `reports` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `publisher` VARCHAR(255) NOT NULL,
    `published` DATE NOT NULL,
    `sector` VARCHAR(100) NOT NULL,
    `access` VARCHAR(50) NOT NULL DEFAULT 'paid', -- 'paid' or 'public excerpt'
    `summary` TEXT,
    `metadata_json` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_reports_sector` (`sector`),
    INDEX `idx_reports_access` (`access`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Clients Table (contains confidential contact emails, NEVER exposed to LLM)
CREATE TABLE `clients` (
    `id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `company` VARCHAR(255) NOT NULL,
    `contact_email` VARCHAR(255) NOT NULL, -- CONFIDENTIAL
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Client Report Entitlements (Access Control Boundary)
CREATE TABLE `client_report_entitlements` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `client_id` VARCHAR(50) NOT NULL,
    `report_id` VARCHAR(50) NOT NULL,
    `status` VARCHAR(50) NOT NULL DEFAULT 'active',
    `purchased_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_entitlement_client` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_entitlement_report` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uq_client_report` (`client_id`, `report_id`),
    INDEX `idx_entitlement_lookup` (`client_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Market Metrics Table (Structured verified metrics for calculation & RAG grounding)
CREATE TABLE `market_metrics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `report_id` VARCHAR(50) NOT NULL,
    `metric` VARCHAR(100) NOT NULL, -- 'Market size', 'CAGR', 'Regional share'
    `region` VARCHAR(100) NOT NULL DEFAULT 'Global',
    `year_period` VARCHAR(50) NOT NULL, -- '2024', '2025-2030'
    `value_text` VARCHAR(100) NOT NULL, -- 'USD 4.21 B', '11.2 %'
    `numeric_value` DECIMAL(15,4) NOT NULL,
    `unit` VARCHAR(50) NOT NULL, -- 'USD Billion', '%', 'Share'
    `scope_note` TEXT NOT NULL,
    `source_page` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_metrics_report` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE,
    INDEX `idx_metrics_report_region` (`report_id`, `region`, `metric`),
    INDEX `idx_metrics_year` (`year_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Conversations
CREATE TABLE `conversations` (
    `id` VARCHAR(100) NOT NULL PRIMARY KEY,
    `client_id` VARCHAR(50) NOT NULL,
    `title` VARCHAR(255) DEFAULT 'New Research Session',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_conv_client` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
    INDEX `idx_conv_client` (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Conversation Messages
CREATE TABLE `conversation_messages` (
    `id` VARCHAR(100) NOT NULL PRIMARY KEY,
    `conversation_id` VARCHAR(100) NOT NULL,
    `role` ENUM('user', 'assistant', 'system') NOT NULL,
    `content` MEDIUMTEXT NOT NULL,
    `response_metadata` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_msg_conv` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE,
    INDEX `idx_msg_conv` (`conversation_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Feedback (Thumbs up / thumbs down)
CREATE TABLE `feedback` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `message_id` VARCHAR(100) NOT NULL,
    `client_id` VARCHAR(50) NOT NULL,
    `rating` TINYINT NOT NULL, -- 1 for thumbs up, -1 for thumbs down
    `feedback_text` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_feedback_msg` FOREIGN KEY (`message_id`) REFERENCES `conversation_messages` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_feedback_client` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
    INDEX `idx_feedback_client` (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Escalations (Human analyst tickets)
CREATE TABLE `escalations` (
    `id` VARCHAR(100) NOT NULL PRIMARY KEY,
    `client_id` VARCHAR(50) NOT NULL,
    `question` TEXT NOT NULL,
    `reason` VARCHAR(255) NOT NULL,
    `confidence` FLOAT NOT NULL,
    `status` ENUM('open', 'in_progress', 'resolved', 'closed') NOT NULL DEFAULT 'open',
    `citations_json` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_escalation_client` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
    INDEX `idx_escalation_status` (`status`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Audit Events (Security logging for injections, unsafe queries, access denials)
CREATE TABLE `audit_events` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `client_id` VARCHAR(50),
    `request_id` VARCHAR(100),
    `unsafe_flag` BOOLEAN NOT NULL DEFAULT FALSE,
    `details` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_audit_event_type` (`event_type`),
    INDEX `idx_audit_client` (`client_id`),
    INDEX `idx_audit_unsafe` (`unsafe_flag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
