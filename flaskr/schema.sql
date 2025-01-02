DROP TABLE IF EXISTS `post`;
drop table IF EXISTS `bolasDoBingo`;
drop table IF EXISTS `user`;
CREATE TABLE `user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(255) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL);

create TABLE `bolasDoBingo` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `author_id` INT NOT NULL,
  `bolasDoBingoJson` TEXT NOT NULL,
  `rankingJson` TEXT,
  FOREIGN KEY (`author_id`) REFERENCES `user` (`id`)
);

create TABLE `post` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `author_id` INT NOT NULL,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `title` VARCHAR(255) NOT NULL,
  `body` TEXT NOT NULL,
  FOREIGN KEY (`author_id`) REFERENCES `user` (`id`)
);
