PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT UNIQUE,
                item_description TEXT NOT NULL,
                vendor_name TEXT,
                current_price REAL,
                last_purchased_price REAL,
                last_purchased_date TEXT,
                unit_measure TEXT,
                purchase_unit TEXT,
                recipe_cost_unit TEXT,
                pack_size TEXT,
                yield_percent REAL DEFAULT 100,
                product_categories TEXT,
                close_watch BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , density_g_per_ml DECIMAL(10,4), count_to_weight_g DECIMAL(10,2));
INSERT INTO inventory VALUES(5,'237552','Protein, Catfish, Fillet, Fresh','Buckhead Meat & Seafood OF HOUSTON',6.429999999999999716,6.429999999999999716,'3/13/2025','lb','lb','','1 lb',100.0,'Protein, Catfish, Fillet, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929220',NULL,NULL);
INSERT INTO inventory VALUES(8,'58897_XC9776450','Dairy, Egg','Jorge Garza',71.0,71.0,'3/24/2025','case','case','','180 each',100.0,'Dairy, Egg',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929248',NULL,NULL);
INSERT INTO inventory VALUES(9,'58897_XC10484627','N/A Bev, Soda, Fresca, Mexican','Jorge Garza',41.89000000000000056,41.89000000000000056,'1/27/2025','cs','case','each','24 x 16 oz',100.0,'N/A Bev, Soda, Fresca, Mexican',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929255',NULL,NULL);
INSERT INTO inventory VALUES(10,'58897_XC11725426','N/A Bev, Soda, Fresca, Mexican','Jorge Garza',43.5,43.5,'3/24/2025','cs','case','each','24 x 16 oz',100.0,'N/A Bev, Soda, Fresca, Mexican',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929262',NULL,NULL);
INSERT INTO inventory VALUES(11,'58897_XC11546426','Produce, Kale, Green, Fresh, by Count','Jorge Garza',26.5,26.5,'2/25/2025','cs','case','each','24 each',100.0,'Produce, Kale, Green, Fresh, by Count',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929268',NULL,NULL);
INSERT INTO inventory VALUES(12,'58897_XC11546428','Dry Goods, Oil, Canola, Clear, Frying','Jorge Garza',40.5,40.5,'2/25/2025','ea','ea','','35 lb',100.0,'Dry Goods, Oil, Canola, Clear, Frying',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929275',NULL,NULL);
INSERT INTO inventory VALUES(14,'1001997','Protein, Chicken, Wing','Buckhead Meat & Seafood OF HOUSTON',1.739999999999999992,1.739999999999999992,'7/1/2025','lb','lb','','1 lb',100.0,'Protein, Chicken, Wing',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929287',NULL,NULL);
INSERT INTO inventory VALUES(24,'58897_XC11546427','Produce, Onions, Green, wt','Jorge Garza',25.75,25.75,'2/25/2025','ct','each','each','48 x 4 oz',100.0,'Produce, Onions, Green, wt',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929879',NULL,NULL);
INSERT INTO inventory VALUES(25,'58897_XC5723334','Produce, Carrots, Jumbo, Fresh','Jorge Garza',23.5,23.5,'2/18/2025','case','case','','50 pound',100.0,'Produce, Carrots, Jumbo, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929886',NULL,NULL);
INSERT INTO inventory VALUES(29,'58897_XC11131128','Dry Goods, Flour, All Purpose, White','Jorge Garza',11.78999999999999915,11.78999999999999915,'1/6/2025','cs','case','','5 lb',100.0,'Dry Goods, Flour, All Purpose, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.929917',NULL,NULL);
INSERT INTO inventory VALUES(39,'7228367','Frozen, Corn Rib, Hickory Smoked','Sysco Houston',71.06999999999999317,71.06999999999999317,'5/23/2025','cs','case','pack','4 x 4 lb',100.0,'Frozen, Corn Rib, Hickory Smoked',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.930003',NULL,NULL);
INSERT INTO inventory VALUES(47,'70247159793','BAC TRAY PACK 3#','RESTAURANT DEPOT',13.40000000000000035,13.40000000000000035,'5/13/2025','cs','case','','3 lb',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.930572',NULL,NULL);
INSERT INTO inventory VALUES(48,'18692','BAC TRAY PACK 3# FLAND','RESTAURANT DEPOT',12.17999999999999972,12.17999999999999972,'4/22/2025','cs','case','','3 lb',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.930578',NULL,NULL);
INSERT INTO inventory VALUES(60,'101841_XC7523071','Dessert, Banana Pudding','MJ Sweet and Cake',20.0,20.0,'6/24/2025','cs','case','','1 each',100.0,'Dessert, Banana Pudding',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.931167',NULL,NULL);
INSERT INTO inventory VALUES(71,'58897_XC5705377','Produce, Beetroot,  Red, Fresh','Jorge Garza',1.489999999999999992,1.489999999999999992,'3/24/2025','lb','lb','','1 lb',100.0,'Produce, Beetroot,  Red, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.931238',NULL,NULL);
INSERT INTO inventory VALUES(84,'101841_XC10776471','Dessert, Blueberry Bundt Cake','MJ Sweet and Cake',32.0,32.0,'6/24/2025','ea','ea','','8 each',100.0,'Dessert, Blueberry Bundt Cake',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932350',NULL,NULL);
INSERT INTO inventory VALUES(86,'486','Dry Goods, Bread,  Burger Bun, 2.5 oz','CB Commissary LLC',0.5699999999999999512,0.5699999999999999512,'6/3/2025','cs','case','','1 each',100.0,'Dry Goods, Bread,  Burger Bun, 2.5 oz',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932362',NULL,NULL);
INSERT INTO inventory VALUES(87,'90880_XC12350157','Dry Goods, Bread,  Burger Bun','COMMON BOND BISTRO & BAKERY',0.6199999999999999956,0.6199999999999999956,'5/15/2025','cs','case','','1 each',100.0,'Dry Goods, Bread,  Burger Bun',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932368',NULL,NULL);
INSERT INTO inventory VALUES(88,'483','Dry Goods, Bread,  Burger Bun, 2 oz','CB Commissary LLC',1.590000000000000079,1.590000000000000079,'6/3/2025','cs','case','each','12 x 2 oz',100.0,'Dry Goods, Bread,  Burger Bun, 2 oz',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932375',NULL,NULL);
INSERT INTO inventory VALUES(89,'487','Dry Goods, Bread,  Burger Bun','CB Commissary LLC',0.6199999999999999956,0.6199999999999999956,'7/1/2025','ea','ea','','1 each',100.0,'Dry Goods, Bread,  Burger Bun',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932381',NULL,NULL);
INSERT INTO inventory VALUES(90,'936','Dry Goods, Bread, Texas Toast','CB Commissary LLC',2.189999999999999947,2.189999999999999947,'7/1/2025','loaf','each','each','10 x 1 each',100.0,'Dry Goods, Bread, Texas Toast',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932387',NULL,NULL);
INSERT INTO inventory VALUES(91,'90880_XC12350158','Dry Goods, Bread, Texas Toast','COMMON BOND BISTRO & BAKERY',2.189999999999999947,2.189999999999999947,'5/15/2025','cs','case','','1 each',100.0,'Dry Goods, Bread, Texas Toast',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932393',NULL,NULL);
INSERT INTO inventory VALUES(92,'2537','Dry Goods, Bread, French Toast, Thick Slice','CB Commissary LLC',1.060000000000000053,1.060000000000000053,'6/3/2025','each','each','','1 each',100.0,'Dry Goods, Bread, French Toast, Thick Slice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932399',NULL,NULL);
INSERT INTO inventory VALUES(93,'2537T','Dry Goods, Bread, French Toast, Thin Slice','CB Commissary LLC',1.060000000000000053,1.060000000000000053,'5/20/2025','ea','ea','','1 each',100.0,'Dry Goods, Bread, French Toast, Thin Slice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.932897',NULL,NULL);
INSERT INTO inventory VALUES(102,'900006','Frozen, Bread, Texas Toast, White,','JAKE''S, INC.',34.1700000000000017,34.1700000000000017,'5/1/2025','cs','case','each','8 x 24 oz',100.0,'Frozen, Bread, Texas Toast, White,',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.933567',NULL,NULL);
INSERT INTO inventory VALUES(105,'15700227220','Dairy,  Clarified Butter','RESTAURANT DEPOT',24.51000000000000156,24.51000000000000156,'5/13/2025','cs','case','each','4 x 5 lb',100.0,'Dairy,  Clarified Butter',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.933585',NULL,NULL);
INSERT INTO inventory VALUES(112,'BUTR28','Dairy,  Clarified Butter','JAKES, INC.',102.9500000000000028,102.9500000000000028,'6/9/2025','case','case','each','4 x 5 lb',100.0,'Dairy,  Clarified Butter',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.933664',NULL,NULL);
INSERT INTO inventory VALUES(131,'58897_XC35013','Produce, Carrots, Jumbo, Fresh','Jorge Garza',0.7900000000000000355,0.7900000000000000355,'2/25/2025','lb','lb','','1 lb',100.0,'Produce, Carrots, Jumbo, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.934829',NULL,NULL);
INSERT INTO inventory VALUES(138,'58897_XC10619296','Dairy, Cheese Sauce, Loaf, American','Jorge Garza',144.0,144.0,'1/7/2025','case','case','lb','6 x 5 lb',100.0,'Dairy, Cheese Sauce, Loaf, American',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.934872',NULL,NULL);
INSERT INTO inventory VALUES(140,'58897_XC10619293','N/A Bev, Soda, Sprite','Jorge Garza',41.5,41.5,'2/25/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Soda, Sprite',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.934885',NULL,NULL);
INSERT INTO inventory VALUES(141,'58897_XC11813053','N/A Bev, Soda, Sprite','Jorge Garza',41.5,41.5,'3/24/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Soda, Sprite',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935380',NULL,NULL);
INSERT INTO inventory VALUES(142,'58897_XC11484060','N/A Bev, Soda, Sprite','Jorge Garza',41.5,41.5,'3/10/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Soda, Sprite',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935395',NULL,NULL);
INSERT INTO inventory VALUES(143,'58897_XC10484628','Case ===== Topo Chico 24ct|355ml','Jorge Garza',32.5,32.5,'2/25/2025','cs','case','','1 each',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935402',NULL,NULL);
INSERT INTO inventory VALUES(145,'7237552','Protein, Catfish, Fillet, Fresh','Buckhead Meat & Seafood OF HOUSTON',6.429999999999999716,6.429999999999999716,'7/1/2025','lb','lb','each','1 lb',100.0,'Protein, Catfish, Fillet, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935416',NULL,NULL);
INSERT INTO inventory VALUES(146,'58897_XC3682926','Produce, Cauliflower, Fresh','Jorge Garza',28.75,28.75,'2/18/2025','case','case','each','18 x 1 lb',100.0,'Produce, Cauliflower, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935422',NULL,NULL);
INSERT INTO inventory VALUES(147,'58897_XC6873465','Dry Good,  Cayenne Pepper, Spice','Jorge Garza',4.240000000000000213,4.240000000000000213,'2/11/2025','case','case','','1 lb',100.0,'Dry Good,  Cayenne Pepper, Spice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935428',NULL,NULL);
INSERT INTO inventory VALUES(148,'58897_XC11813060','Dry Good,  Cayenne Pepper, Spice','Jorge Garza',4.240000000000000213,4.240000000000000213,'3/24/2025','cs','case','','1 lb',100.0,'Dry Good,  Cayenne Pepper, Spice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935434',NULL,NULL);
INSERT INTO inventory VALUES(149,'58897_XC63226','Produce, Celery Stalks, Fresh','Jorge Garza',1.790000000000000035,1.790000000000000035,'2/18/2025','cs','case','','1 each',100.0,'Produce, Celery Stalks, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935440',NULL,NULL);
INSERT INTO inventory VALUES(153,'PR8153','Produce, Celery Stalks, Fresh','JAKE''S, INC.',10.00999999999999979,10.00999999999999979,'6/2/2025','cs','case','','6 each',100.0,'Produce, Celery Stalks, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935465',NULL,NULL);
INSERT INTO inventory VALUES(157,'PCH007','Dairy, Cheese, Cheddar, Yellow Bar','JAKES, INC.',3.310000000000000053,3.310000000000000053,'6/9/2025','lb','lb','','1 lb',100.0,'Dairy, Cheese, Cheddar, Yellow Bar',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935488',NULL,NULL);
INSERT INTO inventory VALUES(163,'NCHS64','Dairy, Cheese, Cheddar, Yellow Bar','JAKES, INC.',4.150000000000000356,4.150000000000000356,'5/20/2025','lb','lb','','1 lb',100.0,'Dairy, Cheese, Cheddar, Yellow Bar',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935523',NULL,NULL);
INSERT INTO inventory VALUES(165,'NCHS45','Dairy, Cheese, Monterray Jack','US Foods',3.470000000000000195,3.470000000000000195,'6/30/2025','lb','lb','','1 lb',100.0,'Dairy, Cheese, Monterray Jack',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.935535',NULL,NULL);
INSERT INTO inventory VALUES(171,'JACK50','Dairy, Cheese, Loaf, Pepper Jack','US Foods',4.450000000000000177,4.450000000000000177,'6/30/2025','lb','lb','','1 lb',100.0,'Dairy, Cheese, Monterray Jack',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936056',NULL,NULL);
INSERT INTO inventory VALUES(175,'58897_XC11270013','Dry Goods, Chicken Base, Paste','Jorge Garza',18.94999999999999929,18.94999999999999929,'1/23/2025','ea','ea','','4.4 lb',100.0,'Dry Goods, Chicken Base, Paste',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936081',NULL,NULL);
INSERT INTO inventory VALUES(178,'1002010','Protein, Chicken, Tenders','Buckhead Meat & Seafood OF HOUSTON',2.859999999999999876,2.859999999999999876,'7/1/2025','lb','lb','','1 lb',100.0,'Protein, Chicken, Tenders',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936098',NULL,NULL);
INSERT INTO inventory VALUES(179,'1005246','Protein, Chicken, Tenders','Buckhead Meat & Seafood OF HOUSTON',4.009999999999999787,4.009999999999999787,'7/1/2025','lb','lb','','1 lb',100.0,'Protein, Chicken, Tenders',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936104',NULL,NULL);
INSERT INTO inventory VALUES(183,'G20223','Protein, Chicken, Thighs','US Foods',3.759999999999999787,3.759999999999999787,'6/27/2025','lb','lb','','1 lb',100.0,'Protein, Chicken, Thighs',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936133',NULL,NULL);
INSERT INTO inventory VALUES(186,'CHIC22','Protein, Chicken, Wing','JAKE''S, INC.',1.989999999999999992,1.989999999999999992,'4/11/2025','lb','lb','','1 lb',100.0,'Protein, Chicken, Wing',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936150',NULL,NULL);
INSERT INTO inventory VALUES(192,'34500487757','Dairy, Cheese, Cheddar, Yellow Bar','RESTAURANT DEPOT',110.0699999999999931,110.0699999999999931,'4/29/2025','cs','case','each','6 x 5 lb',100.0,'Dairy, Cheese, Cheddar, Yellow Bar',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936714',NULL,NULL);
INSERT INTO inventory VALUES(194,'71505015875','Dairy, Cheese, Cheddar, Yellow Bar','RESTAURANT DEPOT',17.76000000000000157,17.76000000000000157,'4/29/2025','cs','case','','5 lb',100.0,'Dairy, Cheese, Cheddar, Yellow Bar',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936736',NULL,NULL);
INSERT INTO inventory VALUES(195,'44310','Dairy, Cheese Sauce, Loaf, American','RESTAURANT DEPOT',18.78000000000000113,18.78000000000000113,'4/22/2025','cs','case','','5 lb',100.0,'Dairy, Cheese Sauce, Loaf, American',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936742',NULL,NULL);
INSERT INTO inventory VALUES(197,'14726','Dairy, Chesse, Parmesan, Grated','RESTAURANT DEPOT',31.55999999999999873,31.55999999999999873,'5/28/2025','case','case','each','4 x 5 lb',100.0,'Dairy, Chesse, Parmesan, Grated',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936755',NULL,NULL);
INSERT INTO inventory VALUES(208,'165826_XC12097639','N/A Bev, Coca Cola, Mexican, Bottle','ALVARADO''S',37.0,37.0,'4/22/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Coca Cola, Mexican, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936831',NULL,NULL);
INSERT INTO inventory VALUES(209,'165826_XC12097641','N/A Bev, Coca Cola, Mexican, Bottle','ALVARADO''S',30.0,30.0,'4/22/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Coca Cola, Mexican, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.936838',NULL,NULL);
INSERT INTO inventory VALUES(213,'58897_XC10447740','N/A Bev, DRINK SODA COLA COKE MEX GLS','Jorge Garza',39.75,39.75,'3/15/2025','cs','case','each','24 x 500 ml',100.0,'N/A Bev, DRINK SODA COLA COKE MEX GLS',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.937401',NULL,NULL);
INSERT INTO inventory VALUES(214,'49000047790','N/A Bev, DRINK SODA COLA COKE MEX GLS','RESTAURANT DEPOT',41.10999999999999944,41.10999999999999944,'4/2/2025','cs','case','each','24 x 500 ml',100.0,'N/A Bev, DRINK SODA COLA COKE MEX GLS',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.937415',NULL,NULL);
INSERT INTO inventory VALUES(215,'49000046595','N/A Bev, Coca Cola, Mexican, Bottle','RESTAURANT DEPOT',41.10999999999999944,41.10999999999999944,'4/15/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Coca Cola, Mexican, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.937423',NULL,NULL);
INSERT INTO inventory VALUES(219,'PR9313','Produce, Coleslaw Mix','JAKES, INC.',20.25,20.25,'5/20/2025','cs','case','each','4 x 5 lb',100.0,'Produce, Coleslaw Mix',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.937447',NULL,NULL);
INSERT INTO inventory VALUES(259,'MILK33','Dairy, Cream, Heavy','JAKE''S, INC.',64.98000000000000397,64.98000000000000397,'6/2/2025','cs','case','each','12 x 1 qt',100.0,'Dairy, Cream, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.938218',NULL,NULL);
INSERT INTO inventory VALUES(261,'10031','Dairy, Cream, Heavy','RESTAURANT DEPOT',50.4200000000000017,50.4200000000000017,'4/22/2025','case','case','','1 qt',100.0,'Dairy, Cream, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.938229',NULL,NULL);
INSERT INTO inventory VALUES(262,'41467000738','Dairy, Cream, Heavy','RESTAURANT DEPOT',49.5,49.5,'5/13/2025','case','case','each','12 x 1 quart',100.0,'Dairy, Cream, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.938235',NULL,NULL);
INSERT INTO inventory VALUES(263,'2061156','Dry Goods, Croutons, Homestyle','RESTAURANT DEPOT',26.51000000000000156,26.51000000000000156,'5/28/2025','cs','case','each','4 x 2.5 lb',100.0,'Dry Goods, Croutons, Homestyle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.938241',NULL,NULL);
INSERT INTO inventory VALUES(284,'58897_XC9163168','Produce, Daikon Radish, Fresh','Jorge Garza',1.489999999999999992,1.489999999999999992,'2/18/2025','lb','lb','','1 lb',100.0,'Produce, Daikon Radish, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.939431',NULL,NULL);
INSERT INTO inventory VALUES(285,'54565','Dry Goods, Caesar Dressing','RESTAURANT DEPOT',30.21999999999999887,30.21999999999999887,'5/28/2025','case','case','each','4 x 128 ounce',100.0,'Dry Goods, Caesar Dressing',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.939437',NULL,NULL);
INSERT INTO inventory VALUES(286,'41335351986','Dry Goods, Ranch Dressing, with Jalapeno','RESTAURANT DEPOT',18.05000000000000071,18.05000000000000071,'5/20/2025','cs','case','','1 gal',100.0,'Dry Goods, Ranch Dressing, with Jalapeno',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.939443',NULL,NULL);
INSERT INTO inventory VALUES(291,'333615','Dry Goods, Dressing, Honey Mustard','US Foods',26.94999999999999929,26.94999999999999929,'6/30/2025','ea','ea','','1 gal',100.0,'Dry Goods, Dressing, Honey Mustard',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.939472',NULL,NULL);
INSERT INTO inventory VALUES(293,'41335086710','Dry Goods, Sauce, Tartar','RESTAURANT DEPOT',16.46000000000000085,16.46000000000000085,'5/20/2025','jug','each','','1 gal',100.0,'Dry Goods, Sauce, Tartar',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940004',NULL,NULL);
INSERT INTO inventory VALUES(297,'CDK145','N/A Bev,  Soda, Jarritos, Grapefruit','JAKES, INC.',33.35999999999999944,33.35999999999999944,'5/23/2025','ea','ea','each','24 x 12.5 oz',100.0,'N/A Bev,  Soda, Jarritos, Grapefruit',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940039',NULL,NULL);
INSERT INTO inventory VALUES(299,'CDK149','N/A Bev,. Soda, Sidral','JAKES, INC.',33.35999999999999944,33.35999999999999944,'3/11/2025','case','case','each','24 x 12 oz',100.0,'N/A Bev,. Soda, Sidral',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940051',NULL,NULL);
INSERT INTO inventory VALUES(308,'CDK148','N/A Bev, Soda, Jarritos, Strawberry','JAKE''S, INC.',33.35999999999999944,33.35999999999999944,'5/26/2025','cs','case','each','24 x 12.5 oz',100.0,'N/A Bev, Soda, Jarritos, Strawberry',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940104',NULL,NULL);
INSERT INTO inventory VALUES(311,'CDK146','N/A Bev, Soda, Jarritos, Tamarind','US Foods',33.97999999999999687,33.97999999999999687,'6/30/2025','cs','case','each','24 x 12.5 oz',100.0,'N/A Bev, Soda, Jarritos, Tamarind',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940122',NULL,NULL);
INSERT INTO inventory VALUES(313,'78000082401','N/A Bev, Soda, Dr Pepper, Bottle','RESTAURANT DEPOT',29.01999999999999958,29.01999999999999958,'4/2/2025','ea','ea','each','24 x 1 each',100.0,'N/A Bev, Soda, Dr Pepper, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940133',NULL,NULL);
INSERT INTO inventory VALUES(314,'78000804676','N/A Bev, Soda, Dr Pepper, Bottle','RESTAURANT DEPOT',14.58000000000000007,14.58000000000000007,'4/29/2025','ea','ea','each','12 x 1 each',100.0,'N/A Bev, Soda, Dr Pepper, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940139',NULL,NULL);
INSERT INTO inventory VALUES(315,'440808','N/A Bev, Soda, Dr Pepper, Bottle','RESTAURANT DEPOT',13.42999999999999972,13.42999999999999972,'4/17/2025','pack','pack','each','24 x 1 each',100.0,'N/A Bev, Soda, Dr Pepper, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940145',NULL,NULL);
INSERT INTO inventory VALUES(316,'BRD040','Frozen, Bread, Texas Toast, White,','JAKE''S, INC.',23.92999999999999972,23.92999999999999972,'4/11/2025','cs','case','each','7 x 32 oz',100.0,'Frozen, Bread, Texas Toast, White,',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940151',NULL,NULL);
INSERT INTO inventory VALUES(317,'40900016084','Dairy, Cream, Heavy','RESTAURANT DEPOT',65.12999999999999546,65.12999999999999546,'4/1/2025','carton','carton','each','12 x 32 ml',100.0,'Dairy, Cream, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940157',NULL,NULL);
INSERT INTO inventory VALUES(318,'58897_XC11494749','Produce, Parsley, Italian, Fresh','Jorge Garza',0.6899999999999999467,0.6899999999999999467,'2/25/2025','each','each','','1 each',100.0,'Produce, Parsley, Italian, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940163',NULL,NULL);
INSERT INTO inventory VALUES(324,'51213','Dairy, Egg','RESTAURANT DEPOT',41.95000000000000285,41.95000000000000285,'4/22/2025','case','case','','180 each',100.0,'Dairy, Egg',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940198',NULL,NULL);
INSERT INTO inventory VALUES(331,'EGGS08','Dairy, Egg','JAKES, INC.',3.939999999999999947,3.939999999999999947,'6/4/2025','lb','lb','','15 each',100.0,'Dairy, Egg',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940239',NULL,NULL);
INSERT INTO inventory VALUES(335,'EGGS07','Dairy, Egg','US Foods',3.899999999999999912,3.899999999999999912,'6/30/2025','lb','lb','each','12 x 1 each',100.0,'Dairy, Egg',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940261',NULL,NULL);
INSERT INTO inventory VALUES(341,'58897_XC10111214','Extra Melt | White','Jorge Garza',144.0,144.0,'1/6/2025','cs','case','lb','6 x 5 lb',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940296',NULL,NULL);
INSERT INTO inventory VALUES(342,'58897_XC10447737','Extra Melt | Yellow','Jorge Garza',144.0,144.0,'3/10/2025','cs','case','','1 each',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940301',NULL,NULL);
INSERT INTO inventory VALUES(345,'165826_XC12097645','N/A Bev, Soda, Fresa, Fanta','ALVARADO''S',36.0,36.0,'4/22/2025','cs','case','each','24 x 16 oz',100.0,'N/A Bev, Soda, Fresa, Fanta',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940826',NULL,NULL);
INSERT INTO inventory VALUES(346,'165826_XC12097643','N/A Bev, Soda, Fanta, Orange, Mexican','ALVARADO''S',35.0,35.0,'4/22/2025','cs','case','each','24 x 16 ml',100.0,'N/A Bev, Soda, Fanta, Orange, Mexican',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940834',NULL,NULL);
INSERT INTO inventory VALUES(347,'58897_XC10172096','N/A Bev, SODA ORANGE MEXICAN GLASS','Jorge Garza',39.75,39.75,'2/11/2025','cs','case','each','24 x 500 ml',100.0,'N/A Bev, SODA ORANGE MEXICAN GLASS',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940841',NULL,NULL);
INSERT INTO inventory VALUES(353,'FISH14','Protein, Catfish, Fillet, Fresh','JAKES, INC.',5.910000000000000142,5.910000000000000142,'3/18/2025','lb','lb','','1 lb',100.0,'Protein, Catfish, Fillet, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940878',NULL,NULL);
INSERT INTO inventory VALUES(354,'FIS035','Seafood, Cod, Loin','JAKES, INC.',7.0,7.0,'5/20/2025','cs','case','','10 lb',100.0,'Seafood, Cod, Loin',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940884',NULL,NULL);
INSERT INTO inventory VALUES(355,'VFSH52','Seafood, Haddock, Yuengling Beer Coated','JAKE''S, INC.',9.23000000000000042,9.23000000000000042,'3/28/2025','lb','lb','','10 lb',100.0,'Seafood, Haddock, Yuengling Beer Coated',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940890',NULL,NULL);
INSERT INTO inventory VALUES(360,'FLOR32','FLOUR HAND R ALL PURPOSE','JAKES, INC.',17.98000000000000042,17.98000000000000042,'1/13/2025','bag','bag','','25 lb',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940919',NULL,NULL);
INSERT INTO inventory VALUES(361,'FLOR33','Dry Goods, Flour, All Purpose, White','US Foods',10.33000000000000007,10.33000000000000007,'6/30/2025','each','each','','25 lb',100.0,'Dry Goods, Flour, All Purpose, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940925',NULL,NULL);
INSERT INTO inventory VALUES(366,'58897_XC11270014','N/A Bev, Soda, Fresca, Mexican','Jorge Garza',43.5,43.5,'3/10/2025','cs','case','each','24 x 16 oz',100.0,'N/A Bev, Soda, Fresca, Mexican',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.940954',NULL,NULL);
INSERT INTO inventory VALUES(371,'FRY057','Frozen, Potato, French Fries, Frozen','US Foods',35.75,35.75,'7/2/2025','cs','case','each','6 x 4.5 lb',100.0,'Frozen, Potato, French Fries, Frozen',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.941505',NULL,NULL);
INSERT INTO inventory VALUES(373,'73538020154','Seafood, Cod, Battered, Wedges, Frozen','RESTAURANT DEPOT',39.5799999999999983,39.5799999999999983,'5/20/2025','cs','case','each','32 x 2 oz',100.0,'Seafood, Cod, Battered, Wedges, Frozen',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.942438',NULL,NULL);
INSERT INTO inventory VALUES(376,'58897_XC11090807','Produce, Lemon Juice','Jorge Garza',7.490000000000000213,7.490000000000000213,'1/13/2025','cs','case','','0.5 gal',100.0,'Produce, Lemon Juice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.942468',NULL,NULL);
INSERT INTO inventory VALUES(378,'58897_XC11281491','Dry Goods, Honey, Natural, by Volume','Jorge Garza',39.75,39.75,'1/24/2025','ea','ea','','1 gal',100.0,'Dry Goods, Honey, Natural, by Volume',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.942480',NULL,NULL);
INSERT INTO inventory VALUES(381,'58897_XC11189472','Dry Goods, Spice, Ghost Pepper','Jorge Garza',29.94999999999999929,29.94999999999999929,'1/13/2025','each','each','','8 oz',100.0,'Dry Goods, Spice, Ghost Pepper',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.942499',NULL,NULL);
INSERT INTO inventory VALUES(414,'58897_XC10943904','Produce, Kale, Green, Fresh, by Count','Jorge Garza',28.5,28.5,'1/27/2025','cs','case','','24 each',100.0,'Produce, Kale, Green, Fresh, by Count',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943212',NULL,NULL);
INSERT INTO inventory VALUES(415,'58897_XC28467','Produce, Onions, Green','Jorge Garza',0.7900000000000000355,0.7900000000000000355,'3/10/2025','ea','ea','','1 each',100.0,'Produce, Onions, Green',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943218',NULL,NULL);
INSERT INTO inventory VALUES(416,'58897_XC10566294','Produce, Onions, Green','Jorge Garza',0.6899999999999999467,0.6899999999999999467,'1/27/2025','ea','ea','','1 each',100.0,'Produce, Onions, Green',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943223',NULL,NULL);
INSERT INTO inventory VALUES(417,'58897_XC37782','Green Onion/Iceless','Jorge Garza',24.75,24.75,'3/24/2025','case','case','','1 each',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943229',NULL,NULL);
INSERT INTO inventory VALUES(419,'FVEG13','Produce, Collard Green, Frozen, Chopped','JAKES, INC.',48.22999999999999688,48.22999999999999688,'2/4/2025','ea','ea','each','12 x 3 lb',100.0,'Produce, Collard Green, Frozen, Chopped',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943241',NULL,NULL);
INSERT INTO inventory VALUES(428,'58897_XC10172100','Dairy, Cream, Heavy','Jorge Garza',5.429999999999999716,5.429999999999999716,'2/25/2025','qt','qt','','1 gal',100.0,'Dairy, Cream, Heavy',1,'2025-07-04 21:29:47','2025-07-04T16:46:01.943799',NULL,NULL);
INSERT INTO inventory VALUES(433,'SYRP67','Dry Goods, Honey, Natural','US Foods',18.76999999999999958,18.76999999999999958,'6/23/2025','cs','case','each','6 x 5 lb',100.0,'Dry Goods, Honey, Natural',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943829',NULL,NULL);
INSERT INTO inventory VALUES(434,'71100210057','Dry Goods, Blue Cheese, Dry Mix','RESTAURANT DEPOT',58.35000000000000142,58.35000000000000142,'4/1/2025','ea','ea','each','18 x 3 oz',100.0,'Dry Goods, Blue Cheese, Dry Mix',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943835',NULL,NULL);
INSERT INTO inventory VALUES(436,'7.42434E+11','Dry Goods, Jalapenos, Sliced','RESTAURANT DEPOT',7.540000000000000035,7.540000000000000035,'3/28/2025','ea',NULL,NULL,'1 x 10',100.0,'Dry Goods, Jalapenos, Sliced',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943847',NULL,NULL);
INSERT INTO inventory VALUES(437,'58897_XC11725424','N/A Bev, Soda, Jarritos, Strawberry','Jorge Garza',31.5,31.5,'3/24/2025','cs','case','each','24 x 12 oz',100.0,'N/A Bev, Soda, Jarritos, Strawberry',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943853',NULL,NULL);
INSERT INTO inventory VALUES(439,'90478410050','N/A Bev, Soda, Jarritos, Lime','RESTAURANT DEPOT',23.26999999999999958,23.26999999999999958,'4/2/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Soda, Jarritos, Lime',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943865',NULL,NULL);
INSERT INTO inventory VALUES(440,'90478410012','N/A Bev, Soda, Mandarin, Jarritos','RESTAURANT DEPOT',23.58999999999999986,23.58999999999999986,'4/2/2025','case','case','each','24 x 12.5 oz',100.0,'N/A Bev, Soda, Mandarin, Jarritos',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943871',NULL,NULL);
INSERT INTO inventory VALUES(441,'19514','N/A Bev, Soda, Mandarin, Jarritos','RESTAURANT DEPOT',23.58999999999999986,23.58999999999999986,'4/17/2025','cs','case','each','24 x 12.5 oz',100.0,'N/A Bev, Soda, Mandarin, Jarritos',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943877',NULL,NULL);
INSERT INTO inventory VALUES(442,'90478410098','N/A Bev, Soda, Jarritos, Strawberry','RESTAURANT DEPOT',23.26999999999999958,23.26999999999999958,'4/2/2025','each','each','each','24 x 12.5 oz',100.0,'N/A Bev, Soda, Jarritos, Strawberry',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943883',NULL,NULL);
INSERT INTO inventory VALUES(443,'20260','N/A Bev, Soda, Jarritos, Strawberry','RESTAURANT DEPOT',23.26999999999999958,23.26999999999999958,'4/17/2025','cs','case','each','24 x 12.5 oz',100.0,'N/A Bev, Soda, Jarritos, Strawberry',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943889',NULL,NULL);
INSERT INTO inventory VALUES(444,'165826_XC12097642','N/A Bev, Soda, Duranzo, Joya','ALVARADO''S',38.0,38.0,'4/22/2025','ea','ea','each','24 x 16 oz',100.0,'N/A Bev, Soda, Duranzo, Joya',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943895',NULL,NULL);
INSERT INTO inventory VALUES(445,'165826_XC12097644','N/A Bev, Soda, Pina, Joya','ALVARADO''S',40.0,40.0,'4/22/2025','cs','case','each','24 x 500 ml',100.0,'N/A Bev, Soda, Pina, Joya',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943901',NULL,NULL);
INSERT INTO inventory VALUES(447,'58897_XC6949630','Produce, Carrots, Jumbo, Fresh','Jorge Garza',23.5,23.5,'2/4/2025','cs','case','','50 lb',100.0,'Produce, Carrots, Jumbo, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.943912',NULL,NULL);
INSERT INTO inventory VALUES(448,'58897_XC10610694','Produce, Onions, Yellow','Jorge Garza',19.94999999999999929,19.94999999999999929,'3/24/2025','case','case','','50 lb',100.0,'Produce, Onions, Yellow',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.944593',NULL,NULL);
INSERT INTO inventory VALUES(454,'INDV98','Dry Goods, Ketchup Packets','JAKE''S, INC.',31.08999999999999986,31.08999999999999986,'6/2/2025','cs','case','each','1000 x 1 each',100.0,'Dry Goods, Ketchup Packets',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.944641',NULL,NULL);
INSERT INTO inventory VALUES(461,'9329384','Dry Goods, Ketchup Packets','US Foods',31.78999999999999915,31.78999999999999915,'7/2/2025','cs','case','each','1000 x 1 each',100.0,'Dry Goods, Ketchup Packets',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.944683',NULL,NULL);
INSERT INTO inventory VALUES(471,'ROLP69','LABEL 2X4 SHELF LIFE REMOVABL','JAKES, INC.',20.0,20.0,'2/17/2025','cs','case','','1 x 500',100.0,'',1,'2025-07-04 21:29:47','2025-07-04T16:46:01.944741',NULL,NULL);
INSERT INTO inventory VALUES(474,'OILS49','Dry Goods, Shortening, Pork Lard','US Foods',68.29000000000000626,68.29000000000000626,'6/30/2025','cs','case','','50 lb',100.0,'Dry Goods, Shortening, Pork Lard',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.944759',NULL,NULL);
INSERT INTO inventory VALUES(475,'32165','Dry Goods, Chicken  Breading, Lea Jane Recipe','ALTAMIRA LTD.',94.8499999999999944,94.8499999999999944,'3/19/2025','cs','case','','50 lb',100.0,'Dry Goods, Chicken  Breading, Lea Jane Recipe',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.944765',NULL,NULL);
INSERT INTO inventory VALUES(477,'DMIX11','N/A Bev, Lemonade, Sweet, Pure','JAKES, INC.',81.95999999999999374,81.95999999999999374,'5/30/2025','cs','case','each','8 x 55 oz',100.0,'N/A Bev, Lemonade, Sweet, Pure',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.945311',NULL,NULL);
INSERT INTO inventory VALUES(480,'58897_XC48718','Produce, Lemon Juice','Jorge Garza',6.990000000000000213,6.990000000000000213,'1/6/2025','ea','ea','','0.5 gal',100.0,'Produce, Lemon Juice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.945332',NULL,NULL);
INSERT INTO inventory VALUES(482,'PR3001','Produce, Lettuce, Living','JAKE''S, INC.',26.39999999999999858,26.39999999999999858,'2/21/2025','cs','case','','18 each',100.0,'Produce, Lettuce, Living',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.945345',NULL,NULL);
INSERT INTO inventory VALUES(497,'44313','Produce, Limes, Fresh','RESTAURANT DEPOT',7.69000000000000039,7.69000000000000039,'5/28/2025','cs','case','','5 lb',100.0,'Produce, Limes, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.945432',NULL,NULL);
INSERT INTO inventory VALUES(504,'GLIN18','Non, Trash Can Liner, Black','JAKE''S, INC.',53.96000000000000085,53.96000000000000085,'4/28/2025','cs','case','each','100 each',100.0,'Non, Trash Can Liner, Black',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946013',NULL,NULL);
INSERT INTO inventory VALUES(510,'58897_XC11725428','Dry Goods, Mayonnaise, Heavy','Jorge Garza',12.94999999999999929,12.94999999999999929,'3/15/2025','each','each','','1 gal',100.0,'Dry Goods, Mayonnaise, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946051',NULL,NULL);
INSERT INTO inventory VALUES(511,'36243','Dry Goods, Mayonnaise, Heavy','RESTAURANT DEPOT',10.33000000000000007,10.33000000000000007,'4/22/2025','each','each','','1 gal',100.0,'Dry Goods, Mayonnaise, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946057',NULL,NULL);
INSERT INTO inventory VALUES(517,'MAYO32','Dry Goods, Mayonnaise, Heavy','JAKES, INC.',12.47000000000000063,12.47000000000000063,'3/11/2025','ea','ea','','1 gal',100.0,'Dry Goods, Mayonnaise, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946096',NULL,NULL);
INSERT INTO inventory VALUES(518,'MAYO02','Dry Goods, Mayonnaise, Heavy','JAKES, INC.',10.88000000000000079,10.88000000000000079,'2/17/2025','ea','ea','','1 gallon',100.0,'Dry Goods, Mayonnaise, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946102',NULL,NULL);
INSERT INTO inventory VALUES(521,'6328157','Dry Goods, Mayonnaise, Heavy','US Foods',15.43999999999999951,15.43999999999999951,'7/2/2025','ea','ea','','1 gal',100.0,'Dry Goods, Mayonnaise, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946120',NULL,NULL);
INSERT INTO inventory VALUES(523,'48001265301','Dry Goods, Mayonnaise, Heavy','RESTAURANT DEPOT',21.98999999999999843,21.98999999999999843,'4/1/2025','ea','ea','','1 gal',100.0,'Dry Goods, Mayonnaise, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946131',NULL,NULL);
INSERT INTO inventory VALUES(524,'48001265400','Dry Goods, Mayonnaise, Heavy','RESTAURANT DEPOT',22.73999999999999843,22.73999999999999843,'5/20/2025','ea','ea','','1 gallon',100.0,'Dry Goods, Mayonnaise, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946137',NULL,NULL);
INSERT INTO inventory VALUES(525,'52100010793','Dry Food. Lemon Pepper','RESTAURANT DEPOT',12.32000000000000028,12.32000000000000028,'3/28/2025','oz','oz','','168 oz',100.0,'Dry Food. Lemon Pepper',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946142',NULL,NULL);
INSERT INTO inventory VALUES(526,'49000044225','N/A Bev, DRINK SODA COLA COKE MEX GLS','RESTAURANT DEPOT',38.10999999999999944,38.10999999999999944,'3/10/2025','case','case','each','24 x 335 ml',100.0,'N/A Bev, DRINK SODA COLA COKE MEX GLS',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946149',NULL,NULL);
INSERT INTO inventory VALUES(529,'MLK051','Dairy, Milk, Whole','JAKE''S, INC.',22.92000000000000171,22.92000000000000171,'5/26/2025','cs','case','each','4 x 1 gal',100.0,'Dairy, Milk, Whole',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946166',NULL,NULL);
INSERT INTO inventory VALUES(532,'41900076382','Dairy, Milk, Whole','RESTAURANT DEPOT',17.44000000000000127,17.44000000000000127,'4/29/2025','cs','case','each','4 x 1 gal',100.0,'Dairy, Milk, Whole',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946184',NULL,NULL);
INSERT INTO inventory VALUES(533,'370441','Dairy, Milk, Whole','RESTAURANT DEPOT',17.44000000000000127,17.44000000000000127,'4/22/2025','gal','gal','gal','4 x 1 gallon',100.0,'Dairy, Milk, Whole',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946190',NULL,NULL);
INSERT INTO inventory VALUES(539,'MLK060','Dairy, Milk, Whole','US Foods',23.87999999999999901,23.87999999999999901,'7/2/2025','cs','case','each','4 x 1 gal',100.0,'Dairy, Milk, Whole',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946225',NULL,NULL);
INSERT INTO inventory VALUES(541,'016D','Dessert, King Cake','CB Commissary LLC',0.930000000000000048,0.930000000000000048,'3/29/2025','ea','ea','','1 each',100.0,'Dessert, King Cake',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946236',NULL,NULL);
INSERT INTO inventory VALUES(544,'DRES37','Dry Goods, Ranch Dressing, Mix, Dry','JAKE''S, INC.',40.28999999999999915,40.28999999999999915,'5/9/2025','cs','case','each','18 x 3.2 oz',100.0,'Dry Goods, Ranch Dressing, Mix, Dry',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946254',NULL,NULL);
INSERT INTO inventory VALUES(549,'MUST16','Dry Goods, Mustard, Creole','US Foods',19.85999999999999944,19.85999999999999944,'6/16/2025','ea','ea','','1 gal',100.0,'Dry Goods, Mustard, Creole',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946283',NULL,NULL);
INSERT INTO inventory VALUES(551,'27541009095','N/A Bev, WATER PLST BTL CLR TWIST CAP','RESTAURANT DEPOT',3.75,3.75,'4/15/2025','cs','case','each','32 x 1 each',100.0,'N/A Bev, WATER PLST BTL CLR TWIST CAP',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946295',NULL,NULL);
INSERT INTO inventory VALUES(552,'1220319','N/A Bev, Water, Still, Bottles','RESTAURANT DEPOT',3.75,3.75,'4/22/2025','cs','case','each','32 x 0.5 l',100.0,'N/A Bev, Water, Still, Bottles',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946301',NULL,NULL);
INSERT INTO inventory VALUES(558,'OIL027','Dry Goods, Oil, Canola, Clear, Frying','JAKE''S, INC.',29.17999999999999972,29.17999999999999972,'5/26/2025','cs','case','','35 lb',100.0,'Dry Goods, Oil, Canola, Clear, Frying',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946856',NULL,NULL);
INSERT INTO inventory VALUES(561,'OILS28','Dry Goods, Oil, Canola, Salad','JAKE''S, INC.',42.14000000000000056,42.14000000000000056,'4/28/2025','cs','case','','35 lb',100.0,'Dry Goods, Oil, Canola, Salad',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946873',NULL,NULL);
INSERT INTO inventory VALUES(565,'400471','Dry Goods, Olive and Truffle Oil','JAKES, INC.',15.35999999999999944,15.35999999999999944,'5/20/2025','cs','case','','8.5 ml',100.0,'Dry Goods, Olive and Truffle Oil',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946897',NULL,NULL);
INSERT INTO inventory VALUES(573,'PR1411','Produce, Onions, Green, wt','US Foods',31.73000000000000042,31.73000000000000042,'6/27/2025','cs','case','each','4 x 2 lb',100.0,'Produce, Onions, Green, wt',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.946943',NULL,NULL);
INSERT INTO inventory VALUES(580,'PR1400','Produce, Onion, Yellow, Collossal','JAKES, INC.',21.71999999999999887,21.71999999999999887,'5/23/2025','cs','case','','50 lb',100.0,'Produce, Onion, Yellow, Collossal',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.947002',NULL,NULL);
INSERT INTO inventory VALUES(599,'58897_XC5296039','Dry Goods,  Spice, Paprika, Powder','Jorge Garza',4.790000000000000035,4.790000000000000035,'3/18/2025','case','case','','1 lb',100.0,'Dry Goods,  Spice, Paprika, Powder',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.947111',NULL,NULL);
INSERT INTO inventory VALUES(603,'SPAG21','Dry Goods, Pasta, Cavatappi','JAKES, INC.',35.42999999999999972,35.42999999999999972,'3/18/2025','cs','case','each','2 x 10 lb',100.0,'Dry Goods, Pasta, Cavatappi',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.947135',NULL,NULL);
INSERT INTO inventory VALUES(607,'1023018','Dry Goods, Pasta, Cavatappi','US Foods',35.22999999999999687,35.22999999999999687,'7/2/2025','case','case','lb','2 x 10 lb',100.0,'Dry Goods, Pasta, Cavatappi',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.947668',NULL,NULL);
INSERT INTO inventory VALUES(610,'3.0223E+11','Produce, Cabbage, Red, Shredded','RESTAURANT DEPOT',8.839999999999999858,8.839999999999999858,'4/29/2025','ea',NULL,NULL,'1 x 10',100.0,'Produce, Cabbage, Red, Shredded',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948359',NULL,NULL);
INSERT INTO inventory VALUES(611,'50622','Produce, Cabbage, Red, Shredded','RESTAURANT DEPOT',8.839999999999999858,8.839999999999999858,'4/22/2025','cs','case','','5 lb',100.0,'Produce, Cabbage, Red, Shredded',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948373',NULL,NULL);
INSERT INTO inventory VALUES(612,'50624','Produce, Carrot, Shredded','RESTAURANT DEPOT',6.570000000000000284,6.570000000000000284,'4/22/2025','bag','bag','','5 lb',100.0,'Produce, Carrot, Shredded',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948381',NULL,NULL);
INSERT INTO inventory VALUES(613,'17923001168','Produce, Carrot, Shredded','RESTAURANT DEPOT',6.570000000000000284,6.570000000000000284,'4/29/2025','bag','bag','each','5 lb',100.0,'Produce, Carrot, Shredded',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948387',NULL,NULL);
INSERT INTO inventory VALUES(614,'7.40695E+12','Produce, Celery Stalks, Fresh','RESTAURANT DEPOT',6.25,6.25,'4/1/2025','bag',NULL,NULL,'5 each',100.0,'Produce, Celery Stalks, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948394',NULL,NULL);
INSERT INTO inventory VALUES(616,'6.80444E+11','Produce, Garlic, White, Whole Cloves','RESTAURANT DEPOT',16.58999999999999986,16.58999999999999986,'4/1/2025','cs',NULL,NULL,'5 each',100.0,'Produce, Garlic, White, Whole Cloves',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948406',NULL,NULL);
INSERT INTO inventory VALUES(617,'28764000456','Produce, Collard Greens, Fresh, By Weight','RESTAURANT DEPOT',7.990000000000000213,7.990000000000000213,'5/13/2025','cs','case','','2.5 lb',100.0,'Produce, Collard Greens, Fresh, By Weight',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948412',NULL,NULL);
INSERT INTO inventory VALUES(618,'2876400045','Produce, Collard Greens, Fresh, By Weight','RESTAURANT DEPOT',9.52999999999999937,9.52999999999999937,'4/15/2025','cs','case','each','4 x 2.5 lb',100.0,'Produce, Collard Greens, Fresh, By Weight',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948418',NULL,NULL);
INSERT INTO inventory VALUES(619,'42312','Produce, Collard Greens, Fresh, By Weight','RESTAURANT DEPOT',29.21999999999999887,29.21999999999999887,'4/22/2025','ea','ea','each','4 x 2.5 lb',100.0,'Produce, Collard Greens, Fresh, By Weight',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948424',NULL,NULL);
INSERT INTO inventory VALUES(620,'8.96968E+11','Produce, Lemon Juice','RESTAURANT DEPOT',7.379999999999999894,7.379999999999999894,'4/2/2025','cs',NULL,NULL,'5 each',100.0,'Produce, Lemon Juice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948430',NULL,NULL);
INSERT INTO inventory VALUES(621,'430288','Produce, Lemon Juice','RESTAURANT DEPOT',7.379999999999999894,7.379999999999999894,'4/22/2025','ea','ea','','0.5 gal',100.0,'Produce, Lemon Juice',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948436',NULL,NULL);
INSERT INTO inventory VALUES(622,'2876400126','PD KALE CHOPPED','RESTAURANT DEPOT',6.820000000000000284,6.820000000000000284,'3/19/2025','cs','case','','5 lb',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948442',NULL,NULL);
INSERT INTO inventory VALUES(623,'20600425195','Produce, Kale, Green, Fresh, by Count','RESTAURANT DEPOT',25.28999999999999915,25.28999999999999915,'4/29/2025','unit','each','','24 each',100.0,'Produce, Kale, Green, Fresh, by Count',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948448',NULL,NULL);
INSERT INTO inventory VALUES(624,'8.13831E+12','Produce, Kale, Green, Fresh, by Count','RESTAURANT DEPOT',24.01999999999999958,24.01999999999999958,'5/13/2025','cs',NULL,NULL,'1 x 24',100.0,'Produce, Kale, Green, Fresh, by Count',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948453',NULL,NULL);
INSERT INTO inventory VALUES(625,'42519','Produce, Kale, Green, Fresh, by Count','RESTAURANT DEPOT',26.58999999999999986,26.58999999999999986,'4/22/2025','cs','case','','1 each',100.0,'Produce, Kale, Green, Fresh, by Count',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948460',NULL,NULL);
INSERT INTO inventory VALUES(626,'28764000661','Produce, Salad Mix, Kale, Shredded','RESTAURANT DEPOT',10.81000000000000049,10.81000000000000049,'3/10/2025','cs','case','','2.5 lb',100.0,'Produce, Salad Mix, Kale, Shredded',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948470',NULL,NULL);
INSERT INTO inventory VALUES(627,'43858','Produce, Lettuce, Romaine','RESTAURANT DEPOT',4.400000000000000356,4.400000000000000356,'5/28/2025','cs','case','','1 each',100.0,'Produce, Lettuce, Romaine',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948476',NULL,NULL);
INSERT INTO inventory VALUES(628,'8.13831E+11','Produce, Onions, Green, wt','RESTAURANT DEPOT',10.09999999999999965,10.09999999999999965,'4/29/2025','cs',NULL,NULL,'4 each',100.0,'Produce, Onions, Green, wt',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948481',NULL,NULL);
INSERT INTO inventory VALUES(629,'53408','Produce, Shallots, Peeled, Fresh','RESTAURANT DEPOT',58.43999999999999773,58.43999999999999773,'5/28/2025','cs','case','','8 lb',100.0,'Produce, Shallots, Peeled, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948487',NULL,NULL);
INSERT INTO inventory VALUES(630,'20600800169','Produce, Green Cabbage, Fresh, by Count','RESTAURANT DEPOT',7.219999999999999752,7.219999999999999752,'4/29/2025','cs','case','each','3 x 1 each',100.0,'Produce, Green Cabbage, Fresh, by Count',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.948493',NULL,NULL);
INSERT INTO inventory VALUES(636,'101841_XC10776472','Dessert, Pecan Bundt Cake','MJ Sweet and Cake',32.0,32.0,'6/24/2025','each','each','','8 each',100.0,'Dessert, Pecan Bundt Cake',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949060',NULL,NULL);
INSERT INTO inventory VALUES(638,'74234951124','Dry Goods, Chipotle Peppers, Can','RESTAURANT DEPOT',5.950000000000000177,5.950000000000000177,'5/20/2025','cs','case','','28 oz',100.0,'Dry Goods, Chipotle Peppers, Can',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949072',NULL,NULL);
INSERT INTO inventory VALUES(644,'PR1568','Produce, Peppers, Red','JAKES, INC.',95.3700000000000045,95.3700000000000045,'5/23/2025','cs','case','','10 lb',100.0,'Produce, Peppers, Red',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949108',NULL,NULL);
INSERT INTO inventory VALUES(652,'PICK41','Dry Goods, Pickle, DIll, Slices','JAKES, INC.',26.19999999999999929,26.19999999999999929,'6/9/2025','ea','ea','','5 gal',100.0,'Dry Goods, Pickle, DIll, Slices',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949154',NULL,NULL);
INSERT INTO inventory VALUES(669,'40138','Produce, Onions, Green, wt','RESTAURANT DEPOT',10.09999999999999965,10.09999999999999965,'5/28/2025','bag','bag','','4 lb',100.0,'Produce, Onions, Green, wt',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949785',NULL,NULL);
INSERT INTO inventory VALUES(670,'6.46127E+11','Produce, Shallots, Peeled, Fresh','RESTAURANT DEPOT',7.730000000000000426,7.730000000000000426,'5/20/2025','bag',NULL,NULL,'1 each',100.0,'Produce, Shallots, Peeled, Fresh',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949790',NULL,NULL);
INSERT INTO inventory VALUES(680,'68274669316','PURE LIFE 35PK .5LTR','RESTAURANT DEPOT',5.389999999999999681,5.389999999999999681,'4/29/2025','case','case','each','35 x 500 ml',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949846',NULL,NULL);
INSERT INTO inventory VALUES(681,'58897_XC11484063','Dairy, Cream, Heavy','Jorge Garza',5.429999999999999716,5.429999999999999716,'3/24/2025','cs','case','','1 qt',100.0,'Dairy, Cream, Heavy',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.949852',NULL,NULL);
INSERT INTO inventory VALUES(688,'58897_XC7505960','Produce, Onions, Red','Jorge Garza',19.0,19.0,'3/24/2025','ea','ea','','25 lb',100.0,'Produce, Onions, Red',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.950411',NULL,NULL);
INSERT INTO inventory VALUES(692,'1090094','Dry Goods, Crackers, Ritz','RESTAURANT DEPOT',9.039999999999999147,9.039999999999999147,'4/17/2025','cs','case','','27.4 oz',100.0,'Dry Goods, Crackers, Ritz',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.950435',NULL,NULL);
INSERT INTO inventory VALUES(693,'44000058326','Dry Goods, Crackers, Ritz','RESTAURANT DEPOT',50.07000000000000028,50.07000000000000028,'5/20/2025','ea','ea','each','6 x 27.4 oz',100.0,'Dry Goods, Crackers, Ritz',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.950441',NULL,NULL);
INSERT INTO inventory VALUES(702,'PR0399','Produce, Carrot, Shredded','JAKES, INC.',29.12000000000000099,29.12000000000000099,'6/4/2025','ea','ea','each','4 x 5 lb',100.0,'Produce, Carrot, Shredded',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.950494',NULL,NULL);
INSERT INTO inventory VALUES(705,'PR9903','Produce, Pepper, Habanero','JAKES, INC.',39.67999999999999972,39.67999999999999972,'6/4/2025','cs','case','','8 lb',100.0,'Produce, Pepper, Habanero',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.950512',NULL,NULL);
INSERT INTO inventory VALUES(711,'SALT20','Dry Goods, Salt, Kosher','JAKE''S, INC.',8.47000000000000064,8.47000000000000064,'5/26/2025','cs','case','box','9 x 3 lb',100.0,'Dry Goods, Salt, Kosher',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.950547',NULL,NULL);
INSERT INTO inventory VALUES(715,'ORSA18','Dry Goods, Sauce, Chile Sambal','JAKES, INC.',73.9200000000000017,73.9200000000000017,'5/12/2025','ea','ea','each','3 x 1 gal',100.0,'Dry Goods, Sauce, Chile Sambal',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.950570',NULL,NULL);
INSERT INTO inventory VALUES(724,'SAUC06','Dry Goods, Sauce, Buffalo Wing Red Hot','JAKES, INC.',22.25,22.25,'5/23/2025','jug','each','','1 gal',100.0,'Dry Goods, Sauce, Buffalo Wing Red Hot',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951162',NULL,NULL);
INSERT INTO inventory VALUES(725,'41500741611','Dry Goods, Sauce, Buffalo Wing Red Hot','RESTAURANT DEPOT',15.40000000000000035,15.40000000000000035,'4/15/2025','cs','case','','1 gal',100.0,'Dry Goods, Sauce, Buffalo Wing Red Hot',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951168',NULL,NULL);
INSERT INTO inventory VALUES(729,'ORSA32','Dry Goods, Sauce, Chilli & Garlic','JAKES, INC.',27.55999999999999873,27.55999999999999873,'3/4/2025','jar','jar','','136 oz',100.0,'Dry Goods, Sauce, Chilli & Garlic',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951191',NULL,NULL);
INSERT INTO inventory VALUES(738,'41390001710','Dry Good.SAUCE SOY','RESTAURANT DEPOT',14.75999999999999979,14.75999999999999979,'3/10/2025','case','case','each','4 x 1 gal',100.0,'Dry Good.SAUCE SOY',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951252',NULL,NULL);
INSERT INTO inventory VALUES(740,'11210000032','Dry Good, Sauce, Tabasco','RESTAURANT DEPOT',7.019999999999999574,7.019999999999999574,'5/20/2025','cs','case','','5 ml',100.0,'Dry Good, Sauce, Tabasco',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951264',NULL,NULL);
INSERT INTO inventory VALUES(742,'BQSA21','Dry Goods, Sauce, BBQ Hickory','US Foods',17.10000000000000143,17.10000000000000143,'7/2/2025','each','each','','1 gal',100.0,'Dry Goods, Sauce, BBQ Hickory',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951276',NULL,NULL);
INSERT INTO inventory VALUES(752,'OILS46','Dry Goods, Shortening Oil, Clear','JAKE''S, INC.',63.49000000000000198,63.49000000000000198,'3/24/2025','cs','case','','50 lb',100.0,'Dry Goods, Shortening Oil, Clear',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951333',NULL,NULL);
INSERT INTO inventory VALUES(759,'1020020','Dry Goods, Shortening Oil, Clear','RESTAURANT DEPOT',58.06000000000000227,58.06000000000000227,'4/22/2025','ea','ea','','50 lb',100.0,'Dry Goods, Shortening Oil, Clear',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951372',NULL,NULL);
INSERT INTO inventory VALUES(762,'OILS91','SHORTENING OIL CLEAR LIQ FRY','JAKE''S, INC.',25.64000000000000056,25.64000000000000056,'3/7/2025','case','case','','35 pound',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951389',NULL,NULL);
INSERT INTO inventory VALUES(767,'SMP014','Protein, Shrimp, White','JAKE''S, INC.',8.490000000000000213,8.490000000000000213,'3/21/2025','lb','lb','','1 lb',100.0,'Protein, Shrimp, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951417',NULL,NULL);
INSERT INTO inventory VALUES(768,'SMP027','Protein, Shrimp, White','US Foods',5.660000000000000142,5.660000000000000142,'7/2/2025','lb','lb','','1 lb',100.0,'Protein, Shrimp, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951423',NULL,NULL);
INSERT INTO inventory VALUES(770,'SHMP42','Protein, Shrimp, White','JAKES, INC.',6.80999999999999961,6.80999999999999961,'3/11/2025','lb','lb','','1 lb',100.0,'Protein, Shrimp, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951434',NULL,NULL);
INSERT INTO inventory VALUES(773,'8.10044E+11','Protein, Shrimp, White','RESTAURANT DEPOT',51.64999999999999858,51.64999999999999858,'3/28/2025','bag',NULL,NULL,'2 each',100.0,'Protein, Shrimp, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951451',NULL,NULL);
INSERT INTO inventory VALUES(776,'58897_XC11725427','Dry Goods, Pickle, DIll, Slices','Jorge Garza',33.5,33.5,'3/15/2025','each','each','','5 gal',100.0,'Dry Goods, Pickle, DIll, Slices',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951469',NULL,NULL);
INSERT INTO inventory VALUES(779,'PR0770','Produce, Kale, Green, Fresh, by Weight','JAKES, INC.',29.51000000000000156,29.51000000000000156,'5/23/2025','cs','case','','25 lb',100.0,'Produce, Kale, Green, Fresh, by Weight',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951486',NULL,NULL);
INSERT INTO inventory VALUES(784,'472265','N/A Bev, Soda, Fanta, Orange, Mexican','JAKE''S, INC.',44.09000000000000342,44.09000000000000342,'6/2/2025','cs','case','each','24 x 500 ml',100.0,'N/A Bev, Soda, Fanta, Orange, Mexican',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951515',NULL,NULL);
INSERT INTO inventory VALUES(791,'7.60696E+11','Dry Goods, Red Pepper, Crushed','RESTAURANT DEPOT',7.870000000000000106,7.870000000000000106,'5/20/2025','cs',NULL,NULL,'1 x 16',100.0,'Dry Goods, Red Pepper, Crushed',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951555',NULL,NULL);
INSERT INTO inventory VALUES(792,'41398','Dry Goods, Spice, Cayenne Pepper, Ground','RESTAURANT DEPOT',20.71999999999999887,20.71999999999999887,'5/28/2025','bg','bag','','5 lb',100.0,'Dry Goods, Spice, Cayenne Pepper, Ground',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951561',NULL,NULL);
INSERT INTO inventory VALUES(796,'ISP016','Dry Goods, Lemon Pepper','JAKE''S, INC.',12.96000000000000085,12.96000000000000085,'5/9/2025','cs','case','each','6 x 20 oz',100.0,'Dry Goods, Lemon Pepper',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951583',NULL,NULL);
INSERT INTO inventory VALUES(816,'8.12944E+11','SPOON 13" BK|H PRF 1CT','RESTAURANT DEPOT',3.319999999999999841,3.319999999999999841,'3/19/2025','cs',NULL,NULL,'1 x 13',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951700',NULL,NULL);
INSERT INTO inventory VALUES(818,'58897_XC10447739','N/A Bev, Soda, Sprite','Jorge Garza',41.5,41.5,'3/18/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Soda, Sprite',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951712',NULL,NULL);
INSERT INTO inventory VALUES(825,'SUGR03','Dry Goods, Sugar, White','JAKES, INC.',24.41000000000000014,24.41000000000000014,'4/8/2025','cs','case','','25 lb',100.0,'Dry Goods, Sugar, White',1,'2025-07-04 21:29:47','2025-07-04T16:46:01.951755',NULL,NULL);
INSERT INTO inventory VALUES(827,'400188','Dry Goods, Sugar, White','JAKES, INC.',36.04999999999999715,36.04999999999999715,'5/12/2025','cs','case','','50 lb',100.0,'Dry Goods, Sugar, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951766',NULL,NULL);
INSERT INTO inventory VALUES(829,'SUGR06','SUGAR EFG GRANULATED 403522','JAKES, INC.',32.35999999999999944,32.35999999999999944,'3/13/2025','ea','ea','','25 lb',100.0,'',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951778',NULL,NULL);
INSERT INTO inventory VALUES(831,'4395612','Dry Goods, Sugar, White','US Foods',28.64999999999999858,28.64999999999999858,'6/27/2025','cs','case','','25 lb',100.0,'Dry Goods, Sugar, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951789',NULL,NULL);
INSERT INTO inventory VALUES(839,'TEA030','N/A Bev, Tea, Regular','JAKE''S, INC.',27.67999999999999972,27.67999999999999972,'4/14/2025','case','case','each','24 x 4 oz',100.0,'N/A Bev, Tea, Regular',1,'2025-07-04 21:29:47','2025-07-04T16:46:01.951835',NULL,NULL);
INSERT INTO inventory VALUES(841,'TEA031','N/A Bev, Tea,  Sweet Brew, Pure','JAKE''S, INC.',59.8299999999999983,59.8299999999999983,'1/23/2025','cs','case','','8 each',100.0,'N/A Bev, Tea,  Sweet Brew, Pure',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951846',NULL,NULL);
INSERT INTO inventory VALUES(852,'165826_XC12097640','N/A Bev, Water, Mineral, Topo Chico, Bottle','ALVARADO''S',28.0,28.0,'4/22/2025','cs','case','each','24 x 16 oz',100.0,'N/A Bev, Water, Mineral, Topo Chico, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951909',NULL,NULL);
INSERT INTO inventory VALUES(853,'58897_XC10447738','N/A Bev, Water, Mineral, Topo Chico, Bottle','Jorge Garza',32.5,32.5,'3/24/2025','cs','case','each','24 x 12 oz',100.0,'N/A Bev, Water, Mineral, Topo Chico, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951915',NULL,NULL);
INSERT INTO inventory VALUES(854,'87914','N/A Bev, Water, Mineral, Topo Chico, Bottle','RESTAURANT DEPOT',29.69000000000000127,29.69000000000000127,'4/17/2025','cs','case','each','24 x 20 oz',100.0,'N/A Bev, Water, Mineral, Topo Chico, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951921',NULL,NULL);
INSERT INTO inventory VALUES(855,'21136070378','N/A Bev, Water, Mineral, Topo Chico, Bottle','RESTAURANT DEPOT',29.69000000000000127,29.69000000000000127,'4/2/2025','cs','case','each','24 x 12 oz',100.0,'N/A Bev, Water, Mineral, Topo Chico, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951927',NULL,NULL);
INSERT INTO inventory VALUES(857,'SALT03','Dry Goods, Salt, Kosher','JAKE''S, INC.',3.540000000000000035,3.540000000000000035,'5/9/2025','case','case','','12 x 3 lb',100.0,'Dry Goods, Salt, Kosher',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951939',NULL,NULL);
INSERT INTO inventory VALUES(858,'272261','N/A Bev, Coca Cola, Mexican, Bottle','JAKES, INC.',39.5,39.5,'6/9/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Coca Cola, Mexican, Bottle',1,'2025-07-04 21:29:47','2025-07-04T16:46:01.951944',NULL,NULL);
INSERT INTO inventory VALUES(862,'369874','Produce, VINEGAR APPLE CIDER SPW LN','JAKES, INC.',12.96000000000000085,12.96000000000000085,'5/16/2025','ea','ea','','1 gal',100.0,'Produce, VINEGAR APPLE CIDER SPW LN',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951967',NULL,NULL);
INSERT INTO inventory VALUES(865,'270670','Dry Goods, Vinegar, Red Wine','JAKES, INC.',16.73000000000000042,16.73000000000000042,'5/23/2025','ea','ea','each','2 x 5 l',100.0,'Dry Goods, Vinegar, Red Wine',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951984',NULL,NULL);
INSERT INTO inventory VALUES(866,'OLVS24','Dry Goods, Vinegar, Rice Wine','JAKE''S, INC.',78.71999999999999887,78.71999999999999887,'5/26/2025','jug','each','','128 ml',100.0,'Dry Goods, Vinegar, Rice Wine',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.951990',NULL,NULL);
INSERT INTO inventory VALUES(868,'410006','Dry Goods, SO VINEGAR WH 50GR','US Foods',20.16000000000000014,20.16000000000000014,'6/30/2025','cs','case','each','6 x 1 gal',100.0,'Dry Goods, SO VINEGAR WH 50GR',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952001',NULL,NULL);
INSERT INTO inventory VALUES(871,'OLVS11','Dry Goods, Vinegar, White','US Foods',4.240000000000000213,4.240000000000000213,'6/27/2025','ea','ea','','1 gal',100.0,'Dry Goods, Vinegar, White',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952018',NULL,NULL);
INSERT INTO inventory VALUES(873,'OLVS13','Dry Goods, Vinegar, Red Wine','JAKES, INC.',14.41999999999999993,14.41999999999999993,'5/23/2025','bottle','each','','1 gal',100.0,'Dry Goods, Vinegar, Red Wine',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952029',NULL,NULL);
INSERT INTO inventory VALUES(874,'7.60695E+11','Non Con, To Go Bags','RESTAURANT DEPOT',12.93999999999999951,12.93999999999999951,'4/1/2025','case',NULL,NULL,'4 each',100.0,'Non Con, To Go Bags',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952035',NULL,NULL);
INSERT INTO inventory VALUES(877,'CDNK24','N/A Bev, Water, Still, Bottles','JAKE''S, INC.',6.570000000000000284,6.570000000000000284,'5/26/2025','cs','case','each','24 x 16.9 oz',100.0,'N/A Bev, Water, Still, Bottles',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952052',NULL,NULL);
INSERT INTO inventory VALUES(879,'272352','N/A Bev, Water, Mineral, Topo Chico, Bottle','JAKE''S, INC.',40.04999999999999715,40.04999999999999715,'6/2/2025','cs','case','','24 x 12 oz',100.0,'N/A Bev, Water, Mineral, Topo Chico, Bottle',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952064',NULL,NULL);
INSERT INTO inventory VALUES(884,'405123','N/A Bev, Soda, Jarritos, Lime','US Foods',37.29999999999999715,37.29999999999999715,'7/2/2025','cs','case','each','24 x 1 each',100.0,'N/A Bev, Soda, Jarritos, Lime',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952604',NULL,NULL);
INSERT INTO inventory VALUES(886,'58897_XC11725429','Dairy, Milk, Whole','Jorge Garza',4.740000000000000213,4.740000000000000213,'3/24/2025','gal','gal','','1 gallon',100.0,'Dairy, Milk, Whole',0,'2025-07-04 21:29:47','2025-07-04T16:46:01.952617',NULL,NULL);
INSERT INTO inventory VALUES(890,'BSPI75','Dry Goods, Black Pepper, Ground','JAKES, INC.',48.27000000000000312,NULL,NULL,NULL,'case','','5 lb',100.0,NULL,0,'2025-07-06 12:45:08','2025-07-06 12:45:08',NULL,NULL);
INSERT INTO inventory VALUES(891,'NC001','Non Con Cup 2oz Clear Plastic','Restaurant Supply',45.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 15:15:58','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(892,'NC002','Non Con Lids 1.5-2oz Souffle Clear','Restaurant Supply',35.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 15:15:58','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(893,'DG001','Dry Goods, Waffle Cone','Restaurant Supply',0.75,NULL,NULL,NULL,'case','each','24 each',100.0,NULL,0,'2025-07-06 15:15:58','2025-07-06 15:15:58',NULL,NULL);
INSERT INTO inventory VALUES(894,'DG002','Worcestershire Sauce','Restaurant Supply',3.5,NULL,NULL,NULL,'each','oz','10 oz',100.0,NULL,0,'2025-07-06 15:15:58','2025-07-06 15:15:58',NULL,NULL);
INSERT INTO inventory VALUES(895,'DG003','Dry Goods, Sambal Chill Sauce (wt)','Restaurant Supply',8.5,NULL,NULL,NULL,'each','oz','32 oz',100.0,NULL,0,'2025-07-06 15:15:58','2025-07-06 15:15:58',NULL,NULL);
INSERT INTO inventory VALUES(896,'DG004','Dry Goods, MAYONNAISE  HVY PLST SHLF','Restaurant Supply',15.0,NULL,NULL,NULL,'each','oz','128 oz',100.0,NULL,0,'2025-07-06 15:15:58','2025-07-06 15:15:58',NULL,NULL);
INSERT INTO inventory VALUES(899,'NC003','Non Con Cup 4oz Clear Plastic','Restaurant Supply',55.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(900,'NC004','Non Con Lids 4oz Clear','Restaurant Supply',40.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(901,'NC005','Non Con Cup 8oz Clear Plastic','Restaurant Supply',65.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(902,'NC006','Non Con Lids 8oz Clear','Restaurant Supply',45.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(903,'NC007','Non Con Souffle Cup 1.5oz Clear','Restaurant Supply',38.0,NULL,NULL,NULL,'case','each','2500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(904,'NC008','Non Con Souffle Cup 2oz Clear','Restaurant Supply',42.0,NULL,NULL,NULL,'case','each','2500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(905,'NC009','Non Con Napkin Cocktail 1ply White','Restaurant Supply',15.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(906,'NC010','Non Con Napkin Dinner 2ply White','Restaurant Supply',25.0,NULL,NULL,NULL,'case','each','300.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(907,'NC011','Non Con Fork Plastic Heavy Black','Restaurant Supply',28.0,NULL,NULL,NULL,'case','each','1000.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(908,'NC012','Non Con Knife Plastic Heavy Black','Restaurant Supply',28.0,NULL,NULL,NULL,'case','each','1000.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(909,'NC013','Non Con Spoon Plastic Heavy Black','Restaurant Supply',28.0,NULL,NULL,NULL,'case','each','1000.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(910,'NC014','Non Con Straw Wrapped 7.75in Clear','Restaurant Supply',18.0,NULL,NULL,NULL,'case','each','500.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
INSERT INTO inventory VALUES(911,'NC015','Non Con To Go Container 9x9x3 3comp','Restaurant Supply',85.0,NULL,NULL,NULL,'case','each','200.0 each',100.0,NULL,0,'2025-07-06 20:46:45','2025-07-06 20:46:45',NULL,NULL);
CREATE TABLE recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'Draft',
                recipe_group TEXT,
                recipe_type TEXT DEFAULT 'Recipe',
                food_cost REAL DEFAULT 0,
                food_cost_percentage REAL DEFAULT 0,
                labor_cost REAL DEFAULT 0,
                labor_cost_percentage REAL DEFAULT 0,
                menu_price REAL DEFAULT 0,
                gross_margin REAL DEFAULT 0,
                prime_cost REAL DEFAULT 0,
                prime_cost_percentage REAL DEFAULT 0,
                shelf_life TEXT,
                shelf_life_uom TEXT,
                prep_recipe_yield TEXT,
                prep_recipe_yield_uom TEXT,
                serving_size TEXT,
                serving_size_uom TEXT,
                per_serving REAL DEFAULT 0,
                station TEXT,
                procedure TEXT,
                cost_modified TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO recipes VALUES(67,'FC-03 Whole Wings','Draft','Main','Recipe',1.440199999999999925,11.57898596938860437,0.0,0.0,14.0,88.42101403061138853,1.440199999999999925,100.0,'','','','','1','each',1.621058035714404654,NULL,NULL,'06/27/2025 05:40:49','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(68,'Ritz Crumble','Draft','Toppings','PrepRecipe',5.27880000000000038,487.2992700729930106,0.0,0.0,0.0,0.0,5.27880000000000038,100.0,'3','Days','1','lb','2','oz',4.872992700729930071,NULL,NULL,'06/27/2025 04:50:59','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(69,'FT-02 Loaded Fries','Draft','Main','Recipe',6.519000000000000127,26.35062815925406809,0.0,0.0,14.0,73.64937184074592836,6.519000000000000127,100.0,'','','','','1','ea',3.6890879422955698,NULL,NULL,'06/27/2025 04:24:55','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(70,'French Fries - Portion','Complete','Sides','Recipe',0.4138000000000000011,10.53958994708992592,0.0,0.0,5.0,89.46041005291007764,0.4138000000000000011,100.0,'','','','','1','ea',0.5269794973544962291,NULL,NULL,'06/27/2025 04:13:24','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(71,'DP-05 Habanero Ranch','Draft','Sauces','Recipe',0.2819999999999999729,31.02632500003589655,0.0,0.0,1.0,68.97367499996408923,0.2819999999999999729,100.0,'','','','','2','oz',0.1551316250001794905,NULL,NULL,'06/27/2025 04:08:09','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(72,'DP-04 Hot Honey','Draft','Sauces','Recipe',0.0,19.17350954121044992,0.0,0.0,1.0,80.82649045878955008,0.0,100.0,'','','','','2','oz',0.0958675477060522557,NULL,NULL,'06/27/2025 04:06:55','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(73,'DP-03 Honey Mustard','Draft','Sauces','Recipe',0.4210999999999999743,44.9325750000534967,0.0,0.0,1.0,55.06742499994650331,0.4210999999999999743,100.0,'','','','','2','oz',0.2246628750002674924,NULL,NULL,'06/27/2025 04:05:30','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(74,'DP-02 Comeback Sauce','Draft','Sauces','Recipe',0.0,33.71064212966800256,0.0,0.0,1.0,66.28935787033199744,0.0,100.0,'','','','','2','oz',0.1685532106483400016,NULL,NULL,'06/27/2025 04:02:55','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(75,'DP-01 Charred-Onion Ranch Dip','Draft','Sauces','Recipe',0.00949999999999999977,83.32710625005216797,0.0,0.0,1.0,16.67289374994783557,0.00949999999999999977,100.0,'7','Days','','','2','oz',0.4166355312502608155,NULL,NULL,'06/27/2025 04:01:29','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(76,'SD-04 Fried Corn Ribs','Draft','Sides','Recipe',1.73799999999999999,34.35620535714286205,0.0,0.0,5.0,65.64379464285714504,1.73799999999999999,100.0,'7','Days','','','6','oz',0.2863017113095238098,NULL,NULL,'06/27/2025 03:58:47','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(77,'Mac Sauce - Modified 2025','Draft','Sauces','PrepRecipe',36.06010000000000559,1170.791318192534617,0.0,0.0,0.0,0.0,36.06010000000000559,100.0,'7','Days','4','gallon','1','ea',14.63489147740668272,NULL,NULL,'06/27/2025 03:55:25','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(78,'Roux recipe','Complete','Sauces','PrepRecipe',7.166999999999999816,225.2679999999999723,0.0,0.0,0.0,0.0,7.166999999999999816,100.0,'1','Weeks','4','lb','1','ea',2.815849999999999742,NULL,NULL,'06/27/2025 03:53:11','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(79,'LJ Mac','Draft','Sides','PrepRecipe',15.94350000000000022,431.4050896672396789,0.0,0.0,0.0,0.0,15.94350000000000022,100.0,'','','25','each','1','ea',0.8628101793344794546,NULL,NULL,'06/27/2025 03:51:29','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(80,'SD-03 LJ Mac','Draft','Sides','Recipe',0.553599999999999981,17.86948038003438199,0.0,0.0,5.0,82.13051961996562511,0.553599999999999981,100.0,'','','','','1','ea',0.8934740190017190776,NULL,NULL,'06/27/2025 03:40:29','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(81,'SD-02 Extra-Crispy Fries with Ranch Powder','Draft','Sides','Recipe',5.999499999999999388,12.52627633762247505,0.0,0.0,7.990000000000000213,87.47372366237750896,5.999499999999999388,100.0,'','','','','1','ea',0.6263138168811237527,NULL,NULL,'06/27/2025 03:36:00','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(82,'French Fries Recipe','Complete','Sides','PrepRecipe',0.4597999999999999865,10.53958994708992592,0.0,0.0,0.0,0.0,0.4597999999999999865,100.0,'','','5','oz','1','ea',0.1053958994708992513,NULL,NULL,'06/27/2025 03:34:09','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(83,'SD-01 Kale & Cabbage Slaw','Draft','Sides','Recipe',0.4263000000000000122,7.940020833336689953,0.0,0.0,5.0,92.05997916666331094,0.4263000000000000122,100.0,'7','','','','1','ea',0.397001041666834531,NULL,NULL,'06/27/2025 03:31:00','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(84,'Kale Kimchi Recipe','Complete','Sides','PrepRecipe',67.04979999999999051,1270.403333333870251,0.0,0.0,0.0,0.0,67.04979999999999051,100.0,'7','','50','lb','1','ea',1.270403333333870454,NULL,NULL,'06/27/2025 03:30:13','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(85,'FT-03 Angry Chicken Mac bowl','Draft','Main','Recipe',1.34319999999999995,27.77764987983069744,0.0,0.0,15.0,72.22235012016930966,1.34319999999999995,100.0,'','','','','1','ea',4.166647481974604438,NULL,NULL,'06/27/2025 01:49:59','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(86,'FT-01 Chicken Waffle Cone','Draft','Main','Recipe',0.00979999999999999969,0.0,0.0,0.0,14.0,100.0,0.00979999999999999969,100.0,'1','Days','','','1','ea',0.0,NULL,NULL,'06/27/2025 01:26:04','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(87,'SL-01 Chicken Caesar Salad','Draft','Salads','Recipe',18.37419999999999831,32.78574900793687875,0.0,0.0,24.98999999999999844,67.21425099206311415,18.37419999999999831,100.0,'1','Days','','','1','each',4.917862351190532166,NULL,NULL,'06/27/2025 00:14:04','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(88,'S-04 Fish Sando','Draft','Main','Recipe',3.247900000000000454,25.86659759616909326,0.0,0.0,14.0,74.13340240383089962,3.247900000000000454,100.0,'1','Days','','','1','ea',3.621323663463673182,NULL,NULL,'06/26/2025 23:50:29','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(89,'FC-02 Leg Quarter','Draft','Main','Recipe',2.101799999999999891,15.15765358361923277,0.0,0.0,15.0,84.84234641638077789,2.101799999999999891,100.0,'1','Days','','','1','ea',2.273648037542884914,NULL,NULL,'06/26/2025 23:45:23','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(90,'FC-01 Thicc''n Tenders','Draft','Main','Recipe',0.469299999999999995,28.48052560742994643,0.0,0.0,15.0,71.51947439257004647,0.469299999999999995,100.0,'1','Days','','','1','ea',4.272078841114492321,NULL,NULL,'06/26/2025 23:35:48','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(91,'Fried Chicken Tender','Draft','Main','PrepRecipe',0.95069999999999999,30.49525669643005799,0.0,0.0,0.0,0.0,0.95069999999999999,100.0,'1','Days','1','ea','1','ea',1.219810267857202257,NULL,NULL,'06/26/2025 20:56:56','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(92,'FC-04 Fried Chicken Tender','Draft','Main','Recipe',1.022999999999999909,31.79793526785863377,0.0,0.0,4.0,68.20206473214136622,1.022999999999999909,100.0,'','','','','1','ea',1.271917410714345387,NULL,NULL,'06/26/2025 20:49:51','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(93,'CHilli Oil - Hot Fat','Draft','Ingredient','PrepRecipe',40.4391999999999996,0.0,0.0,0.0,0.0,0.0,40.4391999999999996,100.0,'1','Months','3','gal','','',13.09464943999999953,NULL,NULL,'06/26/2025 18:44:02','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(94,'S-03 Plain Jane Sandwich','Draft','Main','Recipe',2.296700000000000408,28.74156227634576055,0.0,0.0,12.0,71.25843772365423944,2.296700000000000408,100.0,'','','','','1','ea',3.448987473161491568,NULL,NULL,'06/24/2025 04:52:19','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(95,'S-01 OG Nashville Chicken','Draft','Main','Recipe',2.568500000000000227,26.70244471154324373,0.0,0.0,13.0,73.29755528845674916,2.568500000000000227,100.0,'','','','','1','ea',3.471317812500621879,NULL,NULL,'06/24/2025 04:43:53','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(96,'S-02 J-Blaze Chicken','Draft','Main','Recipe',3.256000000000000227,25.85850389328069809,0.0,0.0,13.0,74.14149610671930191,3.256000000000000227,100.0,'','','','','1','',3.361605506126490895,NULL,NULL,'06/24/2025 04:39:53','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(97,'24 Hour Chili Brined Chicken Thigh','Draft','Main','PrepRecipe',26.08999999999999986,200.8468052347959941,0.0,0.0,12.99000000000000021,12.99000000000000021,0.0,100.0,'3','days','4','each','1','each',0.0,'','','06/24/2025 04:30:14','2025-07-04 21:29:47','2025-07-06T19:53:31.269243');
INSERT INTO recipes VALUES(98,'DP- 05 Habanero Ranch','Draft','Sauces','Recipe',0.2819999999999999729,28.20312500003590018,0.0,0.0,1.0,71.79687499996410338,0.2819999999999999729,100.0,'3','Days','','','2','oz',0.1410156250001795009,NULL,NULL,'06/24/2025 04:27:41','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(99,'Nashville Hot Chicken','Complete','Main','Recipe',3.446500000000000342,19.32565996367759099,0.0,0.0,15.75,80.67434003632240547,3.446500000000000342,100.0,'2','weeks','','','1','ea',3.04379144427922066,NULL,NULL,'06/22/2025 20:58:17','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(100,'Comeback Sauce - Updated 2025','Draft','Sauces','PrepRecipe',51.91999999999999459,0.0,0.0,0.0,0.0,0.0,0.0,100.0,'7','Days','7.5','quart','','',4.941990740746880383,NULL,NULL,'06/21/2025 21:30:15','2025-07-04 21:29:47','2025-07-06T19:53:31.269668');
INSERT INTO recipes VALUES(101,'Mac Sauce','Complete','Sauces','PrepRecipe',182.6161000000000172,0.0,0.0,0.0,0.0,0.0,182.6161000000000172,100.0,'7','days','3','gallon','','',18.36308440574522294,NULL,NULL,'06/21/2025 20:48:23','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(102,'Coleslaw','Draft','Ingredient','PrepRecipe',41.62000000000000455,0.0,0.0,0.0,0.0,0.0,0.0,100.0,'','','','','','',8.331221343957466274,NULL,NULL,'06/21/2025 20:32:11','2025-07-04 21:29:47','2025-07-06T19:53:31.270039');
INSERT INTO recipes VALUES(103,'Chicken Waffle Cone','Complete','Main','Recipe',3.70589999999999975,30.05884300595626968,0.0,0.0,12.0,69.94115699404372321,3.70589999999999975,100.0,'7','Days','','','1','ea',3.607061160714752468,NULL,NULL,'06/20/2025 17:51:08','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(104,'Charred Onion Ranch','Draft','Sauces','PrepRecipe',25.01679999999999637,6440.312500004173672,0.0,0.0,0.0,0.0,25.01679999999999637,100.0,'5','Days','10','lb','1','ea',6.440312500004173657,NULL,NULL,'06/20/2025 16:57:40','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(105,'Hot Honey - 2025','Draft','Sauces','PrepRecipe',26.08999999999999986,0.0,0.0,0.0,0.0,0.0,0.0,100.0,'7','Days','5','lb','1','each',1.308024763296836035,NULL,NULL,'06/20/2025 16:40:11','2025-07-04 21:29:47','2025-07-06T19:53:31.270372');
INSERT INTO recipes VALUES(106,'Hot Honey - portion','Complete','Sauces','Recipe',0.01420000000000000081,21.59600198968814056,0.0,0.0,1.0,78.40399801031185235,0.01420000000000000081,100.0,'7','Days','','','1','oz',0.2159600198968814056,NULL,NULL,'06/20/2025 16:36:58','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(107,'Hot Honey Sauce','Complete','Sauces','PrepRecipe',3.227000000000000313,0.0,0.0,0.0,0.0,0.0,3.227000000000000313,100.0,'7','Days','8','lb','','',1.727680159175051245,NULL,NULL,'06/20/2025 16:36:07','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(108,'Kale - Chopped','Complete','Ingredient','PrepRecipe',23.60800000000000054,0.0,0.0,0.0,0.0,0.0,23.60800000000000054,100.0,'2','Days','20','lb','','',1.189200000000000034,NULL,NULL,'06/20/2025 16:28:16','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(109,'Lemon Pepper Sauce - Portion','Complete','Sauces','Recipe',0.1466999999999999971,14.66666666666669983,0.0,0.0,1.0,85.33333333333330017,0.1466999999999999971,100.0,'','','','','1','ea',0.1466666666666670005,NULL,NULL,'06/20/2025 16:13:26','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(110,'Alabama White BBQ','Draft','Sauces','PrepRecipe',8.156299999999999884,0.0,0.0,0.0,0.0,0.0,8.156299999999999884,100.0,'7','Days','3','quart','','',3.360270833337297259,NULL,NULL,'06/19/2025 20:14:45','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(111,'Shredded Carrots','Complete','','PrepRecipe',4.700000000000000177,52.6666666666666714,0.0,0.0,0.0,0.0,4.700000000000000177,100.0,'','','10','lb','1','ea',0.7900000000000000355,NULL,NULL,'04/21/2025 07:08:06','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(112,'Shredded Cabbage','Complete','Sides','PrepRecipe',8.839999999999999858,0.0,0.0,0.0,0.0,0.0,8.839999999999999858,100.0,'','','10','lb','','',1.526000000000000023,NULL,NULL,'04/21/2025 07:08:06','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(113,'Comeback Sauce - Portion','Complete','Sauces','Recipe',0.0,30.29212962966800049,0.0,0.0,1.0,69.70787037033198885,0.0,100.0,'','','','','1','ea',0.3029212962966800205,NULL,NULL,'04/01/2025 19:00:39','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(114,'Hot Honey Chicken Wings','Complete','Main','Recipe',1.777500000000000079,17.43687737357850054,0.0,0.0,13.0,82.56312262642150302,1.777500000000000079,100.0,'','','','','1','each',2.266794058565205105,NULL,NULL,'04/01/2025 18:38:46','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(115,'Chicken Wings','Complete','Main','Recipe',1.74900000000000011,18.34874018771442294,0.0,0.0,10.0,81.65125981228558771,1.74900000000000011,100.0,'','','','','1','each',1.834874018771442294,NULL,NULL,'04/01/2025 18:37:34','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(116,'Buffalo Sauce - portion','Complete','Sauces','Recipe',0.347700000000000009,34.76562500004419576,0.0,0.0,1.0,65.23437499995580424,0.347700000000000009,100.0,'','','','','1','ea',0.3476562500004419797,NULL,NULL,'04/01/2025 18:23:48','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(117,'Hot Fish','Complete','Main','Recipe',3.673000000000000042,26.08554437527064706,0.0,0.0,16.0,73.91445562472935648,3.673000000000000042,100.0,'','','','','1','ea',4.173687100043303566,NULL,NULL,'04/01/2025 18:16:49','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(118,'BBQ Sauce Chicken Wings','Complete','Main','Recipe',2.283400000000000318,18.84278091363249529,0.0,0.0,13.0,81.15721908636750471,2.283400000000000318,100.0,'','','','','1','each',2.449561518772224389,NULL,NULL,'04/01/2025 17:45:40','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(119,'Buffalo Chicken Wings','Complete','Main','Recipe',2.444300000000000139,19.46297322132558704,0.0,0.0,13.0,80.53702677867443072,2.444300000000000139,100.0,'','','','','1','each',2.530186518772326031,NULL,NULL,'04/01/2025 17:38:40','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(120,'Lemon Pepper Chicken Wings','Complete','Main','Recipe',1.859000000000000208,14.96056937516494223,0.0,0.0,13.0,85.03943062483506309,1.859000000000000208,100.0,'','','','','1','each',1.944874018771442393,NULL,NULL,'04/01/2025 17:38:04','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(121,'Mac & Cheese','Complete','Sides','Recipe',0.6643000000000000015,18.9497138767953821,0.0,0.0,5.0,81.05028612320461435,0.6643000000000000015,100.0,'5','Days','','','1','ea',0.947485693839769105,NULL,NULL,'04/01/2025 17:07:26','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(122,'Collard Greens - Side Portion','Complete','Sides','Recipe',0.02359999999999999946,4.320812827691685953,0.0,0.0,5.0,95.6791871723083175,0.02359999999999999946,100.0,'5','Days','','','1','ea',0.2160406413845842866,NULL,NULL,'04/01/2025 17:04:34','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(123,'Collard Greens Recipe','Complete','Sides','PrepRecipe',15.03570000000000207,380.2315288368683355,0.0,0.0,0.0,0.0,15.03570000000000207,100.0,'5','Days','22','qt','1','ea',0.8641625655383371463,NULL,NULL,'04/01/2025 17:03:48','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(124,'Loaded Fries','Complete','Main','Recipe',3.212099999999999956,20.68566678378540758,0.0,0.0,12.0,79.31433321621459242,3.212099999999999956,100.0,'','','','','1','',2.482280014054249139,NULL,NULL,'02/18/2025 06:00:02','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(125,'Hot Fat','Complete','Ingredient','PrepRecipe',34.61339999999999862,0.0,0.0,0.0,0.0,0.0,34.61339999999999862,100.0,'1','Months','3','gal','','',11.53778441800000109,NULL,NULL,'02/18/2025 05:44:45','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(126,'Clucking Spice (Seasoning Blend)','Complete','Ingredient','PrepRecipe',16.7626000000000026,0.0,0.0,0.0,0.0,0.0,16.7626000000000026,100.0,'1','Months','106','gram','','',0.161610659575471688,NULL,NULL,'02/18/2025 05:40:43','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(127,'Onion Ranch','Complete','Sauces','PrepRecipe',26.4336999999999982,0.0,0.0,0.0,0.0,0.0,26.4336999999999982,100.0,'2','Days','10','qt','','',2.33183273809556102,NULL,NULL,'02/18/2025 05:23:48','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(128,'Comeback sauce','Complete','Sauces','PrepRecipe',0.05539999999999999786,0.0,0.0,0.0,0.0,0.0,0.05539999999999999786,100.0,'7','Days','7.5','quart','','',4.846740740746880327,NULL,NULL,'02/04/2025 21:13:51','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(129,'Plain Jane Sandwich','Complete','Main','Recipe',3.353299999999999948,20.94779291342522854,0.0,0.0,15.0,79.05220708657478213,3.353299999999999948,100.0,'7','','','','1','ea',3.142168937013784191,NULL,NULL,'02/04/2025 19:10:19','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(130,'Kale Kimchi - Side Portion','Complete','Sides','Recipe',0.4263000000000000122,7.940020833336689953,0.0,0.0,5.0,92.05997916666331094,0.4263000000000000122,100.0,'','','','','1','ea',0.397001041666834531,NULL,NULL,'02/04/2025 18:56:13','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(131,'Pickled Shallot','Complete','Toppings','PrepRecipe',150.984199999999987,0.0,0.0,0.0,0.0,0.0,150.984199999999987,100.0,'2','weeks','4','gallon','','',39.64916666666881895,NULL,NULL,'02/04/2025 16:21:26','2025-07-04 21:29:47','2025-07-06 05:00:58');
INSERT INTO recipes VALUES(132,'Tenders','Complete','Main','Recipe',0.978199999999999959,31.6426562500000017,0.0,0.0,4.0,68.35734374999999829,0.978199999999999959,100.0,'','','','','1','each',1.265706250000000032,NULL,NULL,'06/29/2024 18:01:55','2025-07-04 21:29:47','2025-07-06 05:00:58');
CREATE TABLE recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient_id INTEGER,
                ingredient_name TEXT,
                ingredient_type TEXT DEFAULT 'Product',
                quantity REAL,
                unit_of_measure TEXT,
                cost REAL DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, canonical_quantity DECIMAL(10,4), canonical_unit TEXT, conversion_status TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id),
                FOREIGN KEY (ingredient_id) REFERENCES inventory (id)
            );
INSERT INTO recipe_ingredients VALUES(295,111,25,'Produce, Carrots, Jumbo, Fresh','Product',10.0,'lb',4.700000000000000177,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(303,120,14,'Protein, Chicken, Wing','Product',10.0,'oz',1.087499999999999911,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(304,120,90,'Dry Goods, Bread, Texas Toast','Product',1.0,'each',0.2190000000000000002,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(305,120,652,'Dry Goods, Pickle, DIll, Slices','Product',1.0,'oz',0.001399999999999999986,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(306,120,474,'Dry Goods, Shortening, Pork Lard','Product',1.0,'oz',0.08540000000000000368,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(307,120,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',3.0,'oz',0.3557000000000000161,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(308,120,525,'Dry Food. Lemon Pepper','Product',1.5,'oz',0.1100000000000000005,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(309,72,433,'Hot Honey - 2025','PrepRecipe',2.0,'oz',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(310,72,891,'Non Con, Cup, 2oz, Clear Plastic','Product',1.0,'each',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(311,72,892,'Non Con, Lids, 1.5-2oz, Souffle, Clear','Product',1.0,'ea',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(312,96,183,'Protein, Chicken, Thighs','Product',8.0,'oz',1.879999999999999894,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(313,96,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',3.0,'oz',0.3557000000000000161,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(314,96,433,'Hot Honey - 2025','PrepRecipe',2.0,'oz',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(316,96,87,'Dry Goods, Bread,  Burger Bun','Product',1.0,'each',0.6199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(317,96,12,'Dry Goods, Oil, Canola, Clear, Frying','Product',2.0,'oz',0.1446000000000000063,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(318,95,183,'Protein, Chicken, Thighs','Product',7.0,'oz',1.645000000000000017,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(319,95,87,'Dry Goods, Bread,  Burger Bun','Product',1.0,'each',0.6199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(322,95,105,'Dairy,  Clarified Butter','Product',0.5,'oz',0.03830000000000000071,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(323,123,419,'Produce, Collard Green, Frozen, Chopped','Product',4.0,'lb',5.358900000000000218,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(324,123,39,'Protein, Pork Belly, Diced, Hickory Smoked','Product',10.0,'gram',0.0979000000000000009,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(325,123,448,'Produce, Onions, Yellow','Product',1.0,'lb',0.3990000000000000213,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(326,123,638,'Dry Goods, Chipotle Peppers, Can','Product',14.0,'oz',2.975000000000000088,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(327,123,551,'Water, Tap','Product',4.0,'quart',0.9375,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(328,123,175,'Dry Goods, Chicken Base, Paste','Product',15.0,'oz',4.0376000000000003,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(329,123,105,'Dairy,  Clarified Butter','Product',1.0,'lb',1.225500000000000033,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(330,123,825,'Dry Goods, Sugar, White','Product',2.0,'cup',0.004300000000000000002,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(334,112,610,'Produce, CABBAGE GREEN SHREDDED','Product',10.0,'lb',8.839999999999999858,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(335,68,692,'Dry Goods, Crackers, Ritz','Product',1.0,'lb',5.27880000000000038,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(336,124,178,'Protein, Chicken, Tenders','Product',4.0,'oz',0.714999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(337,124,138,'Dairy, Cheese Sauce, Loaf, American','Product',4.0,'oz',1.199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(339,124,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',2.0,'oz',0.2371000000000000051,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(341,99,183,'Protein, Chicken, Thighs','Product',7.0,'oz',1.645000000000000017,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(342,99,90,'Dry Goods, Bread, Texas Toast','Product',2.0,'each',0.4380000000000000004,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(345,99,105,'Dairy,  Clarified Butter','Product',0.5,'oz',0.03830000000000000071,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(349,69,138,'Dairy, Cheese Sauce, Loaf, American','Product',4.0,'oz',1.199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(353,103,603,'Dry Goods, Pasta, Cavatappi','Product',4.0,'oz',0.4429000000000000158,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(354,103,259,'Dairy, Cream, Heavy','Product',2.0,'ml',0.01140000000000000041,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(355,103,138,'Dairy, Cheese Sauce, Loaf, American','Product',5.0,'oz',1.5,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(356,103,178,'Protein, Chicken, Tenders','Product',4.0,'oz',0.714999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(359,103,415,'Produce, Onions, Green','UOM not available',1.0,'each',0.7900000000000000355,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(360,103,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',2.0,'oz',0.2371000000000000051,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(361,103,893,'Dry Goods, Waffle Cone','Product',1.0,'each',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(370,87,627,'Produce, Lettuce, Romaine','Product',4.0,'oz',17.60000000000000143,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(372,87,263,'Dry Goods, Croutons, Homestyle','Product',2.0,'oz',0.3313999999999999723,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(373,87,197,'Dairy, Chesse, Parmesan, Grated','Product',2.0,'oz',0.1971999999999999864,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(374,87,285,'Dry Goods, Caesar Dressing','Product',4.0,'oz',0.2361000000000000043,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(375,110,510,'Dry Goods, Mayonnaise, Heavy','Product',8.0,'cup',6.474999999999999645,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(376,110,862,'Produce, VINEGAR APPLE CIDER SPW LN','Product',2.0,'cup',1.620000000000000106,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(377,110,894,'Worcestershire Sauce','Product',2.0,'ml',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(378,110,147,'Dry Good,  Cayenne Pepper, Spice','Product',2.0,'ml',0.01870000000000000135,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(379,110,890,'Dry Goods, Black Pepper, Ground','Product',2.0,'ml',0.04259999999999999898,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(380,79,138,'Mac Sauce - Modified 2025','PrepRecipe',50.0,'oz',417.2637500000000727,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(381,79,603,'Dry Goods, Pasta, Cavatappi','Product',9.0,'lb',15.94350000000000022,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(383,75,891,'Non Con, Cup, 2oz, Clear Plastic','Product',1.0,'each',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(384,75,892,'Non Con, Lids, 1.5-2oz, Souffle, Clear','Product',1.0,'ea',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(385,67,14,'Protein, Chicken, Wing','Product',10.0,'oz',1.087499999999999911,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(386,67,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',1.0,'oz',0.1185999999999999971,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(387,67,12,'Dry Goods, Oil, Canola, Clear, Frying','Product',2.0,'oz',0.1446000000000000063,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(388,67,529,'Dairy, Milk, Whole','Product',2.0,'fl oz',0.08949999999999999623,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(389,74,NULL,'Comeback Sauce - Updated 2025','PrepRecipe',2.0,'oz',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(390,74,891,'Non Con, Cup, 2oz, Clear Plastic','Product',1.0,'each',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(391,74,892,'Non Con, Lids, 1.5-2oz, Souffle, Clear','Product',1.0,'ea',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(392,115,14,'Protein, Chicken, Wing','Product',10.0,'oz',1.087499999999999911,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(393,115,90,'Dry Goods, Bread, Texas Toast','Product',1.0,'each',0.2190000000000000002,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(394,115,652,'Dry Goods, Pickle, DIll, Slices','Product',1.0,'oz',0.001399999999999999986,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(395,115,474,'Dry Goods, Shortening, Pork Lard','Product',1.0,'oz',0.08540000000000000368,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(396,115,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',3.0,'oz',0.3557000000000000161,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(397,94,178,'Protein, Chicken, Tenders','Product',8.0,'oz',1.429999999999999938,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(398,94,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',2.0,'oz',0.2371000000000000051,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(399,94,87,'Dry Goods, Bread,  Burger Bun','Product',1.0,'ea',0.6199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(400,94,510,'Dry Goods, Mayonnaise, Heavy','Product',2.0,'oz',0.006799999999999999622,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(401,94,652,'Dry Goods, Pickle, DIll, Slices','Product',2.0,'oz',0.002799999999999999972,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(402,94,433,'Hot Honey - 2025','PrepRecipe',2.0,'oz',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(403,131,871,'Dry Goods, Vinegar, White','Product',2.0,'gallon',0.002200000000000000133,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(404,131,825,'Dry Goods, Sugar, White','Product',5.0,'lb',4.881999999999999674,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(405,131,629,'Produce, Shallots, Peeled, Fresh','Product',20.0,'lb',146.0999999999999944,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(406,70,371,'Frozen, Potato, French Fries, Frozen','PrepRecipe',5.0,'oz',0.4138000000000000011,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(407,104,871,'Dry Goods, Vinegar, White','Product',3.0,'qt',3.180000000000000159,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(408,104,8,'Dairy, Egg','Product',40.0,'each',15.77779999999999916,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(409,104,561,'Dry Goods, Oil, Canola, Salad -v','Product',3.0,'gal',0.008000000000000000166,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(410,104,890,'Dry Goods, Black Pepper, Ground','Product',3.0,'cup',0.06389999999999999847,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(411,104,711,'Dry Goods, Salt, Kosher','Product',3.0,'cup',0.00209999999999999987,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(412,104,448,'Produce, Onions, Yellow','Product',15.0,'lb',5.985000000000000319,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(413,127,448,'Produce, Onions, Yellow','Product',5.0,'lb',1.995000000000000106,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(414,127,8,'Dairy, Egg','Product',40.0,'each',15.77779999999999916,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(415,127,871,'Dry Goods, Vinegar, White','Product',3.0,'qt',3.180000000000000159,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(416,127,890,'Dry Goods, Black Pepper, Ground','Product',3.0,'oz',1.810100000000000042,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(417,127,561,'Dry Goods, Oil, Canola, Salad','Product',3.0,'lb',3.612000000000000099,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(418,127,711,'Dry Goods, Salt, Kosher','Product',3.0,'oz',0.05879999999999999811,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(419,73,291,'Dry Goods, Dressing, Honey Mustard','Product',2.0,'fl oz',0.4210999999999999743,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(420,73,891,'Non Con, Cup, 2oz, Clear Plastic','Product',1.0,'each',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(421,73,892,'Non Con, Lids, 1.5-2oz, Souffle, Clear','Product',1.0,'ea',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(422,121,138,'Mac Sauce','PrepRecipe',2.0,'oz',121.7440666666666828,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(423,121,603,'Dry Goods, Pasta, Cavatappi','Product',6.0,'oz',0.6643000000000000015,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(426,116,724,'Dry Goods, Sauce, Buffalo Wing Red Hot','Product',2.0,'fl oz',0.347700000000000009,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(427,80,138,'Mac Sauce - Modified 2025','PrepRecipe',3.0,'oz',25.03582500000000267,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(428,80,603,'Dry Goods, Pasta, Cavatappi','Product',5.0,'oz',0.553599999999999981,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(429,132,178,'Protein, Chicken, Tenders','Product',4.0,'oz',0.714999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(430,132,474,'Dry Goods, Shortening, Pork Lard','Product',1.0,'oz',0.08540000000000000368,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(431,132,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',1.5,'oz',0.1778000000000000136,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(432,88,373,'Seafood, Cod, Battered, Wedges, Frozen','Product',4.0,'oz',2.473700000000000009,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(433,88,87,'Dry Goods, Bread,  Burger Bun','Product',1.0,'ea',0.6199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(434,88,510,'Dry Goods, Mayonnaise, Heavy','Product',2.0,'oz',0.006799999999999999622,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(435,88,652,'Dry Goods, Pickle, DIll, Slices','Product',2.0,'oz',0.002799999999999999972,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(436,88,12,'Dry Goods, Oil, Canola, Clear, Frying','Product',2.0,'oz',0.1446000000000000063,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(437,76,39,'Frozen, Corn Rib, Hickory Smoked','Product',6.0,'oz',1.665699999999999959,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(438,76,12,'Dry Goods, Oil, Canola, Clear, Frying','Product',1.0,'oz',0.07230000000000000315,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(439,98,286,'Dry Goods, Ranch Dressing, with Jalapeno','Product',2.0,'fl oz',0.2819999999999999729,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(440,101,529,'Dairy, Milk, Whole','Product',2.0,'gallon',0.003000000000000000062,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(441,101,259,'Dairy, Cream, Heavy','Product',2.0,'qt',10.83000000000000007,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(442,101,711,'Dry Goods, Salt, Kosher','Product',170.0,'gram',0.1175999999999999963,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(443,101,157,'Dairy, Cheese, Cheddar, Yellow Bar','Product',1240.0,'gram',9.048700000000000187,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(444,101,138,'Dairy, Cheese Sauce, Loaf, American','Product',680.0,'gram',7.195899999999999964,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(445,101,565,'Dry Goods, Olive and Truffle Oil','Product',86.0,'gram',155.4071000000000141,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(451,82,371,'Frozen, Potato, French Fries, Frozen','Product',5.0,'oz',0.4138000000000000011,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(452,82,711,'Dry Goods, Salt, Kosher','Product',0.5,'oz',0.00979999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(453,82,12,'Dry Goods, Oil, Canola, Clear, Frying','Product',0.5,'oz',0.03620000000000000301,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(454,92,178,'Protein, Chicken, Tenders','Product',4.0,'oz',0.714999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(455,92,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',1.0,'oz',0.1185999999999999971,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(456,92,12,'Dry Goods, Oil, Canola, Clear, Frying','Product',2.0,'oz',0.1446000000000000063,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(457,92,529,'Dairy, Milk, Whole','Product',1.0,'fl oz',0.04479999999999999955,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(458,93,474,'Dry Goods, Shortening, Pork Lard','Product',9600.0,'gram',28.90630000000000165,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(459,93,599,'Dry Goods,  Spice, Paprika, Powder - Spanish','Product',400.0,'gram',4.224099999999999966,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(460,93,792,'Dry Goods, Spice, Cayenne Pepper, Ground','Product',800.0,'gram',7.308799999999999742,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(463,85,138,'Mac Sauce - Modified 2025','PrepRecipe',4.0,'fl oz',33.38110000000000355,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(464,85,603,'Dry Goods, Pasta, Cavatappi','Product',6.0,'oz',0.6643000000000000015,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(465,119,14,'Protein, Chicken, Wing','Product',10.0,'oz',1.087499999999999911,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(466,119,90,'Dry Goods, Bread, Texas Toast','Product',1.0,'each',0.2190000000000000002,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(467,119,652,'Dry Goods, Pickle, DIll, Slices','Product',1.0,'oz',0.001399999999999999986,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(468,119,474,'Dry Goods, Shortening, Pork Lard','Product',1.0,'oz',0.08540000000000000368,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(469,119,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',3.0,'oz',0.3557000000000000161,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(470,119,724,'Dry Goods, Sauce, Buffalo Wing Red Hot','Product',4.0,'fl oz',0.6953000000000000291,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(471,126,381,'Dry Goods, Spice, Ghost Pepper','Product',120.0,'gram',15.8468,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(472,126,147,'Dry Good,  Cayenne Pepper, Spice','Product',46.0,'gram',0.4299999999999999934,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(473,126,599,'Dry Goods,  Spice, Paprika, Powder','Product',46.0,'gram',0.4858000000000000095,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(474,117,87,'Dry Goods, Bread,  Burger Bun','Product',1.0,'ea',0.6199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(475,117,5,'Protein, Catfish, Fillet, Fresh','Product',7.0,'oz',2.813099999999999934,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(476,117,510,'Dry Goods, MAYONNAISE  HVY PLST SHLF','Product',2.0,'fl oz',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(477,117,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',2.0,'oz',0.2371000000000000051,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(478,117,652,'Dry Goods, Pickle, DIll, Slices','Product',2.0,'oz',0.002799999999999999972,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(479,91,178,'Protein, Chicken, Tenders','Product',4.0,'oz',0.714999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(480,91,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',1.0,'oz',0.1185999999999999971,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(481,91,529,'Dairy, Milk, Whole','Product',1.0,'fl oz',0.04479999999999999955,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(482,91,12,'Dry Goods, Oil, Canola, Clear, Frying','Product',1.0,'oz',0.07230000000000000315,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(483,71,286,'Dry Goods, Ranch Dressing, with Jalapeno','Product',2.0,'fl oz',0.2819999999999999729,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(484,71,891,'Non Con, Cup, 2oz, Clear Plastic','Product',1.0,'each',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(485,71,892,'Non Con, Lids, 1.5-2oz, Souffle, Clear','Product',1.0,'ea',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(486,108,779,'Produce, Kale, Green, Fresh, by Weight','Product',20.0,'lb',23.60800000000000054,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(487,109,525,'Dry Food. Lemon Pepper','Product',2.0,'oz',0.1466999999999999971,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(489,81,544,'Dry Goods, Ranch Dressing, Mix, Dry','Product',1.0,'oz',0.6995000000000000106,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(490,107,454,'Dry Goods, Sauce, Tomato Ketchup, Jug','Product',32.0,'oz',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(491,107,433,'Dry Goods, Honey, Natural','Product',48.0,'oz',1.877000000000000001,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(492,107,715,'Dry Goods, Sambal Chill Sauce (wt)','Product',32.0,'oz',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(493,107,738,'Dry Good.SAUCE SOY','Product',12.0,'fl oz',0.3458999999999999853,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(494,107,729,'Garlic Salt','Product',2.0,'oz',0.4052999999999999937,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(495,107,599,'Dry Goods, Onion Powder','Product',2.0,'oz',0.598799999999999999,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(497,78,105,'Dairy,  Clarified Butter','Product',2.0,'lb',2.451000000000000067,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(498,78,29,'Dry Goods, Flour, All Purpose, White','Product',2.0,'lb',4.716000000000000191,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(500,90,652,'Dry Goods, Pickle, DIll, Slices','Product',2.0,'oz',0.002799999999999999972,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(501,90,90,'Dry Goods, Bread, Texas Toast','Product',2.0,'each',0.4380000000000000004,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(502,84,622,'Kale - Chopped','PrepRecipe',20.0,'lb',27.28000000000000113,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(503,84,219,'Produce, Coleslaw Mix','Product',10.0,'lb',10.125,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(504,84,825,'Dry Goods, Sugar, White','Product',7.0,'lb',6.83480000000000043,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(505,84,871,'Dry Goods, Vinegar, White','Product',2.0,'qt',2.120000000000000106,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(506,84,715,'Dry Goods, Sauce, Chile Sambal','Product',3.0,'qt',18.48000000000000042,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(507,84,610,'Shredded Carrots','PrepRecipe',2.5,'lb',2.209999999999999965,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(508,77,529,'Dairy, Milk, Whole','Product',3.0,'gallon',0.004499999999999999659,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(509,77,259,'Dairy, Cream, Heavy','Product',3.0,'qt',16.24500000000000099,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(510,77,711,'Dry Goods, Salt, Kosher','Product',170.0,'gram',0.1175999999999999963,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(511,77,171,'Dairy, Cheese, Loaf, Pepper Jack','Product',1240.0,'gram',12.16510000000000069,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(513,128,510,'Dry Goods, Mayonnaise, Heavy','Product',3.0,'quart',0.01030000000000000012,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(514,128,549,'Dry Goods, Mustard, Creole','Product',3.0,'quart',0.01569999999999999867,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(515,128,715,'Dry Goods, Sauce, Chile Sambal','Product',1.5,'quart',0.00979999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(516,128,711,'Dry Goods, Salt, Kosher','Product',1.0,'oz',0.01959999999999999937,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(517,129,178,'Protein, Chicken, Tenders','Product',8.0,'oz',1.429999999999999938,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(518,129,87,'Dry Goods, Bread,  Burger Bun','Product',1.0,'ea',0.6199999999999999956,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(519,129,510,'Dry Goods, Mayonnaise, Heavy','UOM not available',1.0,'each',0.003399999999999999811,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(520,129,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',2.0,'oz',0.2371000000000000051,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(521,129,652,'Dry Goods, Pickle, DIll, Slices','Product',2.0,'oz',0.002799999999999999972,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(523,118,14,'Protein, Chicken, Wing','Product',10.0,'oz',1.087499999999999911,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(524,118,90,'Dry Goods, Bread, Texas Toast','Product',1.0,'each',0.2190000000000000002,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(525,118,652,'Dry Goods, Pickle, DIll, Slices','Product',1.0,'oz',0.001399999999999999986,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(526,118,474,'Dry Goods, Shortening, Pork Lard','Product',1.0,'oz',0.08540000000000000368,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(527,118,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',3.0,'oz',0.3557000000000000161,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(528,118,742,'Dry Goods, Sauce, BBQ','Product',4.0,'fl oz',0.5343999999999999862,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(529,114,14,'Protein, Chicken, Wing','Product',10.0,'oz',1.087499999999999911,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(530,114,90,'Dry Goods, Bread, Texas Toast','Product',1.0,'each',0.2190000000000000002,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(531,114,652,'Dry Goods, Pickle, DIll, Slices','Product',1.0,'oz',0.001399999999999999986,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(532,114,474,'Dry Goods, Shortening, Pork Lard','Product',1.0,'oz',0.08540000000000000368,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(533,114,475,'Dry Goods, Chicken  Breading, Lea Jane Recipe','Product',3.0,'oz',0.3557000000000000161,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(535,113,NULL,'Comeback sauce','PrepRecipe',2.0,'oz',0.01477333333333333276,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(536,86,893,'Dry Goods, Waffle Cone','Product',1.0,'ea',NULL,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(537,86,171,'Dairy, Cheese, Loaf, Pepper Jack','UOM not available',1.0,'each',0.00979999999999999969,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(538,125,474,'Dry Goods, Shortening, Pork Lard','Product',1920.0,'gram',5.781299999999999884,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(539,125,599,'Dry Goods,  Spice, Paprika, Powder','Product',1000.0,'gram',10.56020000000000003,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(540,125,792,'Dry Goods, Spice, Cayenne Pepper, Ground','Product',2000.0,'gram',18.27189999999999869,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(541,89,183,'Protein, Chicken, Thighs','Product',8.0,'oz',1.879999999999999894,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(542,89,90,'Dry Goods, Bread, Texas Toast','Product',1.0,'each',0.2190000000000000002,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(543,89,652,'Dry Goods, Pickle, DIll, Slices','Product',2.0,'oz',0.002799999999999999972,'2025-07-06 05:00:24',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(544,97,183,'Protein, Chicken, Thighs','Product',6.0,'oz',22.55999999999999873,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(545,97,711,'Dry Goods, Salt, Kosher','Product',0.5,'oz',0.4699999999999999734,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(546,97,105,'Dairy,  Clarified Butter','Product',0.5,'oz',3.060000000000000053,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(547,100,510,'Dry Goods, Mayonnaise, Heavy','Product',4.0,'oz',51.79999999999999716,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(548,100,454,'Dry Goods, Ketchup Packets','Product',1.0,'oz',0.02999999999999999889,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(549,100,894,'Worcestershire Sauce','Product',0.25,'oz',0.08999999999999999667,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(550,102,510,'Dry Goods, Mayonnaise, Heavy','Product',3.0,'oz',38.85000000000000142,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(551,102,871,'Dry Goods, Vinegar, White','Product',0.5,'oz',2.120000000000000106,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(552,102,829,'SUGAR EFG GRANULATED 403522','Product',0.5,'oz',0.6500000000000000222,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(553,105,433,'Dry Goods, Honey, Natural','Product',8.0,'oz',25.03000000000000113,'2025-07-07 00:53:31',NULL,NULL,NULL);
INSERT INTO recipe_ingredients VALUES(554,105,871,'Dry Goods, Vinegar, White','Product',0.25,'oz',1.060000000000000053,'2025-07-07 00:53:31',NULL,NULL,NULL);
CREATE TABLE menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                menu_group TEXT,
                item_description TEXT,
                recipe_id INTEGER,
                menu_price REAL DEFAULT 0,
                food_cost REAL DEFAULT 0,
                food_cost_percent REAL DEFAULT 0,
                gross_profit REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                serving_size TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, version_id INTEGER,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            );
INSERT INTO menu_items VALUES(85,'French Fries - Portion','Sides',NULL,70,5.0,0.5269794973544962291,10.53958994708992592,4.473020502645503882,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(86,'DP-05 Habanero Ranch','Sauces',NULL,71,1.0,0.310263250000358981,31.02632500003589655,0.6897367499996409635,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(87,'DP-04 Hot Honey','Sauces',NULL,72,1.0,0.1917350954121045114,19.17350954121044992,0.8082649045878954608,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(88,'DP-03 Honey Mustard','Sauces',NULL,73,1.0,0.4493257500005349848,44.9325750000534967,0.5506742499994650153,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(89,'DP-02 Comeback Sauce','Sauces',NULL,74,1.0,0.3371064212966800033,33.71064212966800256,0.6628935787033199966,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(90,'DP-01 Charred-Onion Ranch Dip','Sauces',NULL,75,1.0,0.833271062500521631,83.32710625005216797,0.1667289374994783691,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(91,'SD-04 Fried Corn Ribs','Sides',NULL,76,5.0,1.71781026785714297,34.35620535714286205,3.282189732142857252,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(92,'SD-03 LJ Mac','Sides',NULL,80,5.0,0.8934740190017190776,17.86948038003438199,4.106525980998281255,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(93,'SD-02 Extra-Crispy Fries with Ranch Powder','Sides',NULL,81,5.0,0.6263138168811237527,12.52627633762247505,4.373686183118875803,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(94,'SD-01 Kale & Cabbage Slaw','Sides',NULL,83,5.0,0.397001041666834531,7.940020833336689953,4.602998958333165191,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(106,'Nashville Hot Chicken','Main',NULL,99,15.75,3.04379144427922066,19.32565996367759099,12.70620855572077979,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(107,'Chicken Waffle Cone','Main',NULL,86,14.0,0.0,0.0,14.0,'Active',NULL,'2025-07-05 00:55:31','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(108,'Hot Honey - portion','Sauces',NULL,106,1.0,0.2159600198968814056,21.59600198968814056,0.7840399801031185945,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(109,'Lemon Pepper Sauce - Portion','Sauces',NULL,109,1.0,0.1466666666666670005,14.66666666666669983,0.8533333333333330551,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(110,'Comeback Sauce - Portion','Sauces',NULL,113,1.0,0.3029212962966800205,30.29212962966800049,0.6970787037033199241,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(111,'Hot Honey Chicken Wings','Main',NULL,114,13.0,2.266794058565205105,17.43687737357850054,10.7332059414347949,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(112,'Chicken Wings','Main',NULL,115,10.0,1.834874018771442294,18.34874018771442294,8.165125981228557705,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(113,'Buffalo Sauce - portion','Sauces',NULL,116,1.0,0.3476562500004419797,34.76562500004419576,0.6523437499995580203,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(114,'Hot Fish','Main',NULL,117,16.0,4.173687100043303566,26.08554437527064706,11.82631289995669733,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(115,'BBQ Sauce Chicken Wings','Main',NULL,118,13.0,2.449561518772224389,18.84278091363249529,10.55043848122777562,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(116,'Buffalo Chicken Wings','Main',NULL,119,13.0,2.530186518772326031,19.46297322132558704,10.46981348122767486,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(117,'Lemon Pepper Chicken Wings','Main',NULL,120,13.0,1.944874018771442393,14.96056937516494223,11.05512598122855827,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(118,'Mac & Cheese','Sides',NULL,121,5.0,0.947485693839769105,18.9497138767953821,4.052514306160230895,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(119,'Collard Greens - Side Portion','Sides',NULL,122,5.0,0.2160406413845842866,4.320812827691685953,4.783959358615415879,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(120,'Loaded Fries','Main',NULL,69,14.0,0.0,0.0,14.0,'Active',NULL,'2025-07-05 00:55:31','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(121,'Plain Jane Sandwich','Main',NULL,94,12.0,0.0,0.0,12.0,'Active',NULL,'2025-07-05 00:55:31','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(122,'Kale Kimchi - Side Portion','Sides',NULL,130,5.0,0.397001041666834531,7.940020833336689953,4.602998958333165191,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(123,'Tenders','Main',NULL,132,4.0,1.265706250000000032,31.6426562500000017,2.734293749999999968,'Active',NULL,'2025-07-05 00:55:31','2025-07-05 00:55:31',1);
INSERT INTO menu_items VALUES(124,'Thicc''n Tenders','Main',NULL,90,15.0,0.0,0.0,15.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(126,'Whole Wings','Main',NULL,67,14.0,0.0,0.0,14.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(127,'Fried Chicken Tender','Main',NULL,92,4.0,0.0,0.0,4.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(133,'Kale & Cabbage Slaw','Sides',NULL,83,5.0,0.0,0.0,5.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(134,'Extra-Crispy Fries','Sides',NULL,81,5.0,0.0,0.0,5.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(135,'LJ Mac','Sides',NULL,80,5.0,0.0,0.0,5.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(136,'Fried Corn Ribs','Sides',NULL,76,5.0,0.0,0.0,5.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(137,'Charred-Onion Ranch','Sauces',NULL,75,1.0,0.0,0.0,1.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(138,'Comeback Sauce','Sauces',NULL,74,1.0,0.0,0.0,1.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(139,'Honey Mustard','Sauces',NULL,73,1.0,0.0,0.0,1.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(140,'Hot Honey','Sauces',NULL,72,1.0,0.0,0.0,1.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(141,'Habanero Ranch','Sauces',NULL,71,1.0,0.0,0.0,1.0,'Active',NULL,'2025-07-05 03:35:23','2025-07-06 05:00:24',1);
INSERT INTO menu_items VALUES(142,'FC-03 Whole Wings','Main',NULL,67,115.1653999999999768,32.90439999999999542,28.57142857142857651,82.26099999999998146,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(143,'Ritz Crumble','Toppings',NULL,68,1.154650000000000177,0.3299000000000000266,28.57142857142856939,0.8247500000000000942,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(144,'FT-02 Loaded Fries','Main',NULL,69,105.9975000000000164,30.2850000000000037,28.57142857142856939,75.71250000000000569,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(145,'French Fries - Portion','Sides',NULL,70,18.55000000000000071,5.299999999999999823,28.57142857142856939,13.25,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(146,'DP-05 Habanero Ranch','Sauces',NULL,71,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(147,'DP-04 Hot Honey','Sauces',NULL,72,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(148,'DP-03 Honey Mustard','Sauces',NULL,73,188.6500000000000056,53.89999999999999858,28.57142857142856939,134.75,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(149,'DP-02 Comeback Sauce','Sauces',NULL,74,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(150,'DP-01 Charred-Onion Ranch Dip','Sauces',NULL,75,5.530000000000000248,1.580000000000000071,28.57142857142856939,3.950000000000000177,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(151,'SD-04 Fried Corn Ribs','Sides',NULL,76,2.917949999999999822,0.8336999999999999967,28.57142857142857651,2.084249999999999937,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(152,'Mac Sauce - Modified 2025','Sauces',NULL,77,19619.19610000000102,5605.484599999999773,28.57142857142856939,14013.71150000000125,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(153,'Roux recipe','Sauces',NULL,78,36.03249999999999887,10.29499999999999993,28.57142857142856939,25.73749999999999715,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(154,'LJ Mac','Sides',NULL,79,55.80225000000000079,15.94350000000000022,28.57142857142856939,39.85875000000000056,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(155,'SD-03 LJ Mac','Sides',NULL,80,31.00124999999999887,8.857499999999999929,28.57142857142856939,22.14374999999999716,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(156,'SD-02 Extra-Crispy Fries with Ranch Powder','Sides',NULL,81,20.99824999999999875,5.999499999999999388,28.57142857142856939,14.99874999999999937,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(157,'French Fries Recipe','Sides',NULL,82,2.008299999999999752,0.5737999999999999768,28.57142857142857651,1.434499999999999887,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(158,'SD-01 Kale & Cabbage Slaw','Sides',NULL,83,19.32280000000000086,5.520800000000000373,28.57142857142856939,13.80199999999999961,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(159,'Kale Kimchi Recipe','Sides',NULL,84,373.8385000000000104,106.8110000000000071,28.57142857142856939,267.0275000000000319,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(160,'FT-03 Angry Chicken Mac bowl','Main',NULL,85,59.53115000000000378,17.00890000000000057,28.57142857142856939,42.52224999999999966,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(161,'FT-01 Chicken Waffle Cone','Main',NULL,86,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(162,'SL-01 Chicken Caesar Salad','Salads',NULL,87,83.48234999999999673,23.85210000000000007,28.57142857142857651,59.63024999999999665,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(163,'S-04 Fish Sando','Main',NULL,88,82.41590000000000771,23.54740000000000322,28.57142857142857651,58.86850000000000449,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(164,'FC-02 Leg Quarter','Main',NULL,89,37.05380000000000251,10.58680000000000021,28.57142857142856939,26.4670000000000023,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(165,'FC-01 Thicc''n Tenders','Main',NULL,90,67.45795000000001095,19.27370000000000161,28.57142857142856939,48.1842500000000058,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(166,'Fried Chicken Tender','Main',NULL,91,54.81244999999999835,15.66069999999999851,28.57142857142856939,39.15174999999999983,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(167,'FC-04 Fried Chicken Tender','Main',NULL,92,57.73039999999999595,16.49439999999999885,28.57142857142856939,41.2359999999999971,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(168,'CHilli Oil - Hot Fat','Ingredient',NULL,93,45890.88000000000466,13111.68000000000029,28.57142857142856939,32779.20000000000437,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(169,'S-03 Plain Jane Sandwich','Main',NULL,94,138.5789999999999793,39.59399999999999409,28.57142857142856939,98.9849999999999853,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(170,'S-01 OG Nashville Chicken','Main',NULL,95,109.3634500000000002,31.24670000000000058,28.57142857142856939,78.11674999999999614,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(171,'S-02 J-Blaze Chicken','Main',NULL,96,39.34315000000000139,11.2408999999999999,28.57142857142856939,28.1022500000000015,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(172,'24 Hour Chili Brined Chicken Thigh','Uncategorized',NULL,97,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(173,'DP- 05 Habanero Ranch','Sauces',NULL,98,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(175,'Comeback Sauce - Updated 2025','Sauces',NULL,100,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(176,'Mac Sauce','Sauces',NULL,101,8144.148600000000442,2326.899600000000191,28.57142857142856939,5817.248999999999797,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(177,'Coleslaw','Ingredient',NULL,102,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(178,'Chicken Waffle Cone','Main',NULL,103,189.3674999999999783,54.10499999999999688,28.57142857142857651,135.2624999999999887,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(179,'Charred Onion Ranch','Sauces',NULL,104,47.56430000000000291,13.58980000000000032,28.57142857142856939,33.97450000000000613,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(180,'Hot Honey - 2025','Sauces',NULL,105,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(181,'Hot Honey - portion','Sauces',NULL,106,155.75,44.5,28.57142857142856939,111.25,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(182,'Hot Honey Sauce','Sauces',NULL,107,137.4285499999999729,39.26529999999999631,28.57142857142857651,98.1632499999999765,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(183,'Kale - Chopped','Ingredient',NULL,108,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(184,'Lemon Pepper Sauce - Portion','Sauces',NULL,109,0.0,0.0,0.0,0.0,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(185,'Alabama White BBQ','Sauces',NULL,110,357.5600000000000591,102.1600000000000109,28.57142857142856939,255.4000000000000342,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(186,'Shredded Carrots','Uncategorized',NULL,111,225.0499999999999829,64.29999999999999716,28.57142857142856939,160.75,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(187,'Shredded Cabbage','Sides',NULL,112,38.64594999999999914,11.04170000000000051,28.57142857142857651,27.60425000000000039,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(188,'Comeback Sauce - Portion','Sauces',NULL,113,115.2199999999999989,32.9200000000000017,28.57142857142857651,82.29999999999999716,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(189,'Hot Honey Chicken Wings','Main',NULL,114,415.8126000000000318,118.8036000000000029,28.57142857142856939,297.0090000000000145,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(190,'Chicken Wings','Main',NULL,115,104.3126000000000033,29.80359999999999943,28.57142857142856939,74.50900000000000034,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(191,'Buffalo Sauce - portion','Sauces',NULL,116,155.75,44.5,28.57142857142856939,111.25,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(192,'Hot Fish','Main',NULL,117,317.5689999999999599,90.73399999999999465,28.57142857142857651,226.8349999999999795,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(193,'BBQ Sauce Chicken Wings','Main',NULL,118,106.9204500000000024,30.54870000000000018,28.57142857142856939,76.3717500000000058,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(194,'Buffalo Chicken Wings','Main',NULL,119,415.8126000000000318,118.8036000000000029,28.57142857142856939,297.0090000000000145,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(195,'Lemon Pepper Chicken Wings','Main',NULL,120,104.3126000000000033,29.80359999999999943,28.57142857142856939,74.50900000000000034,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(196,'Mac & Cheese','Sides',NULL,121,152.4215000000000088,43.54899999999999949,28.57142857142856939,108.8725000000000022,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(197,'Collard Greens - Side Portion','Sides',NULL,122,37.51230000000000331,10.71780000000000043,28.57142857142856939,26.79450000000000288,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(198,'Collard Greens Recipe','Sides',NULL,123,140.6909000000000276,40.19740000000000891,28.57142857142856939,100.4935000000000116,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(199,'Loaded Fries','Main',NULL,124,113.2565000000000026,32.35900000000000176,28.57142857142856939,80.89750000000000796,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(200,'Hot Fat','Ingredient',NULL,125,9178.175999999999476,2622.335999999999786,28.57142857142856939,6555.840000000000145,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(201,'Clucking Spice (Seasoning Blend)','Ingredient',NULL,126,1572.375,449.25,28.57142857142856939,1123.125,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(202,'Onion Ranch','Sauces',NULL,127,60.30954999999998734,17.2312999999999974,28.57142857142857651,43.07824999999998993,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(203,'Comeback sauce','Sauces',NULL,128,395.8454499999999711,113.0986999999999938,28.57142857142856939,282.7467499999999631,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(204,'Plain Jane Sandwich','Main',NULL,129,104.3839999999999862,29.82399999999999807,28.57142857142857651,74.55999999999998807,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(205,'Kale Kimchi - Side Portion','Sides',NULL,130,19.32280000000000086,5.520800000000000373,28.57142857142856939,13.80199999999999961,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(206,'Pickled Shallot','Toppings',NULL,131,455.4654999999999063,130.1329999999999813,28.57142857142857651,325.332499999999925,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(207,'Tenders','Main',NULL,132,39.09954999999999359,11.17129999999999868,28.57142857142857651,27.92824999999999491,'Active',NULL,'2025-07-05 21:00:54','2025-07-05 21:00:54',0);
INSERT INTO menu_items VALUES(208,' S-01 OG Nashville Chicken','Sandwiches','',95,13.0,2.568500000000000227,19.75769230769230944,10.43149999999999978,'Inactive','1 each','2025-07-07 02:23:24','2025-07-07 02:23:24',2);
CREATE TABLE vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL UNIQUE,
                contact_info TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO vendors VALUES(1,'MJ Sweet and Cake',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(2,'La Reyna Tortilla',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(3,'Flower & Cream',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(4,'Jorge Garza',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(5,'ACE MART',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(6,'Pepsi Cups',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(7,'Chefs Produce',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(8,'G & A',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(9,'ALVARADO''S',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(10,'FAM Group',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(11,'Pereyda Produce',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(12,'COMMON BOND BISTRO & BAKERY',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(13,'US Foods',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(14,'CB Commissary LLC',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(15,'JAKES, INC.',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(16,'JAKE''S, INC.',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(17,'RESTAURANT DEPOT',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(18,'Sellers Bros',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(19,'GORDON FOOD SERVICES',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(20,'Lovett Commercial',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(21,'Buckhead Meat & Seafood OF HOUSTON',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(22,'FIESTA MART',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(23,'TEXAS FINESS',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(24,'ALTAMIRA LTD.',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
INSERT INTO vendors VALUES(25,'Sysco Houston',NULL,NULL,NULL,NULL,1,'2025-07-04 21:29:47');
CREATE TABLE vendor_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                vendor_id INTEGER NOT NULL,
                vendor_item_code TEXT,
                vendor_price REAL,
                last_purchased_date TEXT,
                last_purchased_price REAL,
                pack_size TEXT,
                unit_measure TEXT,
                is_primary BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id),
                UNIQUE(inventory_id, vendor_id, vendor_item_code)
            );
INSERT INTO vendor_products VALUES(1,5,21,'237552',6.429999999999999716,'3/13/2025',6.429999999999999716,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(2,8,4,'58897_XC9776450',71.0,'3/24/2025',71.0,'1 x 180','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(3,9,4,'58897_XC10484627',41.89000000000000056,'1/27/2025',41.89000000000000056,'24 x 16','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(4,10,4,'58897_XC11725426',43.5,'3/24/2025',43.5,'24 x 16','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(5,11,4,'58897_XC11546426',26.5,'2/25/2025',26.5,'1 x 24','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(6,12,4,'58897_XC11546428',40.5,'2/25/2025',40.5,'1 x 35','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(7,14,21,'1001997',1.739999999999999992,'7/1/2025',1.739999999999999992,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(8,24,4,'58897_XC11546427',25.75,'2/25/2025',25.75,'48 x 4','ct',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(9,25,4,'58897_XC5723334',23.5,'2/18/2025',23.5,'1 x 50','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(10,29,4,'58897_XC11131128',11.78999999999999915,'1/6/2025',11.78999999999999915,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(11,39,25,'7228367',71.06999999999999317,'5/23/2025',71.06999999999999317,'4 x 4','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(12,47,17,'70247159793',13.40000000000000035,'5/13/2025',13.40000000000000035,'1 x 3','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(13,48,17,'18692',12.17999999999999972,'4/22/2025',12.17999999999999972,'1 x 3','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(14,60,1,'101841_XC7523071',20.0,'6/24/2025',20.0,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(15,71,4,'58897_XC5705377',1.489999999999999992,'3/24/2025',1.489999999999999992,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(16,74,1,'101841_XC7809704',4.0,'12/15/2022',4.0,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(17,84,1,'101841_XC10776471',32.0,'6/24/2025',32.0,'1 x 8','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(18,86,14,'486',0.5699999999999999512,'6/3/2025',0.5699999999999999512,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(19,87,12,'90880_XC12350157',0.6199999999999999956,'5/15/2025',0.6199999999999999956,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(20,88,14,'483',1.590000000000000079,'6/3/2025',1.590000000000000079,'12 x 2','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(21,89,14,'487',0.6199999999999999956,'7/1/2025',0.6199999999999999956,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(22,90,14,'936',2.189999999999999947,'7/1/2025',2.189999999999999947,'10 x 1','loaf',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(23,91,12,'90880_XC12350158',2.189999999999999947,'5/15/2025',2.189999999999999947,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(24,92,14,'2537',1.060000000000000053,'6/3/2025',1.060000000000000053,'1 each','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(25,93,14,'2537T',1.060000000000000053,'5/20/2025',1.060000000000000053,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(26,102,16,'900006',34.1700000000000017,'5/1/2025',34.1700000000000017,'8 x 24','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(27,105,17,'15700227220',24.51000000000000156,'5/13/2025',24.51000000000000156,'4 x 5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(28,112,15,'BUTR28',102.9500000000000028,'6/9/2025',102.9500000000000028,'4 x 5','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(29,131,4,'58897_XC35013',0.7900000000000000355,'2/25/2025',0.7900000000000000355,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(30,138,4,'58897_XC10619296',144.0,'1/7/2025',144.0,'6 x 5','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(31,140,4,'58897_XC10619293',41.5,'2/25/2025',41.5,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(32,141,4,'58897_XC11813053',41.5,'3/24/2025',41.5,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(33,142,4,'58897_XC11484060',41.5,'3/10/2025',41.5,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(34,143,4,'58897_XC10484628',32.5,'2/25/2025',32.5,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(35,145,21,'7237552',6.429999999999999716,'7/1/2025',6.429999999999999716,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(36,146,4,'58897_XC3682926',28.75,'2/18/2025',28.75,'18 x 1','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(37,147,4,'58897_XC6873465',4.240000000000000213,'2/11/2025',4.240000000000000213,'1 each','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(38,148,4,'58897_XC11813060',4.240000000000000213,'3/24/2025',4.240000000000000213,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(39,149,4,'58897_XC63226',1.790000000000000035,'2/18/2025',1.790000000000000035,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(40,153,16,'PR8153',10.00999999999999979,'6/2/2025',10.00999999999999979,'1 x 6','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(41,157,15,'PCH007',3.310000000000000053,'6/9/2025',3.310000000000000053,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(42,163,15,'NCHS64',4.150000000000000356,'5/20/2025',4.150000000000000356,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(43,165,13,'NCHS45',3.470000000000000195,'6/30/2025',3.470000000000000195,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(44,171,13,'JACK50',4.450000000000000177,'6/30/2025',4.450000000000000177,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(45,175,4,'58897_XC11270013',18.94999999999999929,'1/23/2025',18.94999999999999929,'1 x 4.4','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(46,178,21,'1002010',2.859999999999999876,'7/1/2025',2.859999999999999876,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(47,179,21,'1005246',4.009999999999999787,'7/1/2025',4.009999999999999787,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(48,183,13,'G20223',3.759999999999999787,'6/27/2025',3.759999999999999787,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(49,186,16,'CHIC22',1.989999999999999992,'4/11/2025',1.989999999999999992,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(50,192,17,'34500487757',110.0699999999999931,'4/29/2025',110.0699999999999931,'6 x 5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(51,194,17,'71505015875',17.76000000000000157,'4/29/2025',17.76000000000000157,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(52,195,17,'44310',18.78000000000000113,'4/22/2025',18.78000000000000113,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(53,197,17,'14726',31.55999999999999873,'5/28/2025',31.55999999999999873,'4 x 5','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(54,208,9,'165826_XC12097639',37.0,'4/22/2025',37.0,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(55,209,9,'165826_XC12097641',30.0,'4/22/2025',30.0,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(56,213,4,'58897_XC10447740',39.75,'3/15/2025',39.75,'24 x 500','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(57,214,17,'49000047790',41.10999999999999944,'4/2/2025',41.10999999999999944,'24 x 500','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(58,215,17,'49000046595',41.10999999999999944,'4/15/2025',41.10999999999999944,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(59,219,15,'PR9313',20.25,'5/20/2025',20.25,'4 x 5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(60,259,16,'MILK33',64.98000000000000397,'6/2/2025',64.98000000000000397,'12 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(61,261,17,'10031',50.4200000000000017,'4/22/2025',50.4200000000000017,'1 each','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(62,262,17,'41467000738',49.5,'5/13/2025',49.5,'12 x 1','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(63,263,17,'2061156',26.51000000000000156,'5/28/2025',26.51000000000000156,'4 x 2.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(64,284,4,'58897_XC9163168',1.489999999999999992,'2/18/2025',1.489999999999999992,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(65,285,17,'54565',30.21999999999999887,'5/28/2025',30.21999999999999887,'4 x 128','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(66,286,17,'41335351986',18.05000000000000071,'5/20/2025',18.05000000000000071,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(67,291,13,'333615',26.94999999999999929,'6/30/2025',26.94999999999999929,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(68,293,17,'41335086710',16.46000000000000085,'5/20/2025',16.46000000000000085,'1 each','jug',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(69,297,15,'CDK145',33.35999999999999944,'5/23/2025',33.35999999999999944,'24 x 12.5','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(70,299,15,'CDK149',33.35999999999999944,'3/11/2025',33.35999999999999944,'24 x 12','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(71,308,16,'CDK148',33.35999999999999944,'5/26/2025',33.35999999999999944,'24 x 12.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(72,311,13,'CDK146',33.97999999999999687,'6/30/2025',33.97999999999999687,'24 x 12.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(73,313,17,'78000082401',29.01999999999999958,'4/2/2025',29.01999999999999958,'24 x 1','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(74,314,17,'78000804676',14.58000000000000007,'4/29/2025',14.58000000000000007,'12 x 1','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(75,315,17,'440808',13.42999999999999972,'4/17/2025',13.42999999999999972,'24 x 1','pack',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(76,316,16,'BRD040',23.92999999999999972,'4/11/2025',23.92999999999999972,'7 x 32','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(77,317,17,'40900016084',65.12999999999999546,'4/1/2025',65.12999999999999546,'12 x 32','carton',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(78,318,4,'58897_XC11494749',0.6899999999999999467,'2/25/2025',0.6899999999999999467,'1 each','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(79,324,17,'51213',41.95000000000000285,'4/22/2025',41.95000000000000285,'1 x 180','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(80,331,15,'EGGS08',3.939999999999999947,'6/4/2025',3.939999999999999947,'1 x 15','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(81,335,13,'EGGS07',3.899999999999999912,'6/30/2025',3.899999999999999912,'12 x 1','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(82,341,4,'58897_XC10111214',144.0,'1/6/2025',144.0,'6 x 5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(83,342,4,'58897_XC10447737',144.0,'3/10/2025',144.0,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(84,345,9,'165826_XC12097645',36.0,'4/22/2025',36.0,'24 x 16','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(85,346,9,'165826_XC12097643',35.0,'4/22/2025',35.0,'24 x 16','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(86,347,4,'58897_XC10172096',39.75,'2/11/2025',39.75,'24 x 500','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(87,353,15,'FISH14',5.910000000000000142,'3/18/2025',5.910000000000000142,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(88,354,15,'FIS035',7.0,'5/20/2025',7.0,'1 x 10','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(89,355,16,'VFSH52',9.23000000000000042,'3/28/2025',9.23000000000000042,'1 x 10','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(90,360,15,'FLOR32',17.98000000000000042,'1/13/2025',17.98000000000000042,'1 x 25','bag',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(91,361,13,'FLOR33',10.33000000000000007,'6/30/2025',10.33000000000000007,'1 x 25','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(92,365,24,'7',551.509999999999991,'3/19/2025',551.509999999999991,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(93,366,4,'58897_XC11270014',43.5,'3/10/2025',43.5,'24 x 16','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(94,371,13,'FRY057',35.75,'7/2/2025',35.75,'6 x 4.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(95,373,17,'73538020154',39.5799999999999983,'5/20/2025',39.5799999999999983,'32 x 2','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(96,374,21,'41112040',4.0,'7/1/2025',4.0,'1 x 4.8','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(97,376,4,'58897_XC11090807',7.490000000000000213,'1/13/2025',7.490000000000000213,'1 x 0.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(98,378,4,'58897_XC11281491',39.75,'1/24/2025',39.75,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(99,381,4,'58897_XC11189472',29.94999999999999929,'1/13/2025',29.94999999999999929,'1 x 8','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(100,414,4,'58897_XC10943904',28.5,'1/27/2025',28.5,'1 x 24','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(101,415,4,'58897_XC28467',0.7900000000000000355,'3/10/2025',0.7900000000000000355,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(102,416,4,'58897_XC10566294',0.6899999999999999467,'1/27/2025',0.6899999999999999467,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(103,417,4,'58897_XC37782',24.75,'3/24/2025',24.75,'1 each','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(104,419,15,'FVEG13',48.22999999999999688,'2/4/2025',48.22999999999999688,'12 x 3','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(105,428,4,'58897_XC10172100',5.429999999999999716,'2/25/2025',5.429999999999999716,'1 each','qt',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(106,433,13,'SYRP67',18.76999999999999958,'6/23/2025',18.76999999999999958,'6 x 5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(107,434,17,'71100210057',58.35000000000000142,'4/1/2025',58.35000000000000142,'18 x 3','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(108,436,17,'7.42434E+11',7.540000000000000035,'3/28/2025',7.540000000000000035,'1 x 10','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(109,437,4,'58897_XC11725424',31.5,'3/24/2025',31.5,'24 x 12','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(110,439,17,'90478410050',23.26999999999999958,'4/2/2025',23.26999999999999958,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(111,440,17,'90478410012',23.58999999999999986,'4/2/2025',23.58999999999999986,'24 x 12.5','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(112,441,17,'19514',23.58999999999999986,'4/17/2025',23.58999999999999986,'24 x 12.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(113,442,17,'90478410098',23.26999999999999958,'4/2/2025',23.26999999999999958,'24 x 12.5','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(114,443,17,'20260',23.26999999999999958,'4/17/2025',23.26999999999999958,'24 x 12.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(115,444,9,'165826_XC12097642',38.0,'4/22/2025',38.0,'24 x 16','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(116,445,9,'165826_XC12097644',40.0,'4/22/2025',40.0,'24 x 500','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(117,447,4,'58897_XC6949630',23.5,'2/4/2025',23.5,'1 x 50','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(118,448,4,'58897_XC10610694',19.94999999999999929,'3/24/2025',19.94999999999999929,'1 x 50','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(119,454,16,'INDV98',31.08999999999999986,'6/2/2025',31.08999999999999986,'1000 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(120,461,13,'9329384',31.78999999999999915,'7/2/2025',31.78999999999999915,'1000 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(121,471,15,'ROLP69',20.0,'2/17/2025',20.0,'1 x 500','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(122,474,13,'OILS49',68.29000000000000626,'6/30/2025',68.29000000000000626,'1 x 50','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(123,475,24,'32165',94.8499999999999944,'3/19/2025',94.8499999999999944,'1 x 50','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(124,477,15,'DMIX11',81.95999999999999374,'5/30/2025',81.95999999999999374,'8 x 55','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(125,480,4,'58897_XC48718',6.990000000000000213,'1/6/2025',6.990000000000000213,'1 x 0.5','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(126,482,16,'PR3001',26.39999999999999858,'2/21/2025',26.39999999999999858,'1 x 18','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(127,497,17,'44313',7.69000000000000039,'5/28/2025',7.69000000000000039,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(128,504,16,'GLIN18',53.96000000000000085,'4/28/2025',53.96000000000000085,'1 x 100','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(129,510,4,'58897_XC11725428',12.94999999999999929,'3/15/2025',12.94999999999999929,'1 each','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(130,511,17,'36243',10.33000000000000007,'4/22/2025',10.33000000000000007,'1 each','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(131,517,15,'MAYO32',12.47000000000000063,'3/11/2025',12.47000000000000063,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(132,518,15,'MAYO02',10.88000000000000079,'2/17/2025',10.88000000000000079,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(133,521,13,'6328157',15.43999999999999951,'7/2/2025',15.43999999999999951,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(134,523,17,'48001265301',21.98999999999999843,'4/1/2025',21.98999999999999843,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(135,524,17,'48001265400',22.73999999999999843,'5/20/2025',22.73999999999999843,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(136,525,17,'52100010793',12.32000000000000028,'3/28/2025',12.32000000000000028,'1 x 168','oz',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(137,526,17,'49000044225',38.10999999999999944,'3/10/2025',38.10999999999999944,'24 x 335','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(138,529,16,'MLK051',22.92000000000000171,'5/26/2025',22.92000000000000171,'4 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(139,532,17,'41900076382',17.44000000000000127,'4/29/2025',17.44000000000000127,'4 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(140,533,17,'370441',17.44000000000000127,'4/22/2025',17.44000000000000127,'4 each','gal',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(141,539,13,'MLK060',23.87999999999999901,'7/2/2025',23.87999999999999901,'4 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(142,541,14,'016D',0.930000000000000048,'3/29/2025',0.930000000000000048,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(143,544,16,'DRES37',40.28999999999999915,'5/9/2025',40.28999999999999915,'18 x 3.2','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(144,549,13,'MUST16',19.85999999999999944,'6/16/2025',19.85999999999999944,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(145,551,17,'27541009095',3.75,'4/15/2025',3.75,'32 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(146,552,17,'1220319',3.75,'4/22/2025',3.75,'32 x 0.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(147,558,16,'OIL027',29.17999999999999972,'5/26/2025',29.17999999999999972,'1 x 35','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(148,561,16,'OILS28',42.14000000000000056,'4/28/2025',42.14000000000000056,'1 x 35','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(149,565,15,'400471',15.35999999999999944,'5/20/2025',15.35999999999999944,'1 x 8.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(150,573,13,'PR1411',31.73000000000000042,'6/27/2025',31.73000000000000042,'4 x 2','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(151,580,15,'PR1400',21.71999999999999887,'5/23/2025',21.71999999999999887,'1 x 50','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(152,599,4,'58897_XC5296039',4.790000000000000035,'3/18/2025',4.790000000000000035,'1 each','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(153,603,15,'SPAG21',35.42999999999999972,'3/18/2025',35.42999999999999972,'2 x 10','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(154,607,13,'1023018',35.22999999999999687,'7/2/2025',35.22999999999999687,'2 x 10','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(155,610,17,'3.0223E+11',8.839999999999999858,'4/29/2025',8.839999999999999858,'1 x 10','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(156,611,17,'50622',8.839999999999999858,'4/22/2025',8.839999999999999858,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(157,612,17,'50624',6.570000000000000284,'4/22/2025',6.570000000000000284,'5 each','bag',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(158,613,17,'17923001168',6.570000000000000284,'4/29/2025',6.570000000000000284,'5 each','bag',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(159,614,17,'7.40695E+12',6.25,'4/1/2025',6.25,'5 each','bag',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(160,616,17,'6.80444E+11',16.58999999999999986,'4/1/2025',16.58999999999999986,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(161,617,17,'28764000456',7.990000000000000213,'5/13/2025',7.990000000000000213,'1 x 2.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(162,618,17,'2876400045',9.52999999999999937,'4/15/2025',9.52999999999999937,'4 x 2.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(163,619,17,'42312',29.21999999999999887,'4/22/2025',29.21999999999999887,'4 x 2.5','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(164,620,17,'8.96968E+11',7.379999999999999894,'4/2/2025',7.379999999999999894,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(165,621,17,'430288',7.379999999999999894,'4/22/2025',7.379999999999999894,'1 x 0.5','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(166,622,17,'2876400126',6.820000000000000284,'3/19/2025',6.820000000000000284,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(167,623,17,'20600425195',25.28999999999999915,'4/29/2025',25.28999999999999915,'1 x 24','unit',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(168,624,17,'8.13831E+12',24.01999999999999958,'5/13/2025',24.01999999999999958,'1 x 24','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(169,625,17,'42519',26.58999999999999986,'4/22/2025',26.58999999999999986,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(170,626,17,'28764000661',10.81000000000000049,'3/10/2025',10.81000000000000049,'1 x 2.5','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(171,627,17,'43858',4.400000000000000356,'5/28/2025',4.400000000000000356,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(172,628,17,'8.13831E+11',10.09999999999999965,'4/29/2025',10.09999999999999965,'4 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(173,629,17,'53408',58.43999999999999773,'5/28/2025',58.43999999999999773,'1 x 8','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(174,630,17,'20600800169',7.219999999999999752,'4/29/2025',7.219999999999999752,'3 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(175,636,1,'101841_XC10776472',32.0,'6/24/2025',32.0,'1 x 8','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(176,638,17,'74234951124',5.950000000000000177,'5/20/2025',5.950000000000000177,'1 x 28','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(177,644,15,'PR1568',95.3700000000000045,'5/23/2025',95.3700000000000045,'1 x 10','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(178,652,15,'PICK41',26.19999999999999929,'6/9/2025',26.19999999999999929,'5 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(179,669,17,'40138',10.09999999999999965,'5/28/2025',10.09999999999999965,'4 each','bag',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(180,670,17,'6.46127E+11',7.730000000000000426,'5/20/2025',7.730000000000000426,'1 each','bag',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(181,680,17,'68274669316',5.389999999999999681,'4/29/2025',5.389999999999999681,'35 x 500','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(182,681,4,'58897_XC11484063',5.429999999999999716,'3/24/2025',5.429999999999999716,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(183,688,4,'58897_XC7505960',19.0,'3/24/2025',19.0,'1 x 25','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(184,692,17,'1090094',9.039999999999999147,'4/17/2025',9.039999999999999147,'1 x 27.4','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(185,693,17,'44000058326',50.07000000000000028,'5/20/2025',50.07000000000000028,'6 x 27.4','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(186,702,15,'PR0399',29.12000000000000099,'6/4/2025',29.12000000000000099,'4 x 5','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(187,705,15,'PR9903',39.67999999999999972,'6/4/2025',39.67999999999999972,'1 x 8','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(188,711,16,'SALT20',8.47000000000000064,'5/26/2025',8.47000000000000064,'9 x 3','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(189,715,15,'ORSA18',73.9200000000000017,'5/12/2025',73.9200000000000017,'3 x 1','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(190,724,15,'SAUC06',22.25,'5/23/2025',22.25,'1 each','jug',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(191,725,17,'41500741611',15.40000000000000035,'4/15/2025',15.40000000000000035,'1 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(192,729,15,'ORSA32',27.55999999999999873,'3/4/2025',27.55999999999999873,'1 x 136','jar',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(193,738,17,'41390001710',14.75999999999999979,'3/10/2025',14.75999999999999979,'4 each','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(194,740,17,'11210000032',7.019999999999999574,'5/20/2025',7.019999999999999574,'5 each','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(195,742,13,'BQSA21',17.10000000000000143,'7/2/2025',17.10000000000000143,'1 each','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(196,752,16,'OILS46',63.49000000000000198,'3/24/2025',63.49000000000000198,'1 x 50','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(197,759,17,'1020020',58.06000000000000227,'4/22/2025',58.06000000000000227,'1 x 50','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(198,762,16,'OILS91',25.64000000000000056,'3/7/2025',25.64000000000000056,'1 x 35','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(199,767,16,'SMP014',8.490000000000000213,'3/21/2025',8.490000000000000213,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(200,768,13,'SMP027',5.660000000000000142,'7/2/2025',5.660000000000000142,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(201,770,15,'SHMP42',6.80999999999999961,'3/11/2025',6.80999999999999961,'1 each','lb',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(202,773,17,'8.10044E+11',51.64999999999999858,'3/28/2025',51.64999999999999858,'2 each','bag',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(203,776,4,'58897_XC11725427',33.5,'3/15/2025',33.5,'5 each','each',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(204,779,15,'PR0770',29.51000000000000156,'5/23/2025',29.51000000000000156,'1 x 25','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(205,784,16,'472265',44.09000000000000342,'6/2/2025',44.09000000000000342,'24 x 500','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(206,791,17,'7.60696E+11',7.870000000000000106,'5/20/2025',7.870000000000000106,'1 x 16','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(207,792,17,'41398',20.71999999999999887,'5/28/2025',20.71999999999999887,'5 each','bg',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(208,796,16,'ISP016',12.96000000000000085,'5/9/2025',12.96000000000000085,'6 x 20','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(209,816,17,'8.12944E+11',3.319999999999999841,'3/19/2025',3.319999999999999841,'1 x 13','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(210,818,4,'58897_XC10447739',41.5,'3/18/2025',41.5,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(211,825,15,'SUGR03',24.41000000000000014,'4/8/2025',24.41000000000000014,'1 x 25','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(212,827,15,'400188',36.04999999999999715,'5/12/2025',36.04999999999999715,'1 x 50','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(213,829,15,'SUGR06',32.35999999999999944,'3/13/2025',32.35999999999999944,'1 x 25','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(214,831,13,'4395612',28.64999999999999858,'6/27/2025',28.64999999999999858,'1 x 25','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(215,839,16,'TEA030',27.67999999999999972,'4/14/2025',27.67999999999999972,'24 x 4','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(216,841,16,'TEA031',59.8299999999999983,'1/23/2025',59.8299999999999983,'1 x 8','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(217,852,9,'165826_XC12097640',28.0,'4/22/2025',28.0,'24 x 16','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(218,853,4,'58897_XC10447738',32.5,'3/24/2025',32.5,'24 x 12','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(219,854,17,'87914',29.69000000000000127,'4/17/2025',29.69000000000000127,'24 x 20','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(220,855,17,'21136070378',29.69000000000000127,'4/2/2025',29.69000000000000127,'24 x 12','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(221,857,16,'SALT03',3.540000000000000035,'5/9/2025',3.540000000000000035,'12 x 3','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(222,858,15,'272261',39.5,'6/9/2025',39.5,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(223,862,15,'369874',12.96000000000000085,'5/16/2025',12.96000000000000085,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(224,865,15,'270670',16.73000000000000042,'5/23/2025',16.73000000000000042,'2 x 5','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(225,866,16,'OLVS24',78.71999999999999887,'5/26/2025',78.71999999999999887,'1 x 128','jug',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(226,868,13,'410006',20.16000000000000014,'6/30/2025',20.16000000000000014,'6 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(227,871,13,'OLVS11',4.240000000000000213,'6/27/2025',4.240000000000000213,'1 each','ea',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(228,873,15,'OLVS13',14.41999999999999993,'5/23/2025',14.41999999999999993,'1 each','bottle',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(229,874,17,'7.60695E+11',12.93999999999999951,'4/1/2025',12.93999999999999951,'4 each','case',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(230,877,16,'CDNK24',6.570000000000000284,'5/26/2025',6.570000000000000284,'24 x 16.9','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(231,879,16,'272352',40.04999999999999715,'6/2/2025',40.04999999999999715,'24 x 12','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(232,884,13,'405123',37.29999999999999715,'7/2/2025',37.29999999999999715,'24 x 1','cs',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
INSERT INTO vendor_products VALUES(233,886,4,'58897_XC11725429',4.740000000000000213,'3/24/2025',4.740000000000000213,'1 each','gal',1,1,'2025-07-05 01:58:22','2025-07-05 01:58:22');
CREATE TABLE menu_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_name TEXT NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                effective_date TEXT,
                notes TEXT
            );
INSERT INTO menu_versions VALUES(0,'Master List','Complete list of all available menu items',0,'2025-07-05 21:00:54',NULL,NULL);
INSERT INTO menu_versions VALUES(1,'Current Menu','Currently active menu for service',1,'2025-07-05 02:06:35','2025-07-04',NULL);
INSERT INTO menu_versions VALUES(2,'Planning Menu','Next menu version in development',0,'2025-07-05 02:06:35',NULL,NULL);
INSERT INTO menu_versions VALUES(3,'Experimental Menu','Testing new items and concepts',0,'2025-07-05 02:06:35',NULL,NULL);
CREATE TABLE units (
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL UNIQUE,
                dimension TEXT NOT NULL CHECK(dimension IN ('WEIGHT', 'VOLUME', 'COUNT')),
                to_canonical_factor DECIMAL(20,10) NOT NULL,
                is_precise BOOLEAN DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO units VALUES(1,'Gram','g','WEIGHT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(2,'Grams','grams','WEIGHT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(3,'Kilogram','kg','WEIGHT',1000,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(4,'Milligram','mg','WEIGHT',0.00100000000000000002,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(5,'Pound','lb','WEIGHT',453.5923700000000167,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(6,'Pounds','lbs','WEIGHT',453.5923700000000167,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(7,'Ounce','oz','WEIGHT',28.34952312500000105,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(8,'Ounces','ounces','WEIGHT',28.34952312500000105,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(9,'Milliliter','ml','VOLUME',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(10,'Milliliters','milliliters','VOLUME',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(11,'Liter','l','VOLUME',1000,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(12,'Liters','liters','VOLUME',1000,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(13,'Fluid Ounce','fl oz','VOLUME',29.5735295624999992,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(14,'Fluid Ounces','fl ounces','VOLUME',29.5735295624999992,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(15,'Cup','cup','VOLUME',236.5882369999999924,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(16,'Cups','cups','VOLUME',236.5882369999999924,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(17,'Pint','pt','VOLUME',473.1764729999999873,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(18,'Pints','pints','VOLUME',473.1764729999999873,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(19,'Quart','qt','VOLUME',946.352945999999975,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(20,'Quarts','quarts','VOLUME',946.352945999999975,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(21,'Gallon','gal','VOLUME',3785.411783999999898,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(22,'Gallons','gallons','VOLUME',3785.411783999999898,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(23,'Tablespoon','tbsp','VOLUME',14.78676480000000026,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(24,'Tablespoons','tablespoons','VOLUME',14.78676480000000026,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(25,'Teaspoon','tsp','VOLUME',4.928921589999999853,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(26,'Teaspoons','teaspoons','VOLUME',4.928921589999999853,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(27,'Each','each','COUNT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(28,'Each','ea','COUNT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(29,'Piece','piece','COUNT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(30,'Pieces','pieces','COUNT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(31,'Unit','unit','COUNT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(32,'Units','units','COUNT',1,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(33,'Dozen','dozen','COUNT',12,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(34,'Dozen','doz','COUNT',12,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(35,'Ounce Weight','oz wt','WEIGHT',28.34952312500000105,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(36,'Pound Weight','lb wt','WEIGHT',453.5923700000000167,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(37,'Fluid Ounce','fl.oz','VOLUME',29.5735295624999992,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
INSERT INTO units VALUES(38,'Fluid Ounce','fluid oz','VOLUME',29.5735295624999992,1,'2025-07-05 04:28:14','2025-07-05 04:28:14');
CREATE TABLE ingredient_unit_equivalents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                custom_unit_name TEXT NOT NULL,
                canonical_quantity DECIMAL(10,4) NOT NULL,
                canonical_unit_symbol TEXT NOT NULL,
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                UNIQUE(inventory_id, custom_unit_name)
            );
CREATE TABLE unit_conversion_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_ingredient_id INTEGER,
                from_quantity DECIMAL(10,4),
                from_unit TEXT,
                to_quantity DECIMAL(10,4),
                to_unit TEXT,
                conversion_method TEXT,
                conversion_status TEXT,
                error_message TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_ingredient_id) REFERENCES recipe_ingredients(id)
            );
CREATE TABLE ingredient_densities (
                    density_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_name TEXT NOT NULL UNIQUE,
                    density_g_per_ml DECIMAL(10,4) NOT NULL,
                    source TEXT,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
INSERT INTO ingredient_densities VALUES(1,'Water',1,'Standard',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(2,'Milk',1.030000000000000026,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(3,'Heavy Cream',0.993999999999999995,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(4,'Oil',0.9200000000000000399,'Average vegetable oil',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(5,'Olive Oil',0.9150000000000000355,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(6,'Vegetable Oil',0.9200000000000000399,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(7,'Vinegar',1.010000000000000008,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(8,'Honey',1.419999999999999929,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(9,'Corn Syrup',1.379999999999999894,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(10,'Molasses',1.399999999999999912,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(11,'All-Purpose Flour',0.5290000000000000257,'King Arthur',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(12,'Flour',0.5290000000000000257,'King Arthur',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(13,'Sugar',0.8449999999999999734,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(14,'Granulated Sugar',0.8449999999999999734,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(15,'Brown Sugar',0.7209999999999999743,'USDA (packed)',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(16,'Powdered Sugar',0.5600000000000000533,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(17,'Salt',1.217000000000000081,'Table salt',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(18,'Kosher Salt',0.6899999999999999467,'Diamond Crystal',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(19,'Baking Powder',0.7209999999999999743,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(20,'Baking Soda',0.6889999999999999458,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(21,'Cornstarch',0.6290000000000000035,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(22,'Butter',0.9110000000000000319,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(23,'Sour Cream',0.992999999999999994,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(24,'Yogurt',1.030000000000000026,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(25,'Cream Cheese',0.979999999999999983,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(26,'Ketchup',1.139999999999999902,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(27,'Mayonnaise',0.910000000000000031,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(28,'Mustard',1.050000000000000044,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(29,'Soy Sauce',1.199999999999999956,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(30,'Hot Sauce',1.020000000000000017,'USDA',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(31,'Ground Beef',0.969999999999999974,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(32,'Chicken',1.040000000000000035,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(33,'Fish',1,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(34,'BBQ Sauce',1.25,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(35,'Ranch Dressing',0.949999999999999956,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(36,'Buffalo Sauce',1.020000000000000017,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(37,'Alfredo Sauce',1.100000000000000089,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(38,'Marinara Sauce',1.030000000000000026,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
INSERT INTO ingredient_densities VALUES(39,'Pesto',0.949999999999999956,'Approximate',NULL,'2025-07-05 04:30:05','2025-07-05 04:30:05');
CREATE TABLE vendor_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER,
                vendor_name TEXT,
                vendor_description TEXT,
                item_code TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                UNIQUE(inventory_id, vendor_name)
            );
INSERT INTO vendor_descriptions VALUES(434,5,'Buckhead Meat & Seafood OF HOUSTON','1 | 15 LB CATFISH FILLET FRESH 5-7OZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(435,8,'Jorge Garza','15Doz XL Eggs',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(436,9,'Jorge Garza','24|16oz Fresca |Mex',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(437,10,'Jorge Garza','24|16oz Fresco | Mex',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(438,11,'Jorge Garza','24ct Green Kale',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(439,12,'Jorge Garza','35#=====Clear Fry | Canola',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(440,14,'Buckhead Meat & Seafood OF HOUSTON','4 | 10#av CHICKEN WING BUFFALO 1812 JNT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(441,24,'Jorge Garza','48ct Green Onion|Iceless 12#',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(442,25,'Jorge Garza','50# Jumbo Carrot',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(443,29,'Jorge Garza','A|P Flour',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(444,39,'Sysco Houston','APTZR CORN RIB HCKRY SMK',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(446,60,'MJ Sweet and Cake','Banana Pudding',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(447,71,'Jorge Garza','Beets|Red',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(448,890,'JAKES, INC.','BLACK PEPPER GROUND',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(449,84,'MJ Sweet and Cake','Blueberry Lemon Cake',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(450,86,'CB Commissary LLC','Bread Challah Burger Buns 2.5 oz',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(451,87,'COMMON BOND BISTRO & BAKERY','Bread Challah Burger Buns 3 oz.',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(452,88,'CB Commissary LLC','Bread Challah Rolls 2 oz (12 pk)',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(453,89,'CB Commissary LLC','Bread Challish Burger Buns 3oz',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(454,90,'CB Commissary LLC','Bread Classic White Loaf Sliced',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(455,91,'COMMON BOND BISTRO & BAKERY','Bread Classic White Loaf Sliced.',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(456,92,'CB Commissary LLC','Bread French Toast Brioche Loaf Thick Sliced',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(457,93,'CB Commissary LLC','Bread French Toast Brioche Loaf Thin Sliced',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(458,102,'JAKE''S, INC.','BREAD YELLOW TEXAS TOAST SLIC',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(459,105,'RESTAURANT DEPOT','BTR PLUGRA CLRUED 5LB',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(460,112,'JAKES, INC.','BUTTER CLARIFIED PLUGRA UNSLT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(461,131,'Jorge Garza','Carrot',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(462,138,'Jorge Garza','Case== = = Extra Melt | Yellow......',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(463,140,'Jorge Garza','Case —---Sprite 500ml',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(464,141,'Jorge Garza','Case Sprite 500ml.',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(465,142,'Jorge Garza','CaseSprite 500ml',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(466,145,'Buckhead Meat & Seafood OF HOUSTON','CATFISH FILLET FRESH 5-7OZ Country of Origin : USA|FARMED',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(467,146,'Jorge Garza','Cauliflower | USA',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(468,147,'Jorge Garza','Cayenne Pepper 40SHU',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(469,148,'Jorge Garza','Cayenne Pepper 40SHU',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(470,149,'Jorge Garza','Celery',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(471,153,'JAKE''S, INC.','CELERY 6 EACH',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(472,157,'JAKES, INC.','CHEESE AMERICAN MELTING YELLO',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(473,163,'JAKES, INC.','CHEESE CHEDDER MILD LOAF',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(474,165,'US Foods','CHEESE CHED MONT JACK 50|50',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(475,171,'US Foods','CHEESE LOAN PEPPER JACK',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(476,175,'Jorge Garza','Chicken Base | Knorr',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(477,178,'Buckhead Meat & Seafood OF HOUSTON','CHICKEN TENDER CLIPPED JUMBO',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(478,179,'Buckhead Meat & Seafood OF HOUSTON','CHICKEN TENDER JUMBO SOL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(479,183,'US Foods','CHICKEN THIGH BNLS SKIN ON',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(480,186,'JAKE''S, INC.','CHICKEN WING LG|JMB 1 AND 14 POULTRY X',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(481,192,'RESTAURANT DEPOT','CHS GOLD VELV LOL 5LB C CASES 1 UNITS 6',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(482,194,'RESTAURANT DEPOT','CHZ CHEDDAR CUBES',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(483,195,'RESTAURANT DEPOT','CHZ GLDN VLVT LOL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(485,197,'RESTAURANT DEPOT','CHZ PARM GRATED 5#',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(486,208,'ALVARADO''S','COCA COLA #2 500 ML 24|16 OZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(487,209,'ALVARADO''S','COCA COLA MEXICANA 24|16 OZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(488,213,'Jorge Garza','Coke |500ml Mex',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(489,214,'RESTAURANT DEPOT','COKE MEXICAN',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(490,215,'RESTAURANT DEPOT','COKE MEXICAN',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(491,219,'JAKES, INC.','COLE SLAW 3WAY SEP 1|8 SHRED',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(493,259,'JAKE''S, INC.','CREAM HEAVY WHIPPING UHT 36% QT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(494,261,'RESTAURANT DEPOT','CRM WHP FRH 40%|OF QRT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(495,262,'RESTAURANT DEPOT','CRM WHP FRH 40%|OF QRT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(496,263,'RESTAURANT DEPOT','CROUTONS HMSTYL CQ 4|2.5',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(497,284,'Jorge Garza','Diakon Radish',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(498,285,'RESTAURANT DEPOT','DRES CRM CAESAR KR 4|1GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(499,286,'RESTAURANT DEPOT','DRES RANCH JALAPNO',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(500,291,'US Foods','DRESSING HONEY DIJON #651',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(501,293,'RESTAURANT DEPOT','DRES TARTAR SAUCE 1GL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(502,297,'JAKES, INC.','DRINK GRAPEFRUIT JARRITOS GLA',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(503,299,'JAKES, INC.','DRINK SIORAL MUNDET',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(504,308,'JAKE''S, INC.','DRINK STRAWBERRY JARRITOS GLA',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(505,311,'US Foods','DRINK TAMARIND JARRITOS GLASS',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(506,313,'RESTAURANT DEPOT','DR PEPPER',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(507,314,'RESTAURANT DEPOT','DR PEPPER 12Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(508,315,'RESTAURANT DEPOT','Dr Pepper -16.9 Oz',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(509,316,'JAKE''S, INC.','DRY BREAD TEXAS TOAST 3|4"',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(510,317,'RESTAURANT DEPOT','DS HEAVY CRM 36%',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(511,318,'Jorge Garza','Each Italian Parsley',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(514,324,'RESTAURANT DEPOT','EGG MED LSE 15DZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(515,331,'JAKES, INC.','EGGS LARGE GRD AA LOOSE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(516,335,'US Foods','EGGS XLARGE GRD AA LOOSE PRIC',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(517,345,'ALVARADO''S','FANTA FRESA 24 |16 OZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(518,346,'ALVARADO''S','FANTA ORANGE 24 |16 OZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(519,347,'Jorge Garza','Fanta | Orange 500ml | 24ct',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(520,353,'JAKES, INC.','FISH CATFISH 5-7 FILLET DOMES',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(521,354,'JAKES, INC.','FISH COD PACIFIC LOIN 6 OZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(522,355,'JAKE''S, INC.','FISH HADDOCK 6OZ YUENGLING',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(523,361,'US Foods','FLOUR H AND R ALL PURPOSE DRY',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(525,366,'Jorge Garza','Fresca | Mex',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(526,371,'US Foods','FRIES SC CLEAR COAT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(527,373,'RESTAURANT DEPOT','FSH COD HEDGE 2Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(528,376,'Jorge Garza','Gal Lemon Juice',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(529,378,'Jorge Garza','Gallon======Pure Honey',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(530,381,'Jorge Garza','Ghost Pepper Powder.',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(535,414,'Jorge Garza','Green Kale',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(536,415,'Jorge Garza','Green Onion',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(537,416,'Jorge Garza','Green Onion.',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(538,419,'JAKES, INC.','GREENS COLLARD CHOPPED ''A''',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(539,428,'Jorge Garza','Heavy Cream 40% |Hiland""',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(540,433,'US Foods','HONEY CLOVERAMBER NATURAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(541,434,'RESTAURANT DEPOT','HVR BLUE CHEESE MX',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(542,436,'RESTAURANT DEPOT','JALAP NACHO SLICED #10',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(543,437,'Jorge Garza','Jarritos | Fresa12oz',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(544,439,'RESTAURANT DEPOT','JARRITOS LIME',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(545,440,'RESTAURANT DEPOT','JARRITOS MANDARIN',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(546,441,'RESTAURANT DEPOT','JARRITOS MANDARIN 12.5Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(547,442,'RESTAURANT DEPOT','JARRITOS STRAUBERY 12.52',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(548,443,'RESTAURANT DEPOT','JARRITOS STRAWBERY 12.5Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(549,444,'ALVARADO''S','JOYA DURAZNO 16 OZ',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(550,445,'ALVARADO''S','JOYA PINA 4|500 ML',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(551,447,'Jorge Garza','Jumbo Carrot',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(552,448,'Jorge Garza','Jumbo Yellow Onion.',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(553,454,'JAKE''S, INC.','KETCHUP 33%  FANCY PC GOURMET',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(555,461,'US Foods','KETCHUP, TOMATO FANCY 33% SS FOIL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(556,474,'US Foods','LARD PURE LAUREL NON DEODORIZ00751884180776',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(557,475,'ALTAMIRA LTD.','Lea Jane''s Chicken Breading 50Ib',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(558,477,'JAKES, INC.','LEMONADE SWEET BREW PURE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(559,480,'Jorge Garza','Lemon Juice',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(560,482,'JAKE''S, INC.','LETTUCE KALERA KRUNCH LIVING',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(563,497,'RESTAURANT DEPOT','Limes - 5 lbs',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(564,504,'JAKE''S, INC.','LINER CAN 60 GAL 38X58 2ML',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(565,510,'Jorge Garza','Mayo',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(566,511,'RESTAURANT DEPOT','MAYO CHEFS QUALITY 1GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(568,517,'JAKES, INC.','MAYONNAISE HEAVY DUTY',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(569,518,'JAKES, INC.','MAYONNAISE HEAVY DUTY',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(570,521,'US Foods','MAYONNAISE  XHVY PLST JUG SHLF',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(571,523,'RESTAURANT DEPOT','MAYO REAL HELLMNS GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(572,524,'RESTAURANT DEPOT','MAYO XHVY HELLMANN',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(573,525,'RESTAURANT DEPOT','MCOR LEMON PEPPER',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(574,526,'RESTAURANT DEPOT','MEXICAN COKE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(575,529,'JAKE''S, INC.','MILK 2% GALLONS',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(576,532,'RESTAURANT DEPOT','MILK WHL GAIVOF GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(577,533,'RESTAURANT DEPOT','MILK WHL GAL/OF GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(578,539,'US Foods','MILK WHOLE GALLONS',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(579,541,'CB Commissary LLC','Mini King Cake RASP Deco',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(580,544,'JAKE''S, INC.','MIX DRESSING RANCH DRY HV 1 GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(581,549,'US Foods','MUSTARD CREOLE 443135',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(582,551,'RESTAURANT DEPOT','NIAGARA WATER',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(583,552,'RESTAURANT DEPOT','NIAGARA WATER .5LTR, 32ct',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(584,558,'JAKE''S, INC.','OIL CANOLA CLEAR FRY',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(585,561,'JAKE''S, INC.','OIL CANOLA CLEAR SALAD OIL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(586,565,'JAKES, INC.','Oil, TRUFFLE WHITE ASARO',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(587,573,'US Foods','ONIONS GREEN ICELESS CASE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(588,580,'JAKES, INC.','ONIONS YELLOW COLOSSAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(591,599,'Jorge Garza','Paprika 120ASTA',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(592,603,'JAKES, INC.','PASTA CAVATAPPI MACARONI CURL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(593,607,'US Foods','PASTA  CAVATP TWSTD 1.38  RAW',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(594,610,'RESTAURANT DEPOT','PD CABB RED SHRD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(595,611,'RESTAURANT DEPOT','PD CABB RED SHRD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(596,612,'RESTAURANT DEPOT','PD CARROT SHRED 5#',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(597,613,'RESTAURANT DEPOT','PD CARROT SHRED 5#',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(598,614,'RESTAURANT DEPOT','PD CELERY 5CT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(599,616,'RESTAURANT DEPOT','PD GARLIC ASIANPLD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(600,617,'RESTAURANT DEPOT','PD GRNS COLLARD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(601,618,'RESTAURANT DEPOT','PD GRNS COLLARD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(602,619,'RESTAURANT DEPOT','PD GRNS COLLARD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(603,620,'RESTAURANT DEPOT','PD JCE LEMON 5GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(604,621,'RESTAURANT DEPOT','PD JCE LEMON .5GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(605,623,'RESTAURANT DEPOT','PD KALE GREEN 24CT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(606,624,'RESTAURANT DEPOT','PD KALE GREEN 24CT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(607,625,'RESTAURANT DEPOT','PD KALE GREENS',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(608,626,'RESTAURANT DEPOT','PD KALE SALAD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(609,627,'RESTAURANT DEPOT','PD LETT ROMAINE HT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(610,628,'RESTAURANT DEPOT','PD ON GRN ICELESS',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(611,629,'RESTAURANT DEPOT','PD SHALLOT FRESH',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(612,630,'RESTAURANT DEPOT','PDU GREEN 2CT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(613,636,'MJ Sweet and Cake','Pecan Upside Down Cake',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(614,638,'RESTAURANT DEPOT','PEPPER CHIPOTLE SH',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(615,644,'JAKES, INC.','PEPPERS RED FRESNO 10',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(616,652,'JAKES, INC.','PICKLES DILL SLCD KK HVY PACK',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(617,669,'RESTAURANT DEPOT','PROD GRN ONION 2 LB',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(618,670,'RESTAURANT DEPOT','PROD SHALOT DRY 8C',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(619,681,'Jorge Garza','Qt Heavy Cream 40% | Hiland',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(620,688,'Jorge Garza','Red Onion',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(621,692,'RESTAURANT DEPOT','RITZ CRACK PARTY 27.4Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(622,693,'RESTAURANT DEPOT','RITZ PARTY PACK',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(623,702,'JAKES, INC.','*S09AM* CARROTS SHREDDED (4|',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(624,705,'JAKES, INC.','*S09AM* PEPPER HABANERO 8 LB',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(625,711,'JAKE''S, INC.','SALT KOSHER BOX COARSE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(626,715,'JAKES, INC.','Sambal Oelek',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(627,724,'JAKES, INC.','SAUCE BUFFALO WING RED HOT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(628,725,'RESTAURANT DEPOT','SAUCE BUFF WING FRA GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(629,729,'JAKES, INC.','SAUCE CHILI GRD GARLIC 136Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(630,816,'RESTAURANT DEPOT','SAUCE PAN 2 1/2QT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(631,738,'RESTAURANT DEPOT','SAUCE SOY KIK',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(632,740,'RESTAURANT DEPOT','SAUCE TAB HOT',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(633,742,'US Foods','SAUSE BBQ APPLEWOOD BACON',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(634,752,'JAKE''S, INC.','SHORTENING ALL PURPOSE PALM',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(635,759,'RESTAURANT DEPOT','SHORTENING FRYRITE 50#',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(637,767,'JAKE''S, INC.','SHRIMP 16|20 DOMESTIC BROWN SEAFOOD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(638,768,'US Foods','SHRIMP 16|20 EZ PEEL WHITE SEAFOOD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(639,770,'JAKES, INC.','SHRIMP 16 / 20 WHITE P / D TAIL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(640,773,'RESTAURANT DEPOT','SHRP P&D TO 21-25',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(642,776,'Jorge Garza','Sliced Pickle',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(643,779,'JAKES, INC.','*SO12P* KALE GREEN CASE BR',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(644,784,'JAKE''S, INC.','SODA ORANGE MEXICAN GLASS',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(648,791,'RESTAURANT DEPOT','SPC PEPR CAYENNE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(649,792,'RESTAURANT DEPOT','SPC PEPR CAYENNE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(650,796,'JAKE''S, INC.','SPICE LEMON PEPPER',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(651,818,'Jorge Garza','Sprite 500ml',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(652,825,'JAKES, INC.','SUGAR EFG GRANULATED',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(653,827,'JAKES, INC.','SUGAR EFG GRANULATED',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(654,831,'US Foods','SUGAR  WHT EX FINE CANE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(655,839,'JAKE''S, INC.','TEA 4OZ FP 3 GALLON YIELD',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(656,841,'JAKE''S, INC.','TEA SWEET BREW PURE CANE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(657,852,'ALVARADO''S','TOPO CHICO 24 | 355. ML',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(658,853,'Jorge Garza','Topo Chico 24ct|355ml',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(659,854,'RESTAURANT DEPOT','TOPO CHICO MINERAL 12Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(660,855,'RESTAURANT DEPOT','TOPO CHICO MINERAL 12Z',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(661,857,'JAKE''S, INC.','*TO* SALT KOSHER BOX 10024600017029',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(662,858,'JAKES, INC.','*TO* SODA COCA COLA 500ML MEXICAN',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(663,862,'JAKES, INC.','VINEGAR APPLE CIDER',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(664,865,'JAKES, INC.','VINEGAR RED WINE',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(665,866,'JAKE''S, INC.','VINEGAR RICE HINE SEASONED 10041224705200',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(666,868,'US Foods','VINEGAR WH 50GR m 0007173535009',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(667,871,'US Foods','VINEGAR WHITE 40 GR',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(668,873,'JAKES, INC.','VINEGAR WINE RED',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(669,874,'RESTAURANT DEPOT','VINRGAR WHITE CQ 1GAL',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(670,877,'JAKE''S, INC.','WATER BOTTLED PURIFIED .5',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(671,879,'JAKE''S, INC.','WATER MINERAL TOPO CHICO MEX',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(672,884,'US Foods','WATER TOPO CHICO ?LIME TOUdC',NULL,'2025-07-07 23:38:33');
INSERT INTO vendor_descriptions VALUES(673,886,'Jorge Garza','Whole Milk',NULL,'2025-07-07 23:38:33');
CREATE TABLE recipes_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                note_type TEXT NOT NULL,
                note_text TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            );
INSERT INTO recipes_notes VALUES(1,81,'high_food_cost','Food cost $6.00 exceeds menu price $5.00 (120.0%)','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(2,87,'high_food_cost','Food cost $18.37 exceeds menu price $15.00 (122.5%)','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(3,97,'no_ingredients','Recipe has no ingredients defined','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(4,102,'no_ingredients','Recipe has no ingredients defined','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(5,100,'no_ingredients','Recipe has no ingredients defined','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(6,105,'no_ingredients','Recipe has no ingredients defined','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(7,69,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(8,71,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(9,72,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(10,73,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(11,74,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(12,75,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(13,79,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(14,80,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(15,85,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(16,86,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(17,94,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(18,96,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(19,103,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(20,107,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(21,110,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(22,113,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(23,117,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(24,121,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(25,124,'zero_cost','Recipe has zero or null cost ingredients','2025-07-06 15:09:59');
INSERT INTO recipes_notes VALUES(26,97,'NO_INGREDIENTS','Recipe has no ingredients defined','2025-07-06 15:12:40');
INSERT INTO recipes_notes VALUES(27,102,'NO_INGREDIENTS','Recipe has no ingredients defined','2025-07-06 15:12:40');
INSERT INTO recipes_notes VALUES(28,100,'NO_INGREDIENTS','Recipe has no ingredients defined','2025-07-06 15:12:40');
INSERT INTO recipes_notes VALUES(29,105,'NO_INGREDIENTS','Recipe has no ingredients defined','2025-07-06 15:12:40');
INSERT INTO recipes_notes VALUES(30,74,'ZERO_COST','All 3 ingredients have zero cost','2025-07-06 15:12:40');
INSERT INTO recipes_notes VALUES(31,72,'ZERO_COST','All 3 ingredients have zero cost','2025-07-06 15:12:40');
CREATE TABLE recipe_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_recipe_id INTEGER NOT NULL,
            component_recipe_id INTEGER NOT NULL,
            quantity DECIMAL(10,4) NOT NULL,
            unit_of_measure TEXT NOT NULL,
            cost DECIMAL(10,2) DEFAULT 0,
            FOREIGN KEY (parent_recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (component_recipe_id) REFERENCES recipes(id) ON DELETE RESTRICT,
            UNIQUE(parent_recipe_id, component_recipe_id)
        );
INSERT INTO recipe_components VALUES(1,122,123,8,'fl oz',0.02359999999999999946);
INSERT INTO recipe_components VALUES(2,96,84,3,'oz',0.2556999999999999829);
INSERT INTO recipe_components VALUES(3,95,104,2,'oz',0.00949999999999999977);
INSERT INTO recipe_components VALUES(4,95,84,3,'oz',0.2556999999999999829);
INSERT INTO recipe_components VALUES(5,124,131,1,'oz',37.74604999999999677);
INSERT INTO recipe_components VALUES(6,124,82,1,'ea',1.060000000000000053);
INSERT INTO recipe_components VALUES(7,99,127,2,'oz',0.00949999999999999977);
INSERT INTO recipe_components VALUES(8,99,84,3,'oz',0.2556999999999999829);
INSERT INTO recipe_components VALUES(9,99,82,1,'ea',1.060000000000000053);
INSERT INTO recipe_components VALUES(10,69,91,1,'ea',0.00949999999999999977);
INSERT INTO recipe_components VALUES(11,69,131,1,'oz',37.74604999999999677);
INSERT INTO recipe_components VALUES(12,69,82,5,'oz',5.299999999999999823);
INSERT INTO recipe_components VALUES(13,69,104,2,'oz',0.00949999999999999977);
INSERT INTO recipe_components VALUES(14,103,127,2,'oz',0.00949999999999999977);
INSERT INTO recipe_components VALUES(15,103,131,1,'oz',37.74604999999999677);
INSERT INTO recipe_components VALUES(16,87,91,1,'each',0.00949999999999999977);
INSERT INTO recipe_components VALUES(17,75,104,2,'oz',0.00949999999999999977);
INSERT INTO recipe_components VALUES(18,130,84,5,'oz',0.4263000000000000122);
INSERT INTO recipe_components VALUES(19,83,84,5,'oz',0.4263000000000000122);
INSERT INTO recipe_components VALUES(20,101,78,3.299999999999999823,'pound',0.01379999999999999977);
INSERT INTO recipe_components VALUES(21,85,91,2,'ea',0.01899999999999999953);
INSERT INTO recipe_components VALUES(22,85,68,2,'oz',0.659900000000000042);
INSERT INTO recipe_components VALUES(23,81,82,5,'oz',5.299999999999999823);
INSERT INTO recipe_components VALUES(24,106,107,2,'oz',0.01420000000000000081);
INSERT INTO recipe_components VALUES(25,90,91,3,'each',0.02850000000000000102);
INSERT INTO recipe_components VALUES(26,77,78,1800,'gram',7.527899999999999814);
INSERT INTO recipe_components VALUES(27,129,82,1,'each',1.060000000000000053);
INSERT INTO recipe_components VALUES(28,114,107,4,'oz',0.02850000000000000102);
CREATE TABLE recipe_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                note_type TEXT NOT NULL,
                note_text TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id),
                UNIQUE(recipe_id, note_type)
            );
INSERT INTO recipe_notes VALUES(1,97,'no_ingredients','Recipe has no ingredients or components defined','critical','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(2,102,'no_ingredients','Recipe has no ingredients or components defined','critical','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(3,100,'no_ingredients','Recipe has no ingredients or components defined','critical','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(4,105,'no_ingredients','Recipe has no ingredients or components defined','critical','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(5,75,'zero_cost','All 2 ingredients have zero cost','high','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(6,74,'zero_cost','All 3 ingredients have zero cost','high','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(7,72,'zero_cost','All 3 ingredients have zero cost','high','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(8,113,'missing_costs','1 of 1 ingredients missing costs','medium','2025-07-06 20:46:50');
INSERT INTO recipe_notes VALUES(9,74,'missing_costs','1 of 3 ingredients missing costs','medium','2025-07-06 20:46:50');
CREATE TABLE menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO menus VALUES(4,'Master Menu','Complete list of all possible menu items',1,1,'2025-07-06 21:44:47','2025-07-06 21:44:47');
INSERT INTO menus VALUES(5,'Current Menu','Active menu currently being served',1,2,'2025-07-06 21:44:47','2025-07-06 21:44:47');
INSERT INTO menus VALUES(6,'Future Menu','Planning menu for upcoming changes',0,3,'2025-07-06 21:44:47','2025-07-06 21:44:47');
CREATE TABLE menu_menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    category TEXT,
    sort_order INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT 1,
    override_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
    UNIQUE(menu_id, menu_item_id)
);
INSERT INTO menu_menu_items VALUES(1,4,126,'',0,1,NULL,'2025-07-07 18:38:00');
INSERT INTO menu_menu_items VALUES(3,4,168,NULL,0,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(4,4,201,NULL,1,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(5,4,177,NULL,2,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(6,4,200,NULL,3,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(7,4,183,NULL,4,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(8,4,115,NULL,5,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(9,4,193,NULL,6,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(10,4,116,NULL,7,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(11,4,194,NULL,8,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(12,4,107,NULL,9,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(13,4,178,NULL,10,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(14,4,112,NULL,11,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(15,4,190,NULL,12,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(16,4,165,NULL,13,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(17,4,164,NULL,14,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(18,4,142,NULL,15,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(19,4,167,NULL,16,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(20,4,161,NULL,17,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(21,4,144,NULL,18,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(22,4,160,NULL,19,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(23,4,127,NULL,20,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(24,4,166,NULL,21,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(25,4,114,NULL,22,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(26,4,192,NULL,23,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(27,4,111,NULL,24,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(28,4,189,NULL,25,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(29,4,117,NULL,26,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(30,4,195,NULL,27,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(31,4,120,NULL,28,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(32,4,199,NULL,29,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(33,4,106,NULL,30,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(34,4,121,NULL,31,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(35,4,204,NULL,32,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(36,4,170,NULL,33,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(37,4,171,NULL,34,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(38,4,169,NULL,35,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(39,4,163,NULL,36,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(40,4,123,NULL,37,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(41,4,207,NULL,38,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(42,4,124,NULL,39,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(43,4,162,NULL,40,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(44,4,208,NULL,41,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(45,4,185,NULL,42,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(46,4,113,NULL,43,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(47,4,191,NULL,44,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(48,4,179,NULL,45,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(49,4,137,NULL,46,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(50,4,138,NULL,47,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(51,4,110,NULL,48,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(52,4,188,NULL,49,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(53,4,175,NULL,50,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(54,4,203,NULL,51,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(55,4,173,NULL,52,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(56,4,90,NULL,53,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(57,4,150,NULL,54,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(58,4,89,NULL,55,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(59,4,149,NULL,56,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(60,4,88,NULL,57,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(61,4,148,NULL,58,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(62,4,87,NULL,59,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(63,4,147,NULL,60,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(64,4,86,NULL,61,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(65,4,146,NULL,62,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(66,4,141,NULL,63,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(67,4,139,NULL,64,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(68,4,140,NULL,65,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(69,4,180,NULL,66,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(70,4,108,NULL,67,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(71,4,181,NULL,68,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(72,4,182,NULL,69,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(73,4,109,NULL,70,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(74,4,184,NULL,71,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(75,4,176,NULL,72,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(76,4,152,NULL,73,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(77,4,202,NULL,74,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(78,4,153,NULL,75,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(79,4,119,NULL,76,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(80,4,197,NULL,77,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(81,4,198,NULL,78,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(82,4,134,NULL,79,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(83,4,85,NULL,80,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(84,4,145,NULL,81,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(85,4,157,NULL,82,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(86,4,136,NULL,83,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(87,4,133,NULL,84,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(88,4,122,NULL,85,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(89,4,205,NULL,86,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(90,4,159,NULL,87,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(91,4,135,NULL,88,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(92,4,154,NULL,89,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(93,4,118,NULL,90,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(94,4,196,NULL,91,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(95,4,94,NULL,92,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(96,4,158,NULL,93,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(97,4,93,NULL,94,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(98,4,156,NULL,95,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(99,4,92,NULL,96,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(100,4,155,NULL,97,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(101,4,91,NULL,98,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(102,4,151,NULL,99,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(103,4,187,NULL,100,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(104,4,206,NULL,101,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(105,4,143,NULL,102,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(106,4,172,NULL,103,1,NULL,'2025-07-07 20:16:19');
INSERT INTO menu_menu_items VALUES(107,4,186,NULL,104,1,NULL,'2025-07-07 20:16:19');
CREATE TABLE menu_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
    UNIQUE(menu_id, category_name)
);
INSERT INTO menu_categories VALUES(9,1,'Main',1);
INSERT INTO menu_categories VALUES(10,1,'Sides',2);
INSERT INTO menu_categories VALUES(11,1,'Salads',3);
INSERT INTO menu_categories VALUES(12,1,'Sauces',4);
INSERT INTO menu_categories VALUES(13,1,'Toppings',5);
INSERT INTO menu_categories VALUES(14,1,'Ingredient',6);
INSERT INTO menu_categories VALUES(15,1,'Uncategorized',7);
INSERT INTO menu_categories VALUES(16,2,'Main',1);
INSERT INTO menu_categories VALUES(17,2,'Sides',2);
INSERT INTO menu_categories VALUES(18,2,'Salads',3);
INSERT INTO menu_categories VALUES(19,2,'Sauces',4);
INSERT INTO menu_categories VALUES(20,2,'Toppings',5);
INSERT INTO menu_categories VALUES(21,2,'Ingredient',6);
INSERT INTO menu_categories VALUES(22,2,'Uncategorized',7);
INSERT INTO menu_categories VALUES(23,3,'Main',1);
INSERT INTO menu_categories VALUES(24,3,'Sides',2);
INSERT INTO menu_categories VALUES(25,3,'Salads',3);
INSERT INTO menu_categories VALUES(26,3,'Sauces',4);
INSERT INTO menu_categories VALUES(27,3,'Toppings',5);
INSERT INTO menu_categories VALUES(28,3,'Ingredient',6);
INSERT INTO menu_categories VALUES(29,3,'Uncategorized',7);
INSERT INTO sqlite_sequence VALUES('recipes',132);
INSERT INTO sqlite_sequence VALUES('menu_items',208);
INSERT INTO sqlite_sequence VALUES('vendors',25);
INSERT INTO sqlite_sequence VALUES('inventory',911);
INSERT INTO sqlite_sequence VALUES('recipe_ingredients',554);
INSERT INTO sqlite_sequence VALUES('vendor_products',233);
INSERT INTO sqlite_sequence VALUES('menu_versions',3);
INSERT INTO sqlite_sequence VALUES('units',38);
INSERT INTO sqlite_sequence VALUES('ingredient_densities',39);
INSERT INTO sqlite_sequence VALUES('vendor_descriptions',673);
INSERT INTO sqlite_sequence VALUES('recipes_notes',31);
INSERT INTO sqlite_sequence VALUES('recipe_components',28);
INSERT INTO sqlite_sequence VALUES('recipe_notes',9);
INSERT INTO sqlite_sequence VALUES('menus',6);
INSERT INTO sqlite_sequence VALUES('menu_categories',29);
INSERT INTO sqlite_sequence VALUES('menu_menu_items',107);
CREATE VIEW menu_version_comparison AS
            SELECT 
                mi.item_name,
                mi.menu_group,
                mi.menu_price,
                mi.food_cost,
                mi.food_cost_percent,
                mi.gross_profit,
                mv.version_name,
                mv.is_active,
                r.recipe_name
            FROM menu_items mi
            JOIN menu_versions mv ON mi.version_id = mv.id
            LEFT JOIN recipes r ON mi.recipe_id = r.id
            ORDER BY mv.version_name, mi.menu_group, mi.item_name;
CREATE TRIGGER update_inventory_last_purchase
            AFTER UPDATE OF last_purchased_date, last_purchased_price 
            ON vendor_products
            WHEN NEW.is_primary = 1
            BEGIN
                UPDATE inventory
                SET 
                    last_purchased_date = NEW.last_purchased_date,
                    last_purchased_price = NEW.last_purchased_price,
                    current_price = NEW.vendor_price,
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = NEW.inventory_id;
            END;
CREATE INDEX idx_inventory_description ON inventory(item_description);
CREATE INDEX idx_recipes_name ON recipes(recipe_name);
CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_menu_items_group ON menu_items(menu_group);
CREATE INDEX idx_vendor_products_inventory 
            ON vendor_products(inventory_id)
        ;
CREATE INDEX idx_vendor_products_vendor 
            ON vendor_products(vendor_id)
        ;
CREATE INDEX idx_vendor_products_active 
            ON vendor_products(is_active)
        ;
CREATE INDEX idx_units_symbol ON units(symbol);
CREATE INDEX idx_units_dimension ON units(dimension);
CREATE INDEX idx_ingredient_equivalents ON ingredient_unit_equivalents(inventory_id);
CREATE INDEX idx_ingredient_densities_name 
                ON ingredient_densities(ingredient_name)
            ;
CREATE INDEX idx_menu_menu_items_menu_id ON menu_menu_items(menu_id);
CREATE INDEX idx_menu_menu_items_item_id ON menu_menu_items(menu_item_id);
CREATE INDEX idx_menu_categories_menu_id ON menu_categories(menu_id);
COMMIT;
