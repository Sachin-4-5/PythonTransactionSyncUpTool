-- =======================================
-- Author: Sachin Kumar
-- Created on: 2025-08-30
-- Purpose: Db Script for PythonConsoleApp
-- Database & Table & Stored Proc scripts.
-- =======================================


CREATE TABLE dbo.tbl_RerateRecon 
(
    AsOfDate varchar(20),
	TradeNumber int,
	Bond varchar(50),
	Ticket varchar(50),
	TradeDate varchar(20),
	MaturityDate varchar(20),
	SettleDate varchar(20),
	InitialRate decimal(9,2),
	CurrentRate decimal(9,2),
	APIRate decimal(9,2),
	HasRerateUDF varchar(1),
	IsRerated varchar(1),
	EffectiveDate varchar(20)
);