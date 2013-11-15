/*
author:KK
*/

create database if not exists 91waijiao_mon_db;
use 91waijiao_mon_db;

/*drop all tables*/
drop table if exists t_account;
drop table if exists t_packetlost;

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
table:t-packetlost
*/
create table t_packetlost
(
    aid bigint not null AUTO_INCREMENT,
    classid int not null,
    usrid int not null,
    usrdbid int not null,
    recordtime DATETIME not null,
    count int not null,
    primary key (aid)
);
