-- seeding websites data.
INSERT INTO websites (website_name) VALUES
('asos'),
('patagonia');

INSERT INTO users (email, password) VALUES
('trainee.nabiha.mohamed@sigmalabs.co.uk', '\x24326224313224524f4c42435a52664f6955462e7979355368634678752e3763617075486a7170372e6e4f30324c523336746f6c4e414d51536d334f');

INSERT INTO products (product_code, product_name, website_id, url) VALUES
('205780494', 'ON Cloudrunner 2 running trainers in white', 1, 'https://www.asos.com/on-running/on-cloudrunner-2-running-trainers-in-white/prd/205780494#colourWayId-205780495'),
('206072336', 'Nike Running ReactX Pegasus Trail 5 trainers in navy and purple', 1, 'https://www.asos.com/nike-running/nike-running-reactx-pegasus-trail-5-trainers-in-navy-and-purple/prd/206072336#colourWayId-206072352'),
('205257581', 'Under Armour HOVR Phantom 3 SE trainers triple purple', 1, 'https://www.asos.com/under-armour/under-armour-hovr-phantom-3-se-trainers-triple-purple/prd/205257581#ctaref-we%20recommend%20carousel_2&featureref1-we%20recommend%20pers'),
('205905221', 'adidas Ultraboost Light Shoes in White', 1, 'https://www.asos.com/adidas-performance/adidas-ultraboost-light-shoes-in-white/prd/205905221#ctaref-we%20recommend%20carousel_6&featureref1-we%20recommend%20pers'),
('205779059', 'Saucony Kinvara 14 neutral running trainers in lotus', 1, 'https://www.asos.com/saucony/saucony-kinvara-14-neutral-running-trainers-in-lotus/prd/205779059#ctaref-we%20recommend%20carousel_0&featureref1-we%20recommend%20pers'),
('24197', 'W''s Airshed Pro Pullover', 2, 'https://eu.patagonia.com/gb/en/product/womens-airshed-pro-wind-pullover/24197.html?dwvar_24197_color=COHC&cgid=sport-trail-running-womens'),
('50151', 'Wool Crew Socks', 2, 'https://eu.patagonia.com/gb/en/product/wool-crew-socks/50151.html?dwvar_50151_color=FEA&cgid=sport-trail-running-womens'),
('59085', 'W''s Amber Dawn Dress', 2, 'https://eu.patagonia.com/gb/en/product/womens-amber-dawn-dress/59085.html?dwvar_59085_color=TIDB&cgid=womens-dresses-skirts');

INSERT INTO subscriptions (user_id, product_id, price_threshold) VALUES
(1, 1, 100),
(1, 2, NULL),
(1, 3, NULL),
(1, 4, NULL),
(1, 5, 100),
(1, 6, NULL),
(1, 7, NULL),
(1, 8, 80);

-- 2024-06-28

INSERT INTO price_readings (product_id, reading_at, price) VALUES
(1, '2023-08-16 18:45:59', 150),
(1, '2023-12-11 02:40:03', 140),
(1, '2024-01-08 22:22:07', 150),
(1, '2024-02-21 19:11:04', 135),
(1, '2024-03-27 05:07:06', 140),

(2, '2023-12-19 08:01:03', 140),
(2, '2024-04-02 15:10:44', 129.99),
(2, '2024-04-24 13:54:32', 134.99),
(2, '2024-05-11 20:01:11', 129.99),

(3, '2023-10-16 23:08:11', 149.99),
(3, '2023-12-12 11:43:26', 130),
(3, '2024-01-08 16:23:35', 134.99),

(4, '2023-08-01 08:18:34', 180),
(4, '2023-09-07 07:11:23', 170),
(4, '2023-11-04 11:00:53', 180),
(4, '2024-01-22 15:15:11', 159.99),
(4, '2024-03-14 14:40:02', 180),
(4, '2024-05-11 20:53:14', 179.99),
(4, '2024-06-10 06:32:45', 164.99),

(5, '2023-08-11 20:30:22', 80),
(5, '2023-11-14 21:33:43', 119.99),
(5, '2023-11-25 05:23:58', 99.99),
(5, '2024-01-03 22:25:33', 139.99),
(5, '2024-03-08 19:54:23', 109.99),
(5, '2024-04-02 16:11:11', 85),
(5, '2024-04-25 01:07:34', 110),

(6, '2023-08-11 08:03:22', 140),
(6, '2023-11-28 09:11:45', 99.99),
(6, '2024-01-18 14:19:55', 130),
(6, '2024-02-11 17:35:56', 135),

(7, '2024-05-11 03:23:54', 25),

(8, '2024-01-01 06:14:23', 64.99),
(8, '2024-02-02 11:47:11', 79.99);