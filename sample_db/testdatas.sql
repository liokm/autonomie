INSERT into egw_accounts  (`account_lid`, `account_pwd`, `account_firstname` ,`account_lastname`, `account_email`) VALUES ('user1_login', '24c9e15e52afc47c225b757e7bee1f9d', 'user1_firstname', 'user1_lastname', 'user1@test.fr');
INSERT into coop_company (`name`, `object`, `phone`, `creationDate`, `updateDate`, `IDGroup`, `IDEGWUser`, `logo`, `header`) VALUES ('company1', 'Company of user1', '0457858585', '1286804741', '1286804741', '0', '0', 'logo.png', 'header.png');
INSERT into coop_company_employee (`IDCompany`, `IDEmployee`) VALUES ('1', '1');
INSERT into coop_customer (`code`, `name`, `creationDate`, `updateDate`, `IDCompany`) VALUES ('C001', 'Client1', '1286804741', '1286804741', '1');
INSERT into coop_project (`name`, `customerCode`, `code`, `definition`, `creationDate`, `updateDate`, `status`, `IDCompany`) VALUES ('Projet de test', 'C001', 'P001', 'Projet de test', '1286804741', '1286804741', '', '1');

INSERT INTO `egw_config` VALUES ('phpgwapi','site_title','Test Autonomie'), ('phpgwapi','hostname','autonomie.localhost'), ('coopagest','coop_estimationfooter','Après signature du client, ce devis prendra valeur de bon de commande dès son retour par courrier ou validation par mail en précisant le N° de devis et le montant.\r\n\r\nCachet de l\'entreprise, Nom, fonction et signature du client précédée de la mention « bon pour accord ».\r\n\r\n'),('coopagest','coop_pdffootertitle','Centre de facturation PORT PARALLELE SCOP/SARL à  capital variable'),('coopagest','coop_pdffootercourse','Organisme de formation N° de déclaration d\'activité au titre de la FPC : 11 75 4210875'),('coopagest','coop_pdffootertext','RCS PARIS 492 196 209 - SIRET 492 196 209 000 26 - Code naf 7022Z TVA INTRACOM : FR28492196209\r\nSiège social : 70, rue Amelot 75011 Paris - tel: 00 (33) 1 53 19 96 15'),('coopagest','coop_administratorgroup','-10'),('coopagest','coop_employeesgroup','-135'),('coopagest','coop_interviewergroup','315'),('coopagest','coop_specialuser','134'),('coopagest','coop_estimationaddress','Port Parallèle\r\n70, rue Amelot \r\n75011 Paris'),('coopagest','coop_invoicepayment','Par chèque libellé à l\'ordre de : Port Parallèle Production/ %ENTREPRENEUR% \r\nOu par virement sur le compte de Port Parallèle Production/ %ENTREPRENEUR%\r\nCrédit coopératif Paris gare de l\'Est \r\nRIB : %RIB%\r\nIBAN : %IBAN%\r\nBIC : CCOPFRPPXXX'),('wiki','allow_anonymous','True'),('coopagest','coop_invoicelate','Tout retard de paiement entraînera à titre de clause pénale, conformément à la loi 92.1442 du 31 décembre 1992, une pénalité égale à un taux d\'intérêt équivalent à  une fois et demi le taux d\'intérêt légal en vigueur à cette échéance.'), ('phpgwapi','files_dir','/var/intranet_files/files');
