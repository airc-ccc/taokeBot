/*
SQLyog 企业版 - MySQL GUI v8.14 
MySQL - 5.5.5-10.1.31-MariaDB : Database - wxpy_taojin
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`wxpy_taojin` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `wxpy_taojin`;

/*Table structure for table `taojin_current_log` */

DROP TABLE IF EXISTS `taojin_current_log`;

CREATE TABLE `taojin_current_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT 'å¾®ä¿¡æœºå™¨äºº',
  `username` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '0' COMMENT 'æçŽ°äºº',
  `amount` float(11,2) NOT NULL DEFAULT '1.00' COMMENT 'æçŽ°é‡‘é¢',
  `create_time` int(11) NOT NULL COMMENT 'æçŽ°æ—¶é—´',
  `puid` varchar(255) CHARACTER SET utf8 NOT NULL,
  `bot_puid` varchar(255) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

/*Data for the table `taojin_current_log` */

insert  into `taojin_current_log`(`id`,`wx_bot`,`username`,`amount`,`create_time`,`puid`,`bot_puid`) values (1,'彭涛','彭波',0.30,1526126393,'77c74a5f','389a91e9');

/*Table structure for table `taojin_good_info` */

DROP TABLE IF EXISTS `taojin_good_info`;

CREATE TABLE `taojin_good_info` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL,
  `skuid` bigint(20) NOT NULL COMMENT 'skuid',
  `title` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '商品title',
  `image` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '商品图片',
  `price` float NOT NULL COMMENT '商品原价',
  `rebate` float NOT NULL COMMENT '返利价格',
  `yhq_price` int(11) NOT NULL DEFAULT '0' COMMENT '优惠券价格',
  `coupon_price` float NOT NULL DEFAULT '0' COMMENT '券后价',
  `shoturl` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '商品购买链接',
  `shotcouponurl` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '0' COMMENT '优惠券链接',
  `status` tinyint(1) NOT NULL COMMENT '商品状态，1 未发送，2 已发送',
  `create_time` int(11) NOT NULL,
  `bot_puid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人puid',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

/*Data for the table `taojin_good_info` */

/*Table structure for table `taojin_group_message` */

DROP TABLE IF EXISTS `taojin_group_message`;

CREATE TABLE `taojin_group_message` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人名称',
  `groupid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '群id',
  `groupname` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '群名称',
  `create_time` int(11) NOT NULL,
  `bot_puid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人puid',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

/*Data for the table `taojin_group_message` */

/*Table structure for table `taojin_order` */

DROP TABLE IF EXISTS `taojin_order`;

CREATE TABLE `taojin_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL,
  `username` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT 'ç”¨æˆ·å',
  `order_id` char(32) CHARACTER SET utf8 NOT NULL COMMENT 'è®¢å•å·',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1 未完成 2 已完成',
  `completion_time` int(11) NOT NULL,
  `order_source` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'è®¢å•æ¥æºï¼š1ï¼Œäº¬ä¸œ 2ï¼Œæ·˜å®',
  `puid` varchar(255) CHARACTER SET utf8 NOT NULL,
  `bot_puid` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

/*Data for the table `taojin_order` */

/*Table structure for table `taojin_order_info` */

DROP TABLE IF EXISTS `taojin_order_info`;

CREATE TABLE `taojin_order_info` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `bot_puid` varchar(255) NOT NULL,
  `skuid` int(32) NOT NULL COMMENT '商品skuid',
  `order_id` int(32) NOT NULL,
  `type` tinyint(1) NOT NULL COMMENT '类型，1 京东 2 淘宝',
  `create_time` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `taojin_order_info` */

/*Table structure for table `taojin_proxy_info` */

DROP TABLE IF EXISTS `taojin_proxy_info`;

CREATE TABLE `taojin_proxy_info` (
  `id` int(11) NOT NULL,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL,
  `realname` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT 'ä»£ç†äººå§“å',
  `wx_bot_number` varchar(32) CHARACTER SET utf8 NOT NULL COMMENT 'æœºå™¨äººçš„å¾®ä¿¡å·',
  `jd_username` int(11) NOT NULL COMMENT 'äº¬ä¸œè”ç›Ÿè´¦å·',
  `jd_password` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT 'äº¬ä¸œè”ç›Ÿå¯†ç ',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `taojin_proxy_info` */

/*Table structure for table `taojin_query_record` */

DROP TABLE IF EXISTS `taojin_query_record`;

CREATE TABLE `taojin_query_record` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '微信机器人',
  `skuid` varchar(100) CHARACTER SET utf8 NOT NULL,
  `good_title` varchar(255) CHARACTER SET utf8 NOT NULL,
  `good_price` decimal(10,2) NOT NULL,
  `good_coupon` int(10) DEFAULT NULL,
  `username` varchar(255) CHARACTER SET utf8 NOT NULL,
  `create_time` int(11) NOT NULL,
  `puid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '用户puid',
  `bot_puid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人puid',
  `chatroom` varchar(255) CHARACTER SET utf8 DEFAULT NULL COMMENT '群聊昵称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

/*Data for the table `taojin_query_record` */

insert  into `taojin_query_record`(`id`,`wx_bot`,`skuid`,`good_title`,`good_price`,`good_coupon`,`username`,`create_time`,`puid`,`bot_puid`,`chatroom`) values (105,'彭涛','1892019','Apple iPad mini 4 平板电脑 7.9英寸（128G WLAN版/A8芯片/Retina显示屏/Touch ID技术 MK9P2CH）银色','2498.00',0,'彭波',1526123913,'77c74a5f','389a91e9',NULL),(106,'彭涛','1892019','Apple iPad mini 4 平板电脑 7.9英寸（128G WLAN版/A8芯片/Retina显示屏/Touch ID技术 MK9P2CH）银色','2498.00',0,'彭波',1526123980,'77c74a5f','389a91e9',NULL),(107,'彭涛','1892019','Apple iPad mini 4 平板电脑 7.9英寸（128G WLAN版/A8芯片/Retina显示屏/Touch ID技术 MK9P2CH）银色','2498.00',0,'彭波',1526124088,'77c74a5f','389a91e9',NULL),(108,'彭涛','1892019','Apple iPad mini 4 平板电脑 7.9英寸（128G WLAN版/A8芯片/Retina显示屏/Touch ID技术 MK9P2CH）银色','2498.00',0,'彭波',1526124146,'77c74a5f','389a91e9',NULL),(109,'彭涛','1892019','Apple iPad mini 4 平板电脑 7.9英寸（128G WLAN版/A8芯片/Retina显示屏/Touch ID技术 MK9P2CH）银色','2498.00',0,'彭波',1526124192,'77c74a5f','389a91e9',NULL);

/*Table structure for table `taojin_rebate_log` */

DROP TABLE IF EXISTS `taojin_rebate_log`;

CREATE TABLE `taojin_rebate_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `bot_puid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人的puid',
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人',
  `username` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT 'ç”¨æˆ·',
  `rebate_amount` float(11,2) NOT NULL,
  `type` tinyint(1) NOT NULL COMMENT 'è¿”åˆ©ç±»åž‹ï¼š1æ·»åŠ æœºå™¨äººè¿”åˆ©ï¼Œ2é‚€è¯·äººè¿”åˆ©ï¼Œ3ï¼Œè´­ç‰©è¿”åˆ©ï¼Œ4é‚€è¯·äººè´­ç‰©è¿”åˆ©',
  `create_time` int(11) NOT NULL COMMENT 'åˆ›å»ºæ—¶é—´',
  `puid` varchar(255) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=229 DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

/*Data for the table `taojin_rebate_log` */

insert  into `taojin_rebate_log`(`id`,`bot_puid`,`wx_bot`,`username`,`rebate_amount`,`type`,`create_time`,`puid`) values (228,'389a91e9','彭涛','彭波',0.30,1,1526121594,'77c74a5f');

/*Table structure for table `taojin_user_info` */

DROP TABLE IF EXISTS `taojin_user_info`;

CREATE TABLE `taojin_user_info` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wx_bot` varchar(255) NOT NULL COMMENT '机器人',
  `puid` varchar(255) NOT NULL COMMENT '用户唯一标示',
  `sex` tinyint(1) NOT NULL DEFAULT '1' COMMENT '性别 1男 2女',
  `nickname` varchar(255) NOT NULL COMMENT '用户昵称',
  `lnivt_code` varchar(255) NOT NULL DEFAULT '0' COMMENT '邀请码',
  `total_rebate_amount` float(11,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '总返利金额',
  `jd_rebate_amount` float(11,2) NOT NULL DEFAULT '0.00' COMMENT '京东返利金额',
  `taobao_rebate_amount` float(11,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '淘宝返利金额',
  `withdrawals_amount` float(11,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '可提现金额',
  `save_money` float(11,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '累计总金额',
  `order_quantity` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '订单总数',
  `jd_order_quantity` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '京东订单总数',
  `taobao_order_quantity` int(11) NOT NULL DEFAULT '0' COMMENT '淘宝订单总数',
  `jd_completed_order` int(11) NOT NULL DEFAULT '0' COMMENT '京东订单完成数量',
  `taobao_completed_order` int(11) NOT NULL DEFAULT '0' COMMENT '淘宝订单完成数量',
  `jd_unfinished_order` int(11) NOT NULL DEFAULT '0' COMMENT '京东未完成订单数',
  `lnivter` varchar(255) NOT NULL DEFAULT '0' COMMENT '邀请人',
  `taobao_unfinished_order` int(11) NOT NULL DEFAULT '0' COMMENT '淘宝未完成订单数',
  `friends_rebate` float(11,2) NOT NULL DEFAULT '0.00' COMMENT '好友返利',
  `friends_number` int(11) NOT NULL DEFAULT '0' COMMENT '好友数量 （邀请过的人数）',
  `create_time` int(11) NOT NULL DEFAULT '0' COMMENT '创建时间',
  `update_time` int(11) DEFAULT NULL COMMENT '修改时间',
  `remarkname` varchar(255) NOT NULL COMMENT '用户备注',
  `bot_puid` varchar(255) NOT NULL COMMENT '机器人的puid',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

/*Data for the table `taojin_user_info` */

insert  into `taojin_user_info`(`id`,`wx_bot`,`puid`,`sex`,`nickname`,`lnivt_code`,`total_rebate_amount`,`jd_rebate_amount`,`taobao_rebate_amount`,`withdrawals_amount`,`save_money`,`order_quantity`,`jd_order_quantity`,`taobao_order_quantity`,`jd_completed_order`,`taobao_completed_order`,`jd_unfinished_order`,`lnivter`,`taobao_unfinished_order`,`friends_rebate`,`friends_number`,`create_time`,`update_time`,`remarkname`,`bot_puid`) values (49,'彭涛','77c74a5f',1,'彭波','77c74a5f',0.30,0.00,0.00,0.00,0.00,0,0,0,0,0,0,'0',0,0.00,0,1526121594,1526126393,'2018512_4_B_0','389a91e9');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
