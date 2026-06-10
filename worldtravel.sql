-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1
-- Время создания: Июн 10 2026 г., 08:03
-- Версия сервера: 10.4.32-MariaDB
-- Версия PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `worldtravel`
--

-- --------------------------------------------------------

--
-- Структура таблицы `bot_settings`
--

CREATE TABLE `bot_settings` (
  `key_name` varchar(64) NOT NULL,
  `value` varchar(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Дамп данных таблицы `bot_settings`
--

INSERT INTO `bot_settings` (`key_name`, `value`) VALUES
('paused', '0');

-- --------------------------------------------------------

--
-- Структура таблицы `chat_history`
--

CREATE TABLE `chat_history` (
  `id` bigint(20) NOT NULL,
  `chat_id` varchar(128) NOT NULL,
  `role` enum('user','assistant') NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `chat_sessions`
--

CREATE TABLE `chat_sessions` (
  `chat_id` varchar(128) NOT NULL,
  `greeted` tinyint(1) NOT NULL DEFAULT 0,
  `last_seen` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `tours`
--

CREATE TABLE `tours` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `destination` varchar(128) NOT NULL,
  `country` varchar(128) NOT NULL,
  `region` varchar(64) NOT NULL DEFAULT 'Мир' COMMENT 'Европа, Азия, Ближний Восток, Африка, СНГ, Америка, Океания',
  `duration` varchar(64) NOT NULL DEFAULT '7 дней / 6 ночей',
  `price` int(11) NOT NULL COMMENT 'Цена в USD',
  `old_price` int(11) DEFAULT NULL COMMENT 'Старая цена (зачёркнутая) для акций',
  `description` text NOT NULL,
  `includes` text DEFAULT NULL COMMENT 'Что входит в тур',
  `hotel_stars` tinyint(4) DEFAULT 4,
  `tour_type` varchar(64) NOT NULL DEFAULT 'Классический' COMMENT 'Классический, Авторский, Пляжный, Экстрим, Гастро, Романтический, Экскурсионный, Круиз',
  `is_hot` tinyint(1) NOT NULL DEFAULT 0,
  `available` tinyint(1) NOT NULL DEFAULT 1,
  `photo_url` varchar(512) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Дамп данных таблицы `tours`
--

INSERT INTO `tours` (`id`, `title`, `destination`, `country`, `region`, `duration`, `price`, `old_price`, `description`, `includes`, `hotel_stars`, `tour_type`, `is_hot`, `available`, `photo_url`, `created_at`) VALUES
(1, '🗼 Романтический Париж', 'Париж', 'Франция', 'Европа', '5 дней / 4 ночи', 1290, 1490, 'Город любви, круассанов и Эйфелевой башни. Прогулки по Монмартру, круиз по Сене, дегустация вин и сыров', 'Авиаперелёт, отель 4★, завтраки, трансфер, экскурсия по Парижу, круиз по Сене', 4, 'Романтический', 1, 1, 'https://i.ibb.co/gMnNQyNr/paris.jpg', '2026-06-10 06:03:19'),
(2, '🏛️ Вечный Рим — Колизей и Ватикан', 'Рим', 'Италия', 'Европа', '6 дней / 5 ночей', 1150, NULL, 'Колизей, Ватикан, фонтан Треви, пицца и паста в сердце Италии. Погружение в древнюю историю!', 'Авиаперелёт, отель 4★, завтраки, трансфер, экскурсия по Риму и Ватикану', 4, 'Экскурсионный', 0, 1, 'https://i.ibb.co/nqXKcjh3/rome.jpg', '2026-06-10 06:03:19'),
(3, '🎭 Прага — Сказка Средневековья', 'Прага', 'Чехия', 'Европа', '5 дней / 4 ночи', 890, NULL, 'Карлов мост, Пражский Град, чешское пиво и трдельник. Город, где время остановилось', 'Авиаперелёт, отель 3★, завтраки, трансфер, обзорная экскурсия', 3, 'Экскурсионный', 0, 1, 'https://i.ibb.co/DfrhSRKB/prague.jpg', '2026-06-10 06:03:19'),
(4, '🎡 Барселона — Гауди и Море', 'Барселона', 'Испания', 'Европа', '7 дней / 6 ночей', 1380, 1580, 'Саграда Фамилия, парк Гуэль, Ла Рамбла, пляж Барселонета. Архитектура + отдых на море!', 'Авиаперелёт, отель 4★, завтраки, трансфер, экскурсия Гауди-тур, пляж', 4, 'Классический', 1, 1, 'https://i.ibb.co/35MXKJNH/barcelona.jpg', '2026-06-10 06:03:19'),
(5, '🧱 Берлин — История и Современность', 'Берлин', 'Германия', 'Европа', '5 дней / 4 ночи', 950, NULL, 'Бранденбургские ворота, остатки стены, музейный остров, бурная ночная жизнь', 'Авиаперелёт, отель 3★, завтраки, трансфер, обзорная экскурсия, музейный pass', 3, 'Экскурсионный', 0, 1, 'https://i.ibb.co/twTxY6MY/berlin.jpg', '2026-06-10 06:03:19'),
(6, '🌷 Амстердам — Каналы и Свобода', 'Амстердам', 'Нидерланды', 'Европа', '4 дня / 3 ночи', 980, NULL, 'Каналы, музей Ван Гога, тюльпаны, велосипеды и уникальная атмосфера', 'Авиаперелёт, отель 3★, завтраки, трансфер, круиз по каналам', 3, 'Классический', 0, 1, 'https://i.ibb.co/Z18FWCZ2/amsterdam.jpg', '2026-06-10 06:03:19'),
(7, '🎵 Вена — Вальс Империи', 'Вена', 'Австрия', 'Европа', '5 дней / 4 ночи', 1100, NULL, 'Шёнбрунн, опера, Захер-торт, венские кофейни. Город музыки и императоров', 'Авиаперелёт, отель 4★, завтраки, трансфер, экскурсия + билет в оперу', 4, 'Классический', 0, 1, 'https://i.ibb.co/kpX57Dj/vienna.jpg', '2026-06-10 06:03:19'),
(8, '🏄 Лиссабон — Край Европы', 'Лиссабон', 'Португалия', 'Европа', '6 дней / 5 ночей', 1050, NULL, 'Трамвай 28, Белен, пастеиш-де-ната, фаду и океан. Тёплый, уютный, незабываемый', 'Авиаперелёт, отель 3★, завтраки, трансфер, обзорная экскурсия', 3, 'Классический', 0, 1, 'https://i.ibb.co/YTFbh9gr/lisbon.jpg', '2026-06-10 06:03:19'),
(9, '🏴 Лондон — Королевская Классика', 'Лондон', 'Великобритания', 'Европа', '5 дней / 4 ночи', 1450, NULL, 'Биг-Бен, Букингемский дворец, Тауэр, Гарри Поттер, английский чай и пабы', 'Авиаперелёт, отель 4★, завтраки, трансфер, обзорная экскурсия, London Eye', 4, 'Экскурсионный', 0, 1, 'https://i.ibb.co/1Jhwqy6Q/UK.jpg', '2026-06-10 06:03:19'),
(10, '🏛️ Афины — Колыбель Цивилизации', 'Афины', 'Греция', 'Европа', '7 дней / 6 ночей', 1200, 1400, 'Акрополь, Партенон, Плака, греческая кухня + 2 дня на островах Саронического залива', 'Авиаперелёт, отель 4★, полупансион, трансфер, экскурсия по Акрополю, паром на острова', 4, 'Классический', 1, 1, 'https://i.ibb.co/KzcrVLZj/athens.jpg', '2026-06-10 06:03:19'),
(11, '❄️ Рейкьявик — Страна Льда и Огня', 'Рейкьявик', 'Исландия', 'Европа', '5 дней / 4 ночи', 1890, NULL, 'Северное сияние, гейзеры, водопады, Голубая лагуна. Другая планета на Земле!', 'Авиаперелёт, отель 3★, завтраки, трансфер, тур Golden Circle, Blue Lagoon', 3, 'Экстрим', 0, 1, 'https://i.ibb.co/fVtH6X9k/reykjavik.jpg', '2026-06-10 06:03:19'),
(12, '🏯 Токио — Будущее Уже Здесь', 'Токио', 'Япония', 'Азия', '8 дней / 7 ночей', 1750, 1990, 'Сибуя, Акихабара, храм Мэйдзи, суши и рамен. Традиции + технологии в одном городе', 'Авиаперелёт, отель 4★, завтраки, трансфер, экскурсия по Токио + день в Киото', 4, 'Экскурсионный', 1, 1, 'https://i.ibb.co/9k9nsBB6/tokyo.jpg', '2026-06-10 06:03:19'),
(13, '🐉 Пекин — Великая Стена и Запретный Город', 'Пекин', 'Китай', 'Азия', '7 дней / 6 ночей', 1100, NULL, 'Великая Китайская стена, Запретный город, Храм Неба, утка по-пекински', 'Авиаперелёт, отель 4★, полупансион, трансфер, экскурсии, гид', 4, 'Экскурсионный', 0, 1, 'https://i.ibb.co/prsMCKK2/beijing.jpg', '2026-06-10 06:03:19'),
(14, '🎎 Сеул — K-Pop и Дворцы', 'Сеул', 'Южная Корея', 'Азия', '6 дней / 5 ночей', 1200, NULL, 'Каннамский район, дворец Кёнбоккун, K-Pop, корейское BBQ и уход за кожей', 'Авиаперелёт, отель 4★, завтраки, трансфер, K-Culture тур', 4, 'Авторский', 0, 1, 'https://i.ibb.co/PZXvcP83/seoul.jpg', '2026-06-10 06:03:19'),
(15, '🌴 Пхукет — Тропический Рай', 'Пхукет', 'Таиланд', 'Азия', '10 дней / 9 ночей', 980, 1180, 'Белоснежные пляжи, тайский массаж, острова Пхи-Пхи, ночные рынки и pad thai', 'Авиаперелёт, отель 4★, завтраки, трансфер, экскурсия на Пхи-Пхи', 4, 'Пляжный', 1, 1, 'https://i.ibb.co/C3MdMRJ0/phuket.jpg', '2026-06-10 06:03:19'),
(16, '🦁 Сингапур — Город-Сад Будущего', 'Сингапур', 'Сингапур', 'Азия', '5 дней / 4 ночи', 1350, NULL, 'Marina Bay Sands, Gardens by the Bay, Сентоза, фудкорты и чистейший мегаполис', 'Авиаперелёт, отель 4★, завтраки, трансфер, обзорная экскурсия, Сентоза', 4, 'Классический', 0, 1, 'https://i.ibb.co/pswWgj0/singapore.jpg', '2026-06-10 06:03:19'),
(17, '🛕 Бангкок — Храмы и Стритфуд', 'Бангкок', 'Таиланд', 'Азия', '7 дней / 6 ночей', 850, NULL, 'Ват Арун, Большой дворец, плавучие рынки, тук-туки и лучший стритфуд в мире', 'Авиаперелёт, отель 3★, завтраки, трансфер, экскурсия по храмам + рынкам', 3, 'Гастро', 0, 1, 'https://i.ibb.co/mr1MDJHR/bangkok.jpg', '2026-06-10 06:03:19'),
(18, '🏙️ Куала-Лумпур — Башни Петронас', 'Куала-Лумпур', 'Малайзия', 'Азия', '6 дней / 5 ночей', 920, NULL, 'Башни Петронас, Бату-Кейвз, Чайнатаун, дуриан и невероятный микс культур', 'Авиаперелёт, отель 4★, завтраки, трансфер, обзорная экскурсия', 4, 'Классический', 0, 1, 'https://i.ibb.co/bgq9Lt2c/kualalumpur.jpg', '2026-06-10 06:03:19'),
(19, '🕌 Стамбул — Между Двух Миров', 'Стамбул', 'Турция', 'Ближний Восток', '5 дней / 4 ночи', 690, 850, 'Айя-София, Голубая мечеть, Гранд-Базар, Босфор, турецкий чай и кебабы', 'Авиаперелёт, отель 4★, завтраки, трансфер, обзорная экскурсия, круиз по Босфору', 4, 'Экскурсионный', 1, 1, 'https://i.ibb.co/xKkDQ2Lg/istanbul.jpg', '2026-06-10 06:03:19'),
(20, '🏜️ Дубай — Город Рекордов', 'Дубай', 'ОАЭ', 'Ближний Восток', '6 дней / 5 ночей', 1500, NULL, 'Бурдж-Халифа, Палм-Джумейра, сафари, Gold Souk, аквапарк и роскошь без границ', 'Авиаперелёт, отель 5★, завтраки, трансфер, сафари в пустыне, Бурдж-Халифа', 5, 'Классический', 1, 1, 'https://i.ibb.co/23JXYqJF/dubai.jpg', '2026-06-10 06:03:19'),
(21, '🐫 Каир — Тайны Пирамид', 'Каир', 'Египет', 'Ближний Восток', '7 дней / 6 ночей', 790, NULL, 'Пирамиды Гизы, Сфинкс, Каирский музей, круиз по Нилу, Луксор', 'Авиаперелёт, отель 4★, полупансион, трансфер, экскурсии в Гизу и Луксор', 4, 'Экскурсионный', 0, 1, 'https://i.ibb.co/zTKyWNfh/cairo.jpg', '2026-06-10 06:03:19'),
(22, '🌊 Занзибар — Океан и Специи', 'Занзибар', 'Танзания', 'Африка', '9 дней / 8 ночей', 1350, 1550, 'Бирюзовый океан, белый песок, Stone Town, плантации специй, дайвинг', 'Авиаперелёт, отель 4★, полупансион, трансфер, Spice Tour, снорклинг', 4, 'Пляжный', 1, 1, 'https://i.ibb.co/3m158Rt7/zanzibar.jpg', '2026-06-10 06:03:19'),
(23, '🏺 Марракеш — Ароматы Востока', 'Марракеш', 'Марокко', 'Африка', '5 дней / 4 ночи', 780, NULL, 'Медина, площадь Джемаа-эль-Фна, атласские горы, хаммам и тажин', 'Авиаперелёт, риад 4★, завтраки, трансфер, экскурсия по медине, хаммам', 4, 'Авторский', 0, 1, 'https://i.ibb.co/bjkcxDWz/marrakech.jpg', '2026-06-10 06:03:19'),
(24, '🕌 Самарканд — Жемчужина Шёлкового Пути', 'Самарканд', 'Узбекистан', 'СНГ', '5 дней / 4 ночи', 590, NULL, 'Регистан, Шахи-Зинда, обсерватория Улугбека, плов и восточное гостеприимство', 'Авиаперелёт, отель 3★, полупансион, трансфер, экскурсии по Самарканду', 3, 'Экскурсионный', 0, 1, 'https://i.ibb.co/d0nF1yf0/samarkand.jpg', '2026-06-10 06:03:19'),
(25, '🕌 Бухара — Живая История', 'Бухара', 'Узбекистан', 'СНГ', '4 дня / 3 ночи', 490, NULL, 'Крепость Арк, минарет Калян, торговые купола, бухарский чай и ковры', 'Авиаперелёт, отель 3★, полупансион, трансфер, экскурсии', 3, 'Экскурсионный', 0, 1, 'https://i.ibb.co/mfty7RM/bukhara.jpg', '2026-06-10 06:03:19'),
(26, '🏔️ Иссык-Куль — Горное Море', 'Иссык-Куль', 'Кыргызстан', 'СНГ', '7 дней / 6 ночей', 450, 550, 'Горячее горное озеро, юрты, конные прогулки, каньон Сказка, звёздное небо', 'Трансфер, гостевой дом, полупансион, конная прогулка, каньон Сказка', 3, 'Экстрим', 1, 1, 'https://i.ibb.co/gFt2VJhg/issykkul.jpg', '2026-06-10 06:03:19'),
(27, '🏰 Санкт-Петербург — Северная Венеция', 'Санкт-Петербург', 'Россия', 'СНГ', '5 дней / 4 ночи', 750, NULL, 'Эрмитаж, Петергоф, Невский проспект, разводные мосты и белые ночи', 'Авиаперелёт, отель 4★, завтраки, трансфер, Эрмитаж, Петергоф', 4, 'Экскурсионный', 0, 1, 'https://i.ibb.co/21r45vq3/spb.jpg', '2026-06-10 06:03:19'),
(28, '🕌 Казань — Третья Столица', 'Казань', 'Россия', 'СНГ', '4 дня / 3 ночи', 520, NULL, 'Кремль, мечеть Кул-Шариф, остров Свияжск, чак-чак и эчпочмак', 'Авиаперелёт, отель 3★, завтраки, трансфер, обзорная экскурсия', 3, 'Экскурсионный', 0, 1, 'https://i.ibb.co/hxqZVLPk/kazan.jpg', '2026-06-10 06:03:19'),
(29, '🗽 Нью-Йорк — Город, Который Не Спит', 'Нью-Йорк', 'США', 'Америка', '7 дней / 6 ночей', 2200, NULL, 'Статуя Свободы, Таймс-Сквер, Центральный парк, Broadway, Бруклинский мост', 'Авиаперелёт, отель 4★, завтраки, трансфер, обзорная экскурсия, Broadway шоу', 4, 'Классический', 0, 1, 'https://i.ibb.co/pvDVFtMB/newyork.jpg', '2026-06-10 06:03:19'),
(30, '🏝️ Мальдивы — Рай на Земле', 'Мальдивы', 'Мальдивы', 'Океания', '8 дней / 7 ночей', 2500, 2900, 'Виллы на воде, коралловые рифы, дайвинг с мантами, закаты и полное умиротворение', 'Авиаперелёт, вилла на воде 5★, All Inclusive, трансфер гидроплан, снорклинг', 5, 'Пляжный', 1, 1, 'https://i.ibb.co/jZWLv9Gd/maldives.jpg', '2026-06-10 06:03:19'),
(31, '🍣 Гастро-тур: Бангкок + Пхукет', 'Бангкок — Пхукет', 'Таиланд', 'Азия', '10 дней / 9 ночей', 1250, NULL, 'Кулинарные мастер-классы, ночные рынки, фермы, рыбалка на Андаманском море', 'Авиаперелёт, отели 4★, завтраки, трансфер, 3 мастер-класса, рынок-тур', 4, 'Гастро', 0, 1, 'https://i.ibb.co/mr1MDJHR/bangkok.jpg', '2026-06-10 06:03:27'),
(32, '🧗 Экстрим-тур: Исландия + Треккинг', 'Рейкьявик — Ландманналойгар', 'Исландия', 'Европа', '8 дней / 7 ночей', 2350, NULL, 'Ледниковый хайкинг, вулканы, горячие источники, ночёвка в хижинах, северное сияние', 'Авиаперелёт, горные хижины, питание, снаряжение, гид-проводник', 2, 'Экстрим', 0, 1, 'https://i.ibb.co/fVtH6X9k/reykjavik.jpg', '2026-06-10 06:03:27'),
(33, '💍 Свадебное путешествие: Мальдивы', 'Мальдивы', 'Мальдивы', 'Океания', '10 дней / 9 ночей', 3500, NULL, 'Вилла на воде для двоих, романтический ужин на пляже, спа, дайвинг, закат-круиз', 'Авиаперелёт, вилла 5★, All Inclusive, СПА для двоих, закат-круиз, фотосессия', 5, 'Романтический', 0, 1, 'https://i.ibb.co/jZWLv9Gd/maldives.jpg', '2026-06-10 06:03:27'),
(34, '🚢 Круиз: Средиземное Море', 'Барселона — Рим — Афины', 'Мультистрана', 'Европа', '12 дней / 11 ночей', 2800, 3200, 'Лайнер MSC, заходы в Барселону, Марсель, Рим, Санторини, Афины. Всё включено на борту!', 'Круиз All Inclusive, каюта с балконом, 5 экскурсий на суше, развлечения на борту', 5, 'Круиз', 1, 1, 'https://i.ibb.co/35MXKJNH/barcelona.jpg', '2026-06-10 06:03:27');

-- --------------------------------------------------------

--
-- Структура таблицы `tour_availability`
--

CREATE TABLE `tour_availability` (
  `id` int(11) NOT NULL,
  `tour_id` int(11) NOT NULL,
  `travel_date` date NOT NULL,
  `booked_seats` tinyint(4) NOT NULL DEFAULT 0,
  `max_seats` tinyint(4) NOT NULL DEFAULT 20,
  `booking_id` bigint(20) DEFAULT NULL COMMENT 'Ссылка на tour_bookings',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `tour_bookings`
--

CREATE TABLE `tour_bookings` (
  `id` bigint(20) NOT NULL,
  `chat_id` varchar(128) NOT NULL,
  `sender_phone` varchar(32) NOT NULL,
  `tour_id` int(11) NOT NULL,
  `tour_title` varchar(255) NOT NULL,
  `price` int(11) NOT NULL,
  `num_people` tinyint(4) NOT NULL DEFAULT 1,
  `status` enum('pending','confirmed','rejected','cancelled') NOT NULL DEFAULT 'pending',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `tour_photos`
--

CREATE TABLE `tour_photos` (
  `id` int(11) NOT NULL,
  `tour_id` int(11) NOT NULL,
  `photo_url` varchar(512) NOT NULL,
  `sort_order` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=главное, 2=дополнительное',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `bot_settings`
--
ALTER TABLE `bot_settings`
  ADD PRIMARY KEY (`key_name`);

--
-- Индексы таблицы `chat_history`
--
ALTER TABLE `chat_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_chat_created` (`chat_id`,`created_at`);

--
-- Индексы таблицы `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD PRIMARY KEY (`chat_id`);

--
-- Индексы таблицы `tours`
--
ALTER TABLE `tours`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_region` (`region`),
  ADD KEY `idx_type` (`tour_type`),
  ADD KEY `idx_hot` (`is_hot`),
  ADD KEY `idx_available` (`available`);

--
-- Индексы таблицы `tour_availability`
--
ALTER TABLE `tour_availability`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_tour_date` (`tour_id`,`travel_date`);

--
-- Индексы таблицы `tour_bookings`
--
ALTER TABLE `tour_bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tour_id` (`tour_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_chat` (`chat_id`);

--
-- Индексы таблицы `tour_photos`
--
ALTER TABLE `tour_photos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_tour_order` (`tour_id`,`sort_order`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `chat_history`
--
ALTER TABLE `chat_history`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `tours`
--
ALTER TABLE `tours`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT для таблицы `tour_availability`
--
ALTER TABLE `tour_availability`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `tour_bookings`
--
ALTER TABLE `tour_bookings`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `tour_photos`
--
ALTER TABLE `tour_photos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `tour_availability`
--
ALTER TABLE `tour_availability`
  ADD CONSTRAINT `tour_availability_ibfk_1` FOREIGN KEY (`tour_id`) REFERENCES `tours` (`id`) ON DELETE CASCADE;

--
-- Ограничения внешнего ключа таблицы `tour_bookings`
--
ALTER TABLE `tour_bookings`
  ADD CONSTRAINT `tour_bookings_ibfk_1` FOREIGN KEY (`tour_id`) REFERENCES `tours` (`id`);

--
-- Ограничения внешнего ключа таблицы `tour_photos`
--
ALTER TABLE `tour_photos`
  ADD CONSTRAINT `tour_photos_ibfk_1` FOREIGN KEY (`tour_id`) REFERENCES `tours` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
