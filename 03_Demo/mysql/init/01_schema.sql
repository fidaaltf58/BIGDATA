-- ============================================================
--  Base source "PMS" de l'hôtel (Property Management System)
--  Chargée automatiquement au 1er démarrage du conteneur MySQL
-- ============================================================
USE hotel_db;

CREATE TABLE IF NOT EXISTS bookings (
  booking_id                      INT AUTO_INCREMENT PRIMARY KEY,
  hotel                           VARCHAR(20),
  is_canceled                     TINYINT,
  lead_time                       INT,
  arrival_date_year               SMALLINT,
  arrival_date_month              VARCHAR(10),
  arrival_date_week_number        TINYINT,
  arrival_date_day_of_month       TINYINT,
  stays_in_weekend_nights         TINYINT,
  stays_in_week_nights            TINYINT,
  adults                          SMALLINT,
  children                        SMALLINT NULL,
  babies                          SMALLINT,
  meal                            VARCHAR(10),
  country                         VARCHAR(5),
  market_segment                  VARCHAR(20),
  distribution_channel            VARCHAR(20),
  is_repeated_guest               TINYINT,
  previous_cancellations          SMALLINT,
  previous_bookings_not_canceled  SMALLINT,
  reserved_room_type              CHAR(1),
  assigned_room_type              CHAR(1),
  booking_changes                 SMALLINT,
  deposit_type                    VARCHAR(15),
  agent                           VARCHAR(10),
  company                         VARCHAR(10),
  days_in_waiting_list            SMALLINT,
  customer_type                   VARCHAR(20),
  adr                             DECIMAL(10,2),
  required_car_parking_spaces     TINYINT,
  total_of_special_requests       TINYINT,
  reservation_status              VARCHAR(15),
  reservation_status_date         DATE
);

LOAD DATA INFILE '/var/lib/mysql-files/hotel_bookings.csv'
INTO TABLE bookings
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(hotel, is_canceled, lead_time, arrival_date_year, arrival_date_month,
 arrival_date_week_number, arrival_date_day_of_month, stays_in_weekend_nights,
 stays_in_week_nights, adults, @children, babies, meal, country, market_segment,
 distribution_channel, is_repeated_guest, previous_cancellations,
 previous_bookings_not_canceled, reserved_room_type, assigned_room_type,
 booking_changes, deposit_type, agent, company, days_in_waiting_list,
 customer_type, adr, required_car_parking_spaces, total_of_special_requests,
 reservation_status, @status_date)
SET children = NULLIF(@children, 'NA'),
    reservation_status_date = STR_TO_DATE(TRIM(TRAILING '\r' FROM @status_date), '%Y-%m-%d');

-- Table cible de l'export Sqoop (KPI calculés dans HDFS)
CREATE TABLE IF NOT EXISTS kpi_monthly (
  hotel              VARCHAR(20),
  year_month_key     VARCHAR(7),
  total_bookings     INT,
  canceled_bookings  INT,
  cancel_rate_pct    DECIMAL(5,2),
  avg_adr            DECIMAL(10,2),
  room_nights        INT,
  revenue_realized   DECIMAL(14,2)
);

GRANT ALL PRIVILEGES ON hotel_db.* TO 'sqoop'@'%';
FLUSH PRIVILEGES;

SELECT COUNT(*) AS lignes_chargees FROM bookings;
