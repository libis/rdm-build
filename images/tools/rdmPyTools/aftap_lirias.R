# Analysis of lirias datafile
#
# Pieter De Veuster
#
#############################
library(readr)
library(doBy)
library(dplyr)
library(stringi)
library(plotrix)
library(readr)
library(ggplot2)
library(reshape)

saveDir <- 'c:/temp/rdm'
#READ Users FILE
inFile <- "C:/temp/rdm/aftap_lirias.csv"
allusers <- read_delim(inFile,delim=",",quote="\"",trim_ws = TRUE)


#' uids<-data.frame(unique(lirias$Au))
#' write.csv(x=uids, file = 'c:/temp/unrs.txt',row.names=FALSE,quote=FALSE,col.names=FALSE)
#' 
#' notfoundKul<-data.frame(unique(filter(liriasAuthOrgKulLvl,is.na(KulOuLevel))$LiriasId))
#' notfoundAu<-data.frame(unique(filter(liriasAuthOrgKulLvl,is.na(AuOu))$LiriasId))
#' write.csv(notfound, "c:/temp/notfound.csv", col.names = NA, row.names = FALSE, quote = FALSE)
#' 
#' lirnotfound<-filter(liriasAuthOrgKulLvl,!is.na(OuLevel.y))
#' unique(lirnotfound$LiriasId)
#' unique(lirias$LiriasId)
#' 
#' #search for publications that do not have a valid organisation attached
#' idsNoNA<-unique(filter(liriasAuthOrgLvl,!(is.na(AuOu)))$LiriasId)
#' idsNA<-unique(filter(liriasAuthOrgLvl,is.na(AuOu))$LiriasId)
#' idsToComplete<-setdiff(idsNA,idsNoNA)
#' 
#' #per document stats, include maximum organisational level
#' byId <- group_by(liriasOrgLevel,LiriasId,Au)
#' idCnt<- arrange(summarize(byId, cntOus = n_distinct(Ou),
#'                           cntaus = n_distinct(Au),
#'                           maxOuLevel = max(OuLevel,na.rm=TRUE)))
#' summary(idCnt)
#' 
#' byOu<-group_by(lirias,Ou)
#' p<-arrange(summarize(byOu,cntPubl=n_distinct(LiriasId)),-cntPubl)
#' cutoffupper<-10000
#' cutofflower<-0
#' filter(summarize(byOu,cntPubl=n_distinct(LiriasId)),cntPubl>=cutoffupper)
#' filter(summarize(byOu,cntPubl=n_distinct(LiriasId)),cntPubl<=cutofflower)
#' retainedOu<-filter(summarize(byOu,cntPubl=n_distinct(LiriasId)),cntPubl<cutoffupper & cntPubl>cutofflower)$Ou
#' 
#' triage<-filter(lirias,Ou %in% retainedOu)
#' n_distinct(triage$LiriasId)
#' setdiff(lirias$LiriasId,triage$LiriasId)
#' 
#' #20200406
#' byOrg<-group_by(liriasAuthOrgKulLvl,Ou,OuDesc,KulOuLevel)
#' Ocnt<-summarize(byOrg,Aant=n_distinct(LiriasId))
#' keuzes<-filter(Ocnt,Aant > 300 & Aant < 500 & KulOuLevel > 3)
#' n_distinct(filter(lirias,Ou %in% (keuzes$Ou))$LiriasId)
#' #View(keuzes)
#' docnumbers<-data.frame(unique(filter(lirias,Ou %in% (keuzes$Ou))$LiriasId))
#' write.csv(docnumbers,'c:/temp/docnumbers.csv', row.names = FALSE)
#' 
#' docOus<-distinct(select(filter(lirias,Ou %in% (keuzes$Ou)),LiriasId,Ou))
#' write.csv(docOus,'c:/temp/docOus.csv', row.names = FALSE)
#' unique(docOus$Ou)
#' 
#' #???20200415
#' #'50000453','52445375','50000633','50464358','50000695','50000628','50000455','50000673','50000699','50000382','52407542','50514864','50000218','50000532','50000580','50000439','50620092','50019227','50000744','50487173','52407560','50463906','52607307','52745149','50000637','50000434','50518200'


















