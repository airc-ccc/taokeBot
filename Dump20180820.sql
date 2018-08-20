-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: localhost    Database: taojin_bot
-- ------------------------------------------------------
-- Server version	5.5.5-10.1.31-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `taojin_current_log`
--

DROP TABLE IF EXISTS `taojin_current_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taojin_current_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT 'å¾®ä¿¡æœºå™¨äºº',
  `username` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '0' COMMENT 'æçŽ°äºº',
  `amount` float(11,2) NOT NULL DEFAULT '1.00' COMMENT 'æçŽ°é‡‘é¢',
  `create_time` int(11) NOT NULL COMMENT 'æçŽ°æ—¶é—´',
  `puid` varchar(255) CHARACTER SET utf8 NOT NULL,
  `bot_puid` varchar(255) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_get_orders`
--

DROP TABLE IF EXISTS `taojin_get_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taojin_get_orders` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `order_id` bigint(20) NOT NULL COMMENT '订单id',
  `good_id` bigint(20) NOT NULL COMMENT '商品id',
  `good_name` varchar(255) NOT NULL COMMENT '商品名称',
  `good_price` float NOT NULL COMMENT '商品单价',
  `good_num` int(11) NOT NULL COMMENT '商品数量',
  `order_price` float NOT NULL COMMENT '订单付款价格',
  `order_status` tinyint(1) NOT NULL COMMENT '订单状态, ''订单结算'': 1, ''订单付款'': 2, ''订单失效'': 3, ''订单成功'': 4  5 售后',
  `order_source` tinyint(1) NOT NULL COMMENT '订单来源',
  `order_commission` float NOT NULL DEFAULT '0' COMMENT '订单佣金',
  `create_time` varchar(50) NOT NULL COMMENT '订单创建时间',
  `settlement_time` varchar(50) DEFAULT NULL COMMENT '订单结算时间',
  `bot_puid` varchar(100) NOT NULL COMMENT '机器人puid',
  `pdd_order_id` varchar(100) DEFAULT NULL COMMENT '拼多多id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=298 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_good_info`
--

DROP TABLE IF EXISTS `taojin_good_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_group_message`
--

DROP TABLE IF EXISTS `taojin_group_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taojin_group_message` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人名称',
  `groupid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '群id',
  `groupname` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '群名称',
  `create_time` int(11) NOT NULL,
  `bot_puid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '机器人puid',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_order`
--

DROP TABLE IF EXISTS `taojin_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taojin_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL,
  `username` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT 'ç”¨æˆ·å',
  `order_id` char(32) CHARACTER SET utf8 NOT NULL COMMENT 'è®¢å•å·',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1 未完成 2 已完成 3 错误的订单',
  `completion_time` varchar(50) NOT NULL,
  `order_source` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'è®¢å•æ¥æºï¼š1ï¼Œäº¬ä¸œ 2ï¼Œæ·˜å®',
  `puid` varchar(255) CHARACTER SET utf8 NOT NULL,
  `bot_puid` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `pdd_order_id` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `order_price` float DEFAULT NULL COMMENT '订单金额',
  `total_commission_rate` float DEFAULT NULL COMMENT '佣金比例',
  `total_commission_fee` float DEFAULT NULL COMMENT '用户返利',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_order_info`
--

DROP TABLE IF EXISTS `taojin_order_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taojin_order_info` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `bot_puid` varchar(255) NOT NULL,
  `skuid` int(32) NOT NULL COMMENT '商品skuid',
  `order_id` int(32) NOT NULL,
  `type` tinyint(1) NOT NULL COMMENT '类型，1 京东 2 淘宝',
  `create_time` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_proxy_info`
--

DROP TABLE IF EXISTS `taojin_proxy_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taojin_proxy_info` (
  `id` int(11) NOT NULL,
  `wx_bot` varchar(255) CHARACTER SET utf8 NOT NULL,
  `realname` varchar(32) CHARACTER SET utf8 DEFAULT NULL COMMENT 'ä»£ç†äººå§“å',
  `wx_bot_number` varchar(32) CHARACTER SET utf8 NOT NULL COMMENT 'æœºå™¨äººçš„å¾®ä¿¡å·',
  `jd_username` int(11) NOT NULL COMMENT 'äº¬ä¸œè”ç›Ÿè´¦å·',
  `jd_password` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT 'äº¬ä¸œè”ç›Ÿå¯†ç ',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_query_record`
--

DROP TABLE IF EXISTS `taojin_query_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
  `type` tinyint(1) NOT NULL COMMENT '1京东 2 淘宝 3 拼多多',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_rebate_log`
--

DROP TABLE IF EXISTS `taojin_rebate_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taojin_user_info`
--

DROP TABLE IF EXISTS `taojin_user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
  `pdd_rebate_amount` float(11,2) NOT NULL DEFAULT '0.00' COMMENT '拼多多返利金额',
  `pdd_order_quantity` int(11) NOT NULL DEFAULT '0' COMMENT '拼多多订单总数',
  `pdd_completed_order` int(11) NOT NULL DEFAULT '0' COMMENT '拼多多订单完成数量',
  `pdd_unfinished_order` int(11) NOT NULL DEFAULT '0' COMMENT '拼多多订单未完成数量',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-08-20 16:36:37
