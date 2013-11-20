/*
author:KK
*/

create database if not exists 91waijiao_mon_db;
use 91waijiao_mon_db;

/*drop all tables*/
drop table if exists t_account;
drop table if exists t_gc_packetlost;
drop table if exists t_gg_packetlost;

-- /*
-- procedure: getdbversion
-- */
--
-- delimiter
-- drop procedure if exists getdbversion
-- create procedure getdbversion()
-- begin
--      declare version varchar(10);
--      set version = '0.00.0001';
--      select version;
-- end;
-- delimiter;

/*
table:t_account
*/
create table t_account
(
    aid    bigint not null AUTO_INCREMENT,
    accname    varchar(50) binary not null,
    accpass     varchar(50) binary not null,
    primary key (aid)
);

/*
table:t_gc_packetlost
*/
create table t_gc_packetlost
(
    aid bigint not null AUTO_INCREMENT,
    classid int not null,
    usrid int not null,
    usrdbid int not null,
    usrip CHAR(20) not null,
    stream CHAR(20) not null,
    recordtime DATETIME not null,
    count int not null,
    server CHAR(20) not null,
    primary key (aid)
);

/*
table:t_gg_packetlost
*/
create table t_gg_packetlost
(
    aid bigint not null AUTO_INCREMENT,
    mg_sour CHAR(20) not null,
    mg_dest CHAR(20) not null,
    stream CHAR(20) not null,
    recordtime DATETIME not null,
    count int not null,
    primary key (aid)
);