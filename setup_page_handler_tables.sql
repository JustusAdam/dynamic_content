# creates tables used by page handlers, this file is temporary and will not be in a final version
create table entity (id int unsigned not null auto_increment unique primary key comment 'primary ID used to indentify pages', content_type int not null comment 'content type for given page, used to identify fields', description text comment 'human readable description');
