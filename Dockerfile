# Bắt đầu từ image PHP 5.6 với Apache (thay vì 7.4)
FROM php:5.6-apache

# Cài đặt extension "mysql" cũ và cả "mysqli" mới (để phòng trường hợp code dùng lẫn lộn)
RUN docker-php-ext-install mysql mysqli
