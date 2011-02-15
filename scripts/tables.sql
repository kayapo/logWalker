-- create syslog database
-- Use:
--     mysql -u root -h sqldbhost -p < tables.sql
--
--

CREATE DATABASE IF NOT EXSISTS syslog DEFAULT CHARACTEr SET=utf8 DEFAULT COLLATE=utf8_general_ci;
USE syslog;

-- create table named logs
CREATE TABLE IF NOT EXISTS `logs` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `datetime` datetime DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `facility` varchar(32) DEFAULT NULL,
  `priority` varchar(32) DEFAULT NULL,
  `tag` varchar(255) DEFAULT NULL,
  `message` longtext,
  PRIMARY KEY (`id`),
  KEY `idx_datetime` (`datetime`),
  KEY `idx_host` (`host`),
  KEY `idx_level` (`facility`,`priority`),
  KEY `idx_tag` (`tag`),
  FULLTEXT KEY `idx_msg` (`message`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 DEFAULT COLLATE=utf8_general_ci CHECKSUM=1;


-- create table named hosts
CREATE TABLE IF NOT EXISTS `hosts` (
  `id` int(4) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 CHECKSUM=1;

-- create table named tags
CREATE TABLE IF NOT EXISTS `tags` (
  `id` int(4) unsigned NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_tag` (`tag`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 CHECKSUM=1;

-- Create script END ;)
