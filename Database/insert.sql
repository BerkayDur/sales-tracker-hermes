-- seeding websites data.
INSERT INTO websites (website_name) VALUES
('asos'),
('steam');

INSERT INTO users (email) VALUES
('trainee.berkay.dur@sigmalabs.co.uk');

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
(1, 7, 85);