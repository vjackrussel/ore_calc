from io import StringIO
import pandas as pd

textbox = StringIO("""
Azure Plagioclase	24,018	8,406 m3	59 km
Azure Plagioclase	51,391	17,986 m3	57 km
Azure Plagioclase	61,059	21,370 m3	70 km
Azure Plagioclase	64,638	22,623 m3	53 km
Azure Plagioclase	66,070	23,124 m3	54 km
Azure Plagioclase	70,301	24,605 m3	64 km
Azure Plagioclase	85,131	29,795 m3	67 km
Azure Plagioclase	92,112	32,239 m3	46 km
Azure Plagioclase	94,471	33,064 m3	78 km
Bistot	2,197	35,152 m3	40 km
Bistot	4,177	66,832 m3	57 km
Bistot	4,273	68,368 m3	85 km
Bistot	5,011	80,176 m3	72 km
Condensed Scordite	4,716	707 m3	61 km
Condensed Scordite	5,823	873 m3	56 km
Condensed Scordite	5,909	886 m3	42 km
Condensed Scordite	6,389	958 m3	51 km
Condensed Scordite	6,737	1,010 m3	61 km
Condensed Scordite	6,871	1,030 m3	74 km
Condensed Scordite	7,140	1,071 m3	49 km
Condensed Scordite	7,331	1,099 m3	58 km
Condensed Scordite	8,182	1,227 m3	83 km
Condensed Scordite	8,549	1,282 m3	74 km
Condensed Scordite	8,870	1,330 m3	50 km
Condensed Scordite	9,860	1,479 m3	54 km
Crokite	208	3,328 m3	48 km
Crokite	488	7,808 m3	46 km
Crokite	569	9,104 m3	64 km
Crokite	649	10,384 m3	63 km
Crystalline Crokite	480	7,680 m3	62 km
Crystalline Crokite	518	8,288 m3	57 km
Crystalline Crokite	564	9,024 m3	51 km
Crystalline Crokite	578	9,248 m3	57 km
Crystalline Crokite	651	10,416 m3	59 km
Fiery Kernite	10,293	12,351 m3	55 km
Fiery Kernite	12,463	14,955 m3	59 km
Fiery Kernite	7,695	9,234 m3	63 km
Gneiss	2,163	10,815 m3	52 km
Gneiss	3,111	15,555 m3	54 km
Gneiss	3,374	16,870 m3	55 km
Golden Omber	13,356	8,013 m3	55 km
Iridescent Gneiss	1,125	5,625 m3	52 km
Iridescent Gneiss	1,803	9,015 m3	34 km
Iridescent Gneiss	2,632	13,160 m3	49 km
Iridescent Gneiss	2,805	14,025 m3	49 km
Iridescent Gneiss	2,907	14,535 m3	49 km
Iridescent Gneiss	2,916	14,580 m3	87 km
Iridescent Gneiss	3,537	17,685 m3	72 km
Iridescent Gneiss	762	3,810 m3	63 km
Kernite	10,148	12,177 m3	78 km
Kernite	8,396	10,075 m3	65 km
Luminous Kernite	12,864	15,436 m3	48 km
Luminous Kernite	5,437	6,524 m3	63 km
Luminous Kernite	7,282	8,738 m3	60 km
Luminous Kernite	7,362	8,834 m3	50 km
Luminous Kernite	7,388	8,865 m3	54 km
Luminous Kernite	7,785	9,342 m3	88 km
Luminous Kernite	9,192	11,030 m3	71 km
Luminous Kernite	9,329	11,194 m3	58 km
Luminous Kernite	9,426	11,311 m3	56 km
Luminous Kernite	9,526	11,431 m3	58 km
Luminous Kernite	9,575	11,490 m3	80 km
Luminous Kernite	9,947	11,936 m3	62 km
Massive Scordite	6,305	945 m3	54 km
Massive Scordite	7,281	1,092 m3	44 km
Monoclinic Bistot	4,053	64,848 m3	47 km
Omber	12,259	7,355 m3	65 km
Omber	12,915	7,749 m3	78 km
Omber	14,771	8,862 m3	57 km
Omber	3,813	2,287 m3	41 km
Prismatic Gneiss	2,220	11,100 m3	81 km
Prismatic Gneiss	2,924	14,620 m3	63 km
Pyroxeres	42,745	12,823 m3	62 km
Pyroxeres	46,358	13,907 m3	60 km
Pyroxeres	58,931	17,679 m3	72 km
Pyroxeres	69,132	20,739 m3	41 km
Pyroxeres	78,637	23,591 m3	72 km
Rich Plagioclase	64,689	22,641 m3	61 km
Rich Plagioclase	68,618	24,016 m3	49 km
Rich Plagioclase	76,239	26,683 m3	46 km
Rich Plagioclase	77,884	27,259 m3	56 km
Scordite	7,042	1,056 m3	52 km
Scordite	9,707	1,456 m3	60 km
Sharp Crokite	180	2,880 m3	37 km
Sharp Crokite	366	5,856 m3	46 km
Sharp Crokite	388	6,208 m3	74 km
Sharp Crokite	409	6,544 m3	54 km
Sharp Crokite	468	7,488 m3	55 km
Sharp Crokite	496	7,936 m3	51 km
Sharp Crokite	585	9,360 m3	57 km
Sharp Crokite	646	10,336 m3	73 km
Sharp Crokite	661	10,576 m3	35 km
Sharp Crokite	753	12,048 m3	89 km
Sharp Crokite	769	12,304 m3	61 km
Silvery Omber	10,461	6,276 m3	64 km
Silvery Omber	11,996	7,197 m3	52 km
Silvery Omber	12,068	7,240 m3	66 km
Silvery Omber	13,968	8,380 m3	48 km
Silvery Omber	16,056	9,633 m3	59 km
Silvery Omber	3,708	2,224 m3	52 km
Silvery Omber	5,279	3,167 m3	45 km
Solid Pyroxeres	43,905	13,171 m3	56 km
Solid Pyroxeres	44,240	13,272 m3	68 km
Solid Pyroxeres	44,500	13,350 m3	52 km
Solid Pyroxeres	46,730	14,019 m3	58 km
Solid Pyroxeres	48,271	14,481 m3	63 km
Solid Pyroxeres	54,605	16,381 m3	54 km
Solid Pyroxeres	55,123	16,536 m3	56 km
Solid Pyroxeres	58,084	17,425 m3	52 km
Solid Pyroxeres	59,401	17,820 m3	39 km
Solid Pyroxeres	66,020	19,806 m3	61 km
Solid Pyroxeres	67,409	20,222 m3	63 km
Solid Pyroxeres	68,159	20,447 m3	53 km
Solid Pyroxeres	72,704	21,811 m3	64 km
Triclinic Bistot	2,587	41,392 m3	41 km
Triclinic Bistot	3,870	61,920 m3	57 km
Triclinic Bistot	4,514	72,224 m3	89 km
Triclinic Bistot	4,539	72,624 m3	64 km
Triclinic Bistot	4,650	74,400 m3	44 km
Triclinic Bistot	4,776	76,416 m3	50 km
Triclinic Bistot	4,858	77,728 m3	74 km
Triclinic Bistot	5,756	92,096 m3	56 km
Viscous Pyroxeres	35,930	10,779 m3	44 km
Viscous Pyroxeres	53,592	16,077 m3	61 km
Viscous Pyroxeres	59,221	17,766 m3	63 km
Viscous Pyroxeres	77,090	23,127 m3	35 km
""")

test = pd.read_csv(textbox, sep='\t', lineterminator='\n', names=["Ore", "Units", "Volume", "Distance"])
test = test.drop(columns=['Volume','Distance'])
test["Units"] = test["Units"].map(lambda x: x.replace(',',''))
test[["Units"]] = test[["Units"]].apply(pd.to_numeric)
test = test.groupby("Ore").agg({"Units":"sum"})
test["Units"] = test["Units"].map(lambda x: x/100)
print(test)
