
export class dataApp{
  // Satellite based variables
  public satelliteVariables:string[] = ["Precipitación"];

  // Satellite based products
  public satelliteData =   [

    { Variable: 'Precipitación', Product: 'CHIRPS', Code:"chirps-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'CHIRPS', Code:"chirps-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'CHIRPS', Code:"chirps-annual", Temporal: 'Anual', Tag: "(mm)" },

    { Variable: 'Precipitación', Product: 'CMORPH', Code:"cmorph-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'CMORPH', Code:"cmorph-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'CMORPH', Code:"cmorph-annual", Temporal: 'Anual', Tag: "(mm)" },

    { Variable: 'Precipitación', Product: 'PERSIANN', Code:"persiann-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'PERSIANN', Code:"persiann-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'PERSIANN',Code:"persiann-annual", Temporal: 'Anual', Tag: "(mm)" },

    { Variable: 'Precipitación', Product: 'PERSIANN CCS', Code:"persiann-ccs-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'PERSIANN CCS', Code:"persiann-ccs-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'PERSIANN CCS', Code:"persiann-ccs-annual", Temporal: 'Anual', Tag: "(mm)" },

    { Variable: 'Precipitación', Product: 'PERSIANN PDIR', Code:"persiann-pdir-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'PERSIANN PDIR', Code:"persiann-pdir-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'PERSIANN PDIR', Code:"persiann-pdir-annual", Temporal: 'Anual', Tag: "(mm)" },

    { Variable: 'Precipitación', Product: 'IMERG', Code:"imerg-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'IMERG', Code:"imerg-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'IMERG', Code:"imerg-annual", Temporal: 'Anual', Tag: "(mm)" },

    { Variable: 'Precipitación', Product: 'IMERG Early run', Code:"imerg-early-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'IMERG Early run', Code:"imerg-early-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'IMERG Early run', Code:"imerg-early-annual", Temporal: 'Anual', Tag: "(mm)" },

    { Variable: 'Precipitación', Product: 'IMERG Late run', Code:"imerg-late-daily", Temporal: 'Diaria', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'IMERG Late run', Code:"imerg-late-monthly", Temporal: 'Mensual', Tag: "(mm)" },
    { Variable: 'Precipitación', Product: 'IMERG Late run', Code:"imerg-late-annual", Temporal: 'Anual', Tag: "(mm)" }
  ];

  public provinces:string[] = [
    'AZUAY', 'BOLIVAR', 'CAÑAR', 'CARCHI', 'COTOPAXI','CHIMBORAZO','EL ORO','ESMERALDAS','GUAYAS',
    'IMBABURA','LOJA','LOS RIOS','MANABI', 'MORONA SANTIAGO', 'NAPO', 'PASTAZA', 'PICHINCHA',
    'TUNGURAHUA', 'ZAMORA CHINCHIPE', 'GALAPAGOS', 'SUCUMBIOS', 'ORELLANA', 'SANTO DOMINGO', 'SANTA ELENA']

  public ecuador = [
    { code: '0100', provincia: 'AZUAY', canton: 'TODOS' },
    { code: '0101', provincia: 'AZUAY', canton: 'CUENCA' },
    { code: '0102', provincia: 'AZUAY', canton: 'GIRON' },
    { code: '0103', provincia: 'AZUAY', canton: 'GUALACEO' },
    { code: '0104', provincia: 'AZUAY', canton: 'NABON' },
    { code: '0105', provincia: 'AZUAY', canton: 'PAUTE' },
    { code: '0106', provincia: 'AZUAY', canton: 'PUCARA' },
    { code: '0107', provincia: 'AZUAY', canton: 'SAN FERNANDO' },
    { code: '0108', provincia: 'AZUAY', canton: 'SANTA ISABEL' },
    { code: '0109', provincia: 'AZUAY', canton: 'SIGSIG' },
    { code: '0110', provincia: 'AZUAY', canton: 'OÑA' },
    { code: '0111', provincia: 'AZUAY', canton: 'CHORDELEG' },
    { code: '0112', provincia: 'AZUAY', canton: 'EL PAN' },
    { code: '0113', provincia: 'AZUAY', canton: 'SEVILLA DE ORO' },
    { code: '0114', provincia: 'AZUAY', canton: 'GUACHAPALA' },
    { code: '0115', provincia: 'AZUAY', canton: 'CAMILO PONCE ENRIQUEZ' },

    { code: '0200', provincia: 'BOLIVAR', canton: 'TODOS' },
    { code: '0201', provincia: 'BOLIVAR', canton: 'GUARANDA' },
    { code: '0202', provincia: 'BOLIVAR', canton: 'CHILLANES' },
    { code: '0203', provincia: 'BOLIVAR', canton: 'CHIMBO' },
    { code: '0204', provincia: 'BOLIVAR', canton: 'ECHEANDIA' },
    { code: '0205', provincia: 'BOLIVAR', canton: 'SAN MIGUEL' },
    { code: '0206', provincia: 'BOLIVAR', canton: 'CALUMA' },
    { code: '0207', provincia: 'BOLIVAR', canton: 'LAS NAVES' },

    { code: '0300', provincia: 'CAÑAR', canton: 'TODOS' },
    { code: '0301', provincia: 'CAÑAR', canton: 'AZOGUES' },
    { code: '0302', provincia: 'CAÑAR', canton: 'BIBLIAN' },
    { code: '0303', provincia: 'CAÑAR', canton: 'CAÑAR' },
    { code: '0304', provincia: 'CAÑAR', canton: 'LA TRONCAL' },
    { code: '0305', provincia: 'CAÑAR', canton: 'EL TAMBO' },
    { code: '0306', provincia: 'CAÑAR', canton: 'DELEG' },
    { code: '0307', provincia: 'CAÑAR', canton: 'SUSCAL' },

    { code: '0400', provincia: 'CARCHI', canton: 'TODOS' },
    { code: '0401', provincia: 'CARCHI', canton: 'TULCAN' },
    { code: '0402', provincia: 'CARCHI', canton: 'BOLIVAR' },
    { code: '0403', provincia: 'CARCHI', canton: 'ESPEJO' },
    { code: '0404', provincia: 'CARCHI', canton: 'MIRA' },
    { code: '0405', provincia: 'CARCHI', canton: 'MONTUFAR' },
    { code: '0406', provincia: 'CARCHI', canton: 'SAN PEDRO DE HUACA' },

    { code: '0500', provincia: 'COTOPAXI', canton: 'TODOS' },
    { code: '0501', provincia: 'COTOPAXI', canton: 'LATACUNGA' },
    { code: '0502', provincia: 'COTOPAXI', canton: 'LA MANA' },
    { code: '0503', provincia: 'COTOPAXI', canton: 'PANGUA' },
    { code: '0504', provincia: 'COTOPAXI', canton: 'PUJILI' },
    { code: '0505', provincia: 'COTOPAXI', canton: 'SALCEDO' },
    { code: '0506', provincia: 'COTOPAXI', canton: 'SAQUISILI' },
    { code: '0507', provincia: 'COTOPAXI', canton: 'SIGCHOS' },

    { code: '0600', provincia: 'CHIMBORAZO', canton: 'TODOS' },
    { code: '0601', provincia: 'CHIMBORAZO', canton: 'RIOBAMBA' },
    { code: '0602', provincia: 'CHIMBORAZO', canton: 'ALAUSI' },
    { code: '0603', provincia: 'CHIMBORAZO', canton: 'COLTA' },
    { code: '0604', provincia: 'CHIMBORAZO', canton: 'CHAMBO' },
    { code: '0605', provincia: 'CHIMBORAZO', canton: 'CHUNCHI' },
    { code: '0606', provincia: 'CHIMBORAZO', canton: 'GUAMOTE' },
    { code: '0607', provincia: 'CHIMBORAZO', canton: 'GUANO' },
    { code: '0608', provincia: 'CHIMBORAZO', canton: 'PALLATANGA' },
    { code: '0609', provincia: 'CHIMBORAZO', canton: 'PENIPE' },
    { code: '0610', provincia: 'CHIMBORAZO', canton: 'CUMANDA' },

    { code: '0700', provincia: 'EL ORO', canton: 'TODOS' },
    { code: '0701', provincia: 'EL ORO', canton: 'MACHALA' },
    { code: '0702', provincia: 'EL ORO', canton: 'ARENILLAS' },
    { code: '0703', provincia: 'EL ORO', canton: 'ATAHUALPA' },
    { code: '0704', provincia: 'EL ORO', canton: 'BALSAS' },
    { code: '0705', provincia: 'EL ORO', canton: 'CHILLA' },
    { code: '0706', provincia: 'EL ORO', canton: 'EL GUABO' },
    { code: '0707', provincia: 'EL ORO', canton: 'HUAQUILLAS' },
    { code: '0708', provincia: 'EL ORO', canton: 'MARCABELI' },
    { code: '0709', provincia: 'EL ORO', canton: 'PASAJE' },
    { code: '0710', provincia: 'EL ORO', canton: 'PIÑAS' },
    { code: '0711', provincia: 'EL ORO', canton: 'PORTOVELO' },
    { code: '0712', provincia: 'EL ORO', canton: 'SANTA ROSA' },
    { code: '0713', provincia: 'EL ORO', canton: 'ZARUMA' },
    { code: '0714', provincia: 'EL ORO', canton: 'LAS LAJAS' },

    { code: '0800', provincia: 'ESMERALDAS', canton: 'TODOS' },
    { code: '0801', provincia: 'ESMERALDAS', canton: 'ESMERALDAS' },
    { code: '0802', provincia: 'ESMERALDAS', canton: 'ELOY ALFARO' },
    { code: '0803', provincia: 'ESMERALDAS', canton: 'MUISNE' },
    { code: '0804', provincia: 'ESMERALDAS', canton: 'QUININDE' },
    { code: '0805', provincia: 'ESMERALDAS', canton: 'SAN LORENZO' },
    { code: '0806', provincia: 'ESMERALDAS', canton: 'ATACAMES' },
    { code: '0807', provincia: 'ESMERALDAS', canton: 'RIOVERDE' },
    { code: '0808', provincia: 'ESMERALDAS', canton: 'LA CONCORDIA' },

    { code: '0900', provincia: 'GUAYAS', canton: 'TODOS' },
    { code: '0901', provincia: 'GUAYAS', canton: 'GUAYAQUIL' },
    { code: '0902', provincia: 'GUAYAS', canton: 'ALFREDO BAQUERIZO MORENO (JUJAN)' },
    { code: '0903', provincia: 'GUAYAS', canton: 'BALAO' },
    { code: '0904', provincia: 'GUAYAS', canton: 'BALZAR' },
    { code: '0905', provincia: 'GUAYAS', canton: 'COLIMES' },
    { code: '0906', provincia: 'GUAYAS', canton: 'DAULE' },
    { code: '0907', provincia: 'GUAYAS', canton: 'DURAN' },
    { code: '0908', provincia: 'GUAYAS', canton: 'EL EMPALME' },
    { code: '0909', provincia: 'GUAYAS', canton: 'EL TRIUNFO' },
    { code: '0910', provincia: 'GUAYAS', canton: 'MILAGRO' },
    { code: '0911', provincia: 'GUAYAS', canton: 'NARANJAL' },
    { code: '0912', provincia: 'GUAYAS', canton: 'NARANJITO' },
    { code: '0913', provincia: 'GUAYAS', canton: 'PALESTINA' },
    { code: '0914', provincia: 'GUAYAS', canton: 'PEDRO CARBO' },
    { code: '0916', provincia: 'GUAYAS', canton: 'SAMBORONDON' },
    { code: '0918', provincia: 'GUAYAS', canton: 'SANTA LUCIA' },
    { code: '0919', provincia: 'GUAYAS', canton: 'SALITRE (URBINA JADO)' },
    { code: '0920', provincia: 'GUAYAS', canton: 'SAN JACINTO DE YAGUACHI' },
    { code: '0921', provincia: 'GUAYAS', canton: 'PLAYAS' },
    { code: '0922', provincia: 'GUAYAS', canton: 'SIMON BOLIVAR' },
    { code: '0923', provincia: 'GUAYAS', canton: 'CORONEL MARCELINO MARIDUEÑA' },
    { code: '0925', provincia: 'GUAYAS', canton: 'LOMAS DE SARGENTILLO' },
    { code: '0927', provincia: 'GUAYAS', canton: 'NOBOL' },
    { code: '0928', provincia: 'GUAYAS', canton: 'GENERAL ANTONIO ELIZALDE' },
    { code: '0929', provincia: 'GUAYAS', canton: 'ISIDRO AYORA' },

    { code: '1000', provincia: 'IMBABURA', canton: 'TODOS' },
    { code: '1001', provincia: 'IMBABURA', canton: 'IBARRA' },
    { code: '1002', provincia: 'IMBABURA', canton: 'ANTONIO ANTE' },
    { code: '1003', provincia: 'IMBABURA', canton: 'COTACACHI' },
    { code: '1004', provincia: 'IMBABURA', canton: 'OTAVALO' },
    { code: '1005', provincia: 'IMBABURA', canton: 'PIMAMPIRO' },
    { code: '1006', provincia: 'IMBABURA', canton: 'SAN MIGUEL DE URCUQUI' },

    { code: '1100', provincia: 'LOJA', canton: 'TODOS' },
    { code: '1101', provincia: 'LOJA', canton: 'LOJA' },
    { code: '1102', provincia: 'LOJA', canton: 'CALVAS' },
    { code: '1103', provincia: 'LOJA', canton: 'CATAMAYO' },
    { code: '1104', provincia: 'LOJA', canton: 'CELICA' },
    { code: '1105', provincia: 'LOJA', canton: 'CHAGUARPAMBA' },
    { code: '1106', provincia: 'LOJA', canton: 'ESPINDOLA' },
    { code: '1107', provincia: 'LOJA', canton: 'GONZANAMA' },
    { code: '1108', provincia: 'LOJA', canton: 'MACARA' },
    { code: '1109', provincia: 'LOJA', canton: 'PALTAS' },
    { code: '1110', provincia: 'LOJA', canton: 'PUYANGO' },
    { code: '1111', provincia: 'LOJA', canton: 'SARAGURO' },
    { code: '1112', provincia: 'LOJA', canton: 'SOZORANGA' },
    { code: '1113', provincia: 'LOJA', canton: 'ZAPOTILLO' },
    { code: '1114', provincia: 'LOJA', canton: 'PINDAL' },
    { code: '1115', provincia: 'LOJA', canton: 'QUILANGA' },
    { code: '1116', provincia: 'LOJA', canton: 'OLMEDO' },

    { code: '1200', provincia: 'LOS RIOS', canton: 'TODOS' },
    { code: '1201', provincia: 'LOS RIOS', canton: 'BABAHOYO' },
    { code: '1202', provincia: 'LOS RIOS', canton: 'BABA' },
    { code: '1203', provincia: 'LOS RIOS', canton: 'MONTALVO' },
    { code: '1204', provincia: 'LOS RIOS', canton: 'PUEBLOVIEJO' },
    { code: '1205', provincia: 'LOS RIOS', canton: 'QUEVEDO' },
    { code: '1206', provincia: 'LOS RIOS', canton: 'URDANETA' },
    { code: '1207', provincia: 'LOS RIOS', canton: 'VENTANAS' },
    { code: '1208', provincia: 'LOS RIOS', canton: 'VINCES' },
    { code: '1209', provincia: 'LOS RIOS', canton: 'PALENQUE' },
    { code: '1210', provincia: 'LOS RIOS', canton: 'BUENA FE' },
    { code: '1211', provincia: 'LOS RIOS', canton: 'VALENCIA' },
    { code: '1212', provincia: 'LOS RIOS', canton: 'MOCACHE' },
    { code: '1213', provincia: 'LOS RIOS', canton: 'QUINSALOMA' },

    { code: '1300', provincia: 'MANABI', canton: 'TODOS' },
    { code: '1301', provincia: 'MANABI', canton: 'PORTOVIEJO' },
    { code: '1302', provincia: 'MANABI', canton: 'BOLIVAR' },
    { code: '1303', provincia: 'MANABI', canton: 'CHONE' },
    { code: '1304', provincia: 'MANABI', canton: 'EL CARMEN' },
    { code: '1305', provincia: 'MANABI', canton: 'FLAVIO ALFARO' },
    { code: '1306', provincia: 'MANABI', canton: 'JIPIJAPA' },
    { code: '1307', provincia: 'MANABI', canton: 'JUNIN' },
    { code: '1308', provincia: 'MANABI', canton: 'MANTA' },
    { code: '1309', provincia: 'MANABI', canton: 'MONTECRISTI' },
    { code: '1310', provincia: 'MANABI', canton: 'PAJAN' },
    { code: '1311', provincia: 'MANABI', canton: 'PICHINCHA' },
    { code: '1312', provincia: 'MANABI', canton: 'ROCAFUERTE' },
    { code: '1313', provincia: 'MANABI', canton: 'SANTA ANA' },
    { code: '1314', provincia: 'MANABI', canton: 'SUCRE' },
    { code: '1315', provincia: 'MANABI', canton: 'TOSAGUA' },
    { code: '1316', provincia: 'MANABI', canton: '24 DE MAYO' },
    { code: '1317', provincia: 'MANABI', canton: 'PEDERNALES' },
    { code: '1318', provincia: 'MANABI', canton: 'OLMEDO' },
    { code: '1319', provincia: 'MANABI', canton: 'PUERTO LOPEZ' },
    { code: '1320', provincia: 'MANABI', canton: 'JAMA' },
    { code: '1321', provincia: 'MANABI', canton: 'JARAMIJO' },
    { code: '1322', provincia: 'MANABI', canton: 'SAN VICENTE' },

    { code: '1400', provincia: 'MORONA SANTIAGO', canton: 'TODOS' },
    { code: '1401', provincia: 'MORONA SANTIAGO', canton: 'MORONA' },
    { code: '1402', provincia: 'MORONA SANTIAGO', canton: 'GUALAQUIZA' },
    { code: '1403', provincia: 'MORONA SANTIAGO', canton: 'LIMON INDANZA' },
    { code: '1404', provincia: 'MORONA SANTIAGO', canton: 'PALORA' },
    { code: '1405', provincia: 'MORONA SANTIAGO', canton: 'SANTIAGO' },
    { code: '1406', provincia: 'MORONA SANTIAGO', canton: 'SUCUA' },
    { code: '1407', provincia: 'MORONA SANTIAGO', canton: 'HUAMBOYA' },
    { code: '1408', provincia: 'MORONA SANTIAGO', canton: 'SAN JUAN BOSCO' },
    { code: '1409', provincia: 'MORONA SANTIAGO', canton: 'TAISHA' },
    { code: '1410', provincia: 'MORONA SANTIAGO', canton: 'LOGROÑO' },
    { code: '1411', provincia: 'MORONA SANTIAGO', canton: 'PABLO SEXTO' },
    { code: '1412', provincia: 'MORONA SANTIAGO', canton: 'TIWINTZA' },

    { code: '1500', provincia: 'NAPO', canton: 'TODOS' },
    { code: '1501', provincia: 'NAPO', canton: 'TENA' },
    { code: '1503', provincia: 'NAPO', canton: 'ARCHIDONA' },
    { code: '1504', provincia: 'NAPO', canton: 'EL CHACO' },
    { code: '1507', provincia: 'NAPO', canton: 'QUIJOS' },
    { code: '1509', provincia: 'NAPO', canton: 'CARLOS JULIO AROSEMENA TOLA' },

    { code: '1600', provincia: 'PASTAZA', canton: 'TODOS' },
    { code: '1601', provincia: 'PASTAZA', canton: 'PASTAZA' },
    { code: '1602', provincia: 'PASTAZA', canton: 'MERA' },
    { code: '1603', provincia: 'PASTAZA', canton: 'SANTA CLARA' },
    { code: '1604', provincia: 'PASTAZA', canton: 'ARAJUNO' },

    { code: '1700', provincia: 'PICHINCHA', canton: 'TODOS' },
    { code: '1701', provincia: 'PICHINCHA', canton: 'QUITO' },
    { code: '1702', provincia: 'PICHINCHA', canton: 'CAYAMBE' },
    { code: '1703', provincia: 'PICHINCHA', canton: 'MEJIA' },
    { code: '1704', provincia: 'PICHINCHA', canton: 'PEDRO MONCAYO' },
    { code: '1705', provincia: 'PICHINCHA', canton: 'RUMIÑAHUI' },
    { code: '1707', provincia: 'PICHINCHA', canton: 'SAN MIGUEL DE LOS BANCOS' },
    { code: '1708', provincia: 'PICHINCHA', canton: 'PEDRO VICENTE MALDONADO' },
    { code: '1709', provincia: 'PICHINCHA', canton: 'PUERTO QUITO' },

    { code: '1800', provincia: 'TUNGURAHUA', canton: 'TODOS' },
    { code: '1801', provincia: 'TUNGURAHUA', canton: 'AMBATO' },
    { code: '1802', provincia: 'TUNGURAHUA', canton: 'BAÑOS DE AGUA SANTA' },
    { code: '1803', provincia: 'TUNGURAHUA', canton: 'CEVALLOS' },
    { code: '1804', provincia: 'TUNGURAHUA', canton: 'MOCHA' },
    { code: '1805', provincia: 'TUNGURAHUA', canton: 'PATATE' },
    { code: '1806', provincia: 'TUNGURAHUA', canton: 'QUERO' },
    { code: '1807', provincia: 'TUNGURAHUA', canton: 'SAN PEDRO DE PELILEO' },
    { code: '1808', provincia: 'TUNGURAHUA', canton: 'SANTIAGO DE PILLARO' },
    { code: '1809', provincia: 'TUNGURAHUA', canton: 'TISALEO' },

    { code: '1900', provincia: 'ZAMORA CHINCHIPE', canton: 'TODOS' },
    { code: '1901', provincia: 'ZAMORA CHINCHIPE', canton: 'ZAMORA' },
    { code: '1902', provincia: 'ZAMORA CHINCHIPE', canton: 'CHINCHIPE' },
    { code: '1903', provincia: 'ZAMORA CHINCHIPE', canton: 'NANGARITZA' },
    { code: '1904', provincia: 'ZAMORA CHINCHIPE', canton: 'YACUAMBI' },
    { code: '1905', provincia: 'ZAMORA CHINCHIPE', canton: 'YANTZAZA (YANZATZA)' },
    { code: '1906', provincia: 'ZAMORA CHINCHIPE', canton: 'EL PANGUI' },
    { code: '1907', provincia: 'ZAMORA CHINCHIPE', canton: 'CENTINELA DEL CONDOR' },
    { code: '1908', provincia: 'ZAMORA CHINCHIPE', canton: 'PALANDA' },
    { code: '1909', provincia: 'ZAMORA CHINCHIPE', canton: 'PAQUISHA' },

    { code: '2000', provincia: 'GALAPAGOS', canton: 'TODOS' },
    { code: '2001', provincia: 'GALAPAGOS', canton: 'SAN CRISTOBAL' },
    { code: '2002', provincia: 'GALAPAGOS', canton: 'ISABELA' },
    { code: '2003', provincia: 'GALAPAGOS', canton: 'SANTA CRUZ' },

    { code: '2100', provincia: 'SUCUMBIOS', canton: 'TODOS' },
    { code: '2101', provincia: 'SUCUMBIOS', canton: 'LAGO AGRIO' },
    { code: '2102', provincia: 'SUCUMBIOS', canton: 'GONZALO PIZARRO' },
    { code: '2103', provincia: 'SUCUMBIOS', canton: 'PUTUMAYO' },
    { code: '2104', provincia: 'SUCUMBIOS', canton: 'SHUSHUFINDI' },
    { code: '2105', provincia: 'SUCUMBIOS', canton: 'SUCUMBIOS' },
    { code: '2106', provincia: 'SUCUMBIOS', canton: 'CASCALES' },
    { code: '2107', provincia: 'SUCUMBIOS', canton: 'CUYABENO' },

    { code: '2200', provincia: 'ORELLANA', canton: 'TODOS' },
    { code: '2201', provincia: 'ORELLANA', canton: 'ORELLANA' },
    { code: '2202', provincia: 'ORELLANA', canton: 'AGUARICO' },
    { code: '2203', provincia: 'ORELLANA', canton: 'LA JOYA DE LOS SACHAS' },
    { code: '2204', provincia: 'ORELLANA', canton: 'LORETO' },

    { code: '2301', provincia: 'SANTO DOMINGO', canton: 'SANTO DOMINGO' },

    { code: '2400', provincia: 'SANTA ELENA', canton: 'TODOS' },
    { code: '2401', provincia: 'SANTA ELENA', canton: 'SANTA ELENA' },
    { code: '2402', provincia: 'SANTA ELENA', canton: 'LA LIBERTAD' },
    { code: '2403', provincia: 'SANTA ELENA', canton: 'SALINAS' }
  ];


}
