# Causal drivers of soil N, P, K, OC in Indian farmland and the datasets that map them

Scope: plant-available N, P, K (kg/ha) and OC (%) as reported on Soil Health Cards (SHC). The question is which covariates could explain variation **within a district** after location proxies have been removed (README §5).

**How much was verified.** Facts marked **[V]** were checked against the primary source in this session. Facts marked **[†]** come from the cited primary paper or agency record (DOI or URL given) but were not reopened in this session. Re-check the [†] facts before quoting them in the paper. Anything that could not be pinned down is marked "unverified", with the reason.

---

## 1. Summary

**What the literature says.** At regional scale, SHC N, P, K and OC are controlled by climate (rainfall and temperature control OC and therefore alkaline-KMnO4 N), parent material and clay mineralogy (basalt-derived smectitic Vertisols are K-rich, laterites and red soils are K- and P-poor), and pH/CaCO3 (P fixation). All of these are smooth over tens of km, so a district mean already captures them. This is why every regional covariate behaves like a location proxy in the team's tests.

Within a district, variation comes mostly from **management and micro-landscape**:
- fertilizer and manure history, which falls off with distance from the homestead or village (Tittonell et al. 2005 [V]);
- irrigation and cropping intensity;
- crop type (rice, sugarcane, legumes);
- residue burning;
- position in the toposequence (erosion and deposition, waterlogging);
- alluvial and flood deposition near channels.

On top of that, roughly half of the within-district variance is lab and sampling noise (README §5).

The user's two named drivers, lightning and Rhizobium, are **not useful covariates**:
- **Lightning** adds about 0.1 kg N/ha/yr on a global average. This is derived from roughly 5 Tg N/yr of lightning NOx (Schumann & Huntrieser 2007 [†]) spread over the Earth's surface. That is two to three orders of magnitude below fertilizer rates. All of the world's lightning N combined is roughly a quarter of India's annual fertilizer N use alone (about 20 Mt N in 2022-23, per FAI figures as quoted in secondary sources). Lightning N also reaches the ground only through atmospheric deposition, so it is already contained in N-deposition products.
- **Rhizobium:** no map of rhizobial populations exists for India or anywhere else. Two proxies exist: **legume crop history**, mappable from crop-type time series, and the new agricultural-BNF raster of Reis Ely et al. 2025 (Nature; about 400 m resolution, with layers for legume crops and rice; CC0). The Reis Ely raster is model-derived, so treat it as landscape-scale at best.

**Ranked shortlist for within-district prediction**

| # | Covariate | Why | Data |
|---|---|---|---|
| 1 | **Multi-year crop-phenology metrics** (NDVI/NIRv per kharif/rabi/zaid season, number of seasons cropped, rice/sugarcane/legume flags) | These capture cropping intensity, irrigation, crop removal, legume BNF and residue load, which are the main management drivers. They vary field by field. README idea 9. | Sentinel-2 L2A (10 m, 2017–), Landsat (30 m), Dynamic World, ESA WorldCereal |
| 2 | **Sentinel-1 SAR time series** (VV/VH backscatter, flooding signal during transplanting) | Detects puddled rice (cyanobacterial BNF, denitrification, OC accumulation), waterlogging and soil moisture regime. Works through monsoon cloud. | COPERNICUS/S1_GRD, 10 m, 2014– |
| 3 | **Fine terrain derivatives without absolute elevation** (TWI, TPI at several radii, plan/profile curvature, MRVBF, flow accumulation) | Topography drives erosion, deposition, leaching and waterlogging. These are relative measures, so they are not location proxies. | Copernicus GLO-30, Geomorpho90m, MERIT |
| 4 | **Distance to settlement and building density** | Manure and household waste gradients, and the "homefield" effect [V Tittonell 2005]. Settlement density is also a proxy for input intensity. | Google Open Buildings, GHSL built-up (10–100 m), WorldPop 100 m, VIIRS nightlights (~500 m, weaker) |
| 5 | **Distance to stream or canal, and surface-water occurrence** | Alluvial and flood silt deposition (adds K and P), canal irrigation and seepage salinity | JRC Global Surface Water 30 m, HydroSHEDS/India-WRIS rivers and canals, OSM waterways |
| 6 | **Multi-year fire-pixel counts** | Residue burning removes N, S and part of OC. Strong in Punjab, Haryana and western UP, much weaker in Maharashtra. | VIIRS 375 m / MODIS 1 km active fire (FIRMS) |
| 7 | **Lithology from 1:50k geological maps** (flow units of Deccan basalt, intertrappean beds, alluvium, laterite cappings) | Parent material controls K reserve and texture and changes within districts at plateau edges and valleys | GSI Bhukosh GCM 1:50k |
| 8 | **Bare-soil SWIR mineral indices** (clay, carbonate, iron oxide ratios from S2 B11/B12/B8A/B4) plus the existing composites | These directly sense clay, carbonate (P fixation) and Fe oxides (laterites) at 10–20 m | Sentinel-2 (already downloaded); SoilGrids clay/CEC 250 m as a weaker prior |
| 9 | **Groundwater depth and quality** (EC, K, NO3 of irrigation water) | Irrigation water adds K and salts. Shallow water tables cause waterlogging and sodicity. | CGWB/India-WRIS well data (point data, needs interpolation; landscape scale) |
| 10 | **Neighbourhood land-cover fractions** (cropland, tree, fallow within 250 m / 1 km) | Field context such as forest-edge OC and fallow frequency | Dynamic World / ESA WorldCover 10 m, Bhuvan LULC 50K |

Climate, deposition, lightning, natural BNF, dust-P, livestock grids, the district fertilizer database and the zoning layers are all **regional** (>10 km). Use them for stratification or as priors, not as within-district predictors.

---

## 2. Drivers by nutrient

### 2.0 What SHC actually measures (this determines which drivers matter)

- **"Available N"** in Indian soil labs is normally alkaline-KMnO4 N (Subbiah & Asija 1956). It is an index of easily oxidisable organic N, so it tracks OC closely. It correlates poorly with incubation mineral N and with plant uptake (r = 0.36 and 0.37 for the standard method on acidic soils: Plant Soil Environ. 2013, 59:235, doi:10.17221/675/2012-PSE [V]).
  - Consequence: the **drivers of SHC N are essentially the drivers of OC**. Fertilizer-N timing hardly affects it, because nitrate does not persist. The README's "nutrient chain" idea (OC → N) is well founded.
- **"Available P"** is Olsen (NaHCO3) on neutral and alkaline soils and Bray-1 on acid soils (standard practice; Bray overestimates on calcareous soils [V, method notes]). Where states or labs use different extractants, P is not comparable across the boundary between them.
- **"Available K"** is 1 N NH4OAc-exchangeable K. It does not measure the non-exchangeable reserve, which is large in illitic and smectitic soils.
- **Labs:** 1,068 static and 163 mobile government soil-testing labs; 743 static and 48 mobile labs were active in the last 2 years. 24.16 crore cards issued since 2014-15 (Rajya Sabha answer, 2 Aug 2024 [V]: https://rsdebate.nic.in/bitstream/123456789/749893/1/PQ_265_02082024_U1289_p143_p147.pdf). There is no public per-lab method or QA metadata [V, unverified availability]. A lab effect is therefore a real confounder.
- **Sampling design:** a grid of 2.5 ha in irrigated areas and 10 ha in rainfed areas, 0–15/20 cm depth, sampled after harvest (vikaspedia, the Government of India scheme portal [V]: https://vikaspedia.in/agriculture/policies-and-schemes/crops-related/krishi-unnati-yojana/soil-health-card). One sample therefore represents a composite of a field or grid cell, not a point.

### 2.1 Nitrogen

| Process | Mechanism | Size and importance in India | Source |
|---|---|---|---|
| Mineral fertilizer | Urea dominates. Most applied N is taken up, lost, or transiently mineralised, and little stays as KMnO4-N. | India used about 20.2 Mt N in 2022-23 (FAI figure quoted in secondary sources; the primary table is **unverified**). This is far larger than every natural input combined. | Abrol et al. 2017, *Indian Nitrogen Assessment*, Elsevier, ISBN 978-0-12-811836-8 [V exists] |
| Symbiotic BNF (Rhizobium–legume) | Legume nodules fix N2. Residues and roots raise the N of the following crop. | Global agricultural BNF is 50–70 Tg N/yr. Of this, soybean contributes 16.4, pulses 2.95 and rice 5 Tg [V]. A newer estimate puts agricultural BNF at 56 (54–58) Tg N/yr, and finds that agriculture raised terrestrial BNF by 64% [V]. | Herridge, Peoples & Boddey 2008, Plant Soil 311:1, doi:10.1007/s11104-008-9668-3 [V]; Reis Ely et al. 2025, Nature 643:705, doi:10.1038/s41586-025-09201-w [V] |
| Free-living BNF (cyanobacteria, heterotrophs) in paddy | Floodwater cyanobacteria (blue-green algae, BGA) and rhizosphere diazotrophs fix N2 | Acetylene-reduction estimates range from a few to 80 kg N/ha/crop (mean about 27), but about 20 kg in no-N plots and about 8 kg with broadcast urea, because fertilizer N suppresses fixation. Heterotrophic BNF adds 10–30 kg N/ha/crop [V]. Across cereals, non-symbiotic BNF supplies 22 kg N/ha/yr in rice and 13 in wheat and maize, about 24% of crop N [V]. | Roger & Ladha 1992, Plant Soil 141:41, doi:10.1007/BF00011309 [V]; Ladha et al. 2016 Sci Rep 6:19355, doi:10.1038/srep19355 [V] |
| Lightning | NOx made in the atmosphere, returned in wet and dry deposition | About 5 ± 3 Tg N/yr globally, roughly 3.5 kg N per flash [V]. That is about 0.1 kg N/ha/yr averaged over the globe (derived). Negligible next to fertilizer and BNF, and already counted inside deposition fields. Fowler 2013 reports total N fixation of 413 Tg N/yr, of which 210 is anthropogenic [V]; its per-source table is **unverified**. | Schumann & Huntrieser 2007, ACP 7:3823, doi:10.5194/acp-7-3823-2007 [V]; Fowler et al. 2013, Phil Trans B 368:20130164, doi:10.1098/rstb.2013.0164 [V abstract] |
| Atmospheric deposition (NOx, NH3/NH4+) | Wet and dry deposition. The Indo-Gangetic Plain (IGP) is a global NH3 hotspot (fertilizer plus livestock). | Global inorganic N deposition rose from 86.6 to 93.6 Tg N/yr between 1984 and 2016 [V]. Measured *wet* inorganic N deposition in western UP (Oct 2017–Sep 2018) was 34.8 kg N/ha/yr at a rural site, 31.6 at an urban site and 11.9 at an industrial site [V]. That is not trivial, but it is about 15–25% of typical fertilizer doses and smooth at the ~200 km model grid. | Ackerman, Millet & Chen 2019, GBC 33:100, doi:10.1029/2018GB005990 [V]; Naseem & Kulshrestha 2021, J. Atmos. Chem., doi:10.1007/s10874-021-09425-w [V abstract] |
| Manure, livestock, household waste | Organic N plus OC added near homesteads and cattle sheds | Strong within-farm and within-village gradients (Kenya example: input use 0.7–104 kg N/ha between field types of the same farm) | Tittonell et al. 2005, AEE 110:149, doi:10.1016/j.agee.2005.04.001 [V] |
| Residue burning | N volatilised during burning, surface OC lost | Reported losses for rice residue burning in Punjab are about 35 kg N/ha (secondary review numbers; treat as indicative) | Review, J. Pharmacogn. Phytochem. 2020 (secondary; primary source **unverified**) |
| NH3 volatilisation | Urea hydrolysis at high pH | Measured losses of 28–32 kg N/ha from urea on a pH 9.3 soil at Karnal, and 18–28 kg N/ha in a pH 9.0 sodic soil | J. Agric. Sci. (Cambridge) papers on sodic rice soils [V abstract], https://www.cambridge.org/core/journals/journal-of-agricultural-science/article/abs/effect-of-rates-and-methods-of-urean-application-and-presubmergence-periods-on-ammonia-volatilization-losses-from-rice-fields-in-a-sodic-soil/79DE656C98E338985C630416F0EEA1FE |
| Denitrification | Anaerobic conditions in puddled rice and in waterlogged Vertisols | Mapped through waterlogging and rice extent (SAR) | general |
| Leaching | Nitrate leaching in coarse alluvium and red soils under monsoon rain | Mapped through texture × rainfall × irrigation | general |
| Climate control of the organic N pool | Warm temperatures speed mineralisation; rainfall raises biomass input | Classic India climosequence | Jenny & Raychaudhuri 1960, ICAR (*Effect of climate and cultivation on nitrogen and organic matter reserves in Indian soils*) [V exists] |

### 2.2 Phosphorus

| Process | Mechanism | India | Source |
|---|---|---|---|
| Fertilizer (DAP, SSP) and manure | P is immobile, so it builds up as legacy P in long-fertilized fields | Strongly management-driven. Within-district contrasts of irrigated cash-crop fields against rainfed fields are expected. | MacDonald et al. 2011, PNAS 108:3086, doi:10.1073/pnas.1010808108 (global 0.5° P balance; fertilizer 14.2, manure 9.6, crop removal 12.3 Tg P/yr) [V] |
| Ca-P fixation | Precipitation as Ca phosphates at pH > 7.5 with CaCO3 | Vertisols, calcareous alluvium, sodic soils | standard soil chemistry |
| Fe/Al-P fixation | Sorption onto sesquioxides and kaolinite at pH < 5.5 | Laterites and red soils (Konkan, NE, Kerala) | standard |
| Dust and combustion P deposition | Mineral dust and combustion aerosols | Sources of total atmospheric P are dust 82%, biogenic particles 12% and combustion 5% (Mahowald) [V]. Combustion P emissions are 1.8 Tg P/yr, with deposition of 2.7 Tg P/yr on land (Wang) [V]. Spread over the land surface that is about 0.2 kg P/ha/yr (derived), at least two orders of magnitude below P fertilizer doses. A value specific to India is **unverified**. | Mahowald et al. 2008, GBC 22:GB4026, doi:10.1029/2008GB003240 [V]; Wang et al. 2015, Nat Geosci 8:48, doi:10.1038/ngeo2324 [V]; Brahney et al. 2015 GBC 29:1369 [V] |
| Erosion and deposition | P bound to sediment moves downslope and is deposited in valleys | Terrain and stream proximity | Wiesmeier 2019 (topography) |
| Mycorrhiza (AMF) | Hyphae extend P uptake | No field-scale map exists. The global mycorrhizal vegetation map is coarse and based on natural vegetation. | Soudzilovskaia et al. 2019, Nat Commun 10:5077, doi:10.1038/s41467-019-13019-2 [†] |
| Parent material | Apatite content of the rock. Basalt is P-moderate and granite is P-poor. | Lithology layer | GSI |

P has the weakest natural signal of the four nutrients. It is dominated by fertilizer history plus pH/CaCO3, which agrees with the team's P R² of about 0.

### 2.3 Potassium

| Process | Mechanism | India | Source |
|---|---|---|---|
| Parent material and mineralogy | Feldspar and mica weathering. Smectite holds K on exchange sites; illite releases interlayer K. | In an Indian comparison, cumulative release of non-exchangeable K was 353 mg/kg in smectitic soils, 151 in illitic soils and 194 in kaolinitic soils. Exchangeable K is high in smectitic soils and low in kaolinitic soils. | FAO AGRIS record, "Release kinetics of nonexchangeable potassium… soils of varying mineralogy" [V abstract], https://agris.fao.org/search/es/records/65de3bbf0f3e94b9e5cc3653 |
| High-charge smectite K fixation | Fixes added K, and the fixed K is released slowly | Indian Vertisols | Clays and Clay Minerals, "Role of clay CEC, location of charge and clay mineralogy on K availability in Indian Vertisols" [V abstract via search; DOI **unverified**] |
| Irrigation water K | Groundwater and canal water carry K | Highly variable in space and time; local assessment needed | ICAR (krishi.icar.gov.in record 123456789/26484) [V abstract] |
| Crop removal (K mining) | Sugarcane, banana and rice–wheat remove large amounts of K, and K fertilizer use in India is low | The IGP has negative K balances | ICL review, https://iclfertilizers.com/uploads/Articles/K_nutrition_of%20rice_wheat_cropping_system.pdf [secondary] |
| Alluvial and flood silt | Fresh illitic sediment adds K | Floodplains, canal silt | JRC GSW occurrence |
| Leaching | Little except on sandy and acid soils | Laterites | general |

K is the most parent-material-driven of the four. It is the best case for lithology and mineralogy covariates and the worst case for satellite-only models.

### 2.4 Organic carbon

| Driver | Mechanism | Source |
|---|---|---|
| Climate (temperature, rainfall, aridity) | Rainfall controls biomass input and temperature controls decomposition. This is the main regional control. | Jenny & Raychaudhuri 1960 [V exists]; Wiesmeier et al. 2019, Geoderma 333:149, doi:10.1016/j.geoderma.2018.07.026 [V] |
| Clay content and mineralogy, Ca²⁺, metal oxides | Mineral protection of OC; smectite/Ca bridging in Vertisols, Fe/Al oxides in laterites | Wiesmeier 2019 [V] |
| Land use and management | Inputs from manure, residue retention, irrigation and cropping intensity (more biomass); losses from tillage and burning | Wiesmeier 2019 [V]; Bhattacharyya et al. 2007, Curr. Sci. 93:1854 (IGP and black-soil benchmark sites, SOC rose 1980→2005) [V abstract] |
| Waterlogging and rice | Anaerobic conditions slow decomposition | general |
| Topography | Erosion on slopes, accumulation in depressions | Wiesmeier 2019 [V] |
| Biota | Microbes, earthworms, termites | Delgado-Baquerizo et al. 2018 [†]; Phillips et al. 2019 Science 366:480, doi:10.1126/science.aax4851 [†] (global earthworm map, few Indian sites) |

### 2.5 Cross-cutting soil-property controls

- **pH:** controls P availability and NH3 loss. Already an input.
- **EC:** salinity. Already an input.
- **CaCO3:** controls Ca-P and is sensed by SWIR band 2.33 µm / S2 B12.
- **CEC and texture:** control K and OC retention.
- **Sodicity (ESP):** salt-affected soils of the IGP and canal commands.
- **Waterlogging.**

Of these, pH and EC are the only ones available at field scale apart from satellite sensing. That is why pH/EC alone give N R² of about 0.17.

---

## 3. Dataset catalogue

Scale class: **F** = field (<1 km), **L** = landscape (1–10 km), **R** = regional (>10 km). **R = likely location proxy** for within-district work.

| Driver | Dataset | Resolution | Coverage | Time | Access | Licence | Scale |
|---|---|---|---|---|---|---|---|
| Soil properties (clay, sand, pH, CEC, SOC, N) | SoilGrids v2.0 (ISRIC), Poggio et al. 2021 SOIL 7:217, doi:10.5194/soil-7-217-2021 | 250 m | Global | static (about 240k profiles) [V] | https://soilgrids.org ; GEE community `projects/soilgrids-isric/{clay,sand,silt,cec,phh2o,soc,nitrogen,bdod,cfvo,ocd,ocs}_mean` [V] | CC-BY 4.0 [V] | L (nominal 250 m, but driven by sparse Indian profiles, so effectively R). The IIT Delhi pipeline found NoData gaps [V]. |
| Soil maps | NBSS&LUP soil resource maps 1:1M (India), 1:250k (states) | polygons | India | 1980s–2000s | https://icar-nbsslup.org.in [V]; NBSS Bhoomi geoportal [V exists] | restricted / on request (**unverified**) | R |
| Soil (large scale) | NBSS&LUP Land Resource Inventory (LRI) 1:10k, e.g. 14 Maharashtra watersheds under PMKSY 2.0 (Pub. 253, 2026) | 1:10k | selected watersheds and blocks | 2021– | PDF reports, e.g. https://mhvslna.org/admin/LRI/9.pdf [V]; GIS on request | **unverified** | F (where available) |
| Agro-ecology | NBSS&LUP AER (20) / AESR (60) | polygons | India | 1992 / 1999 | see §4 | — | R |
| Lithology | GSI Bhukosh: 1:2M geology, 1:50k mapping | 1:50k | India | static | https://bhukosh.gsi.gov.in (registration, download cart, delivered by email [V secondary]; formats **unverified**) | GoI (NDSAP-type terms, **unverified**) | L |
| Fertilizer, crop area, irrigation, land use by district | ICRISAT-TCI District Level Database (DLD): 74 datasets, 1,030 variables; district N/P/K consumption, crop-wise area and production, irrigation [V, https://tci.cornell.edu/data] | district | 571 districts, 20 states, apportioned to 1966 boundaries [V] | 1966–2017 [V] | https://vdsa.icrisat.org/vdsa-mesodoc.aspx ; http://data.icrisat.org/dld/ (free registration) | **unverified** | R |
| Fertilizer sales | FAI *Fertiliser Statistics*; DoF/DAC state and district tables | district/state | India | annual | https://www.faidelhi.org (paid) ; https://data.gov.in | mixed | R |
| Livestock | 20th Livestock Census 2019 (DAHD): ~6.6 lakh villages, 303.76 M bovines [V] | district / village tables (some states' village tables on data.gov.in) | India | 2018–19 | https://dahd.gov.in/schemes/programmes/animal-husbandry-statistics [V] | GoI | R (village tables could be L if georeferenced) |
| Livestock | GLW3, Gilbert et al. 2018 Sci Data 5:180227, doi:10.1038/sdata.2018.227 [V] (8 species); GLW4 (FAO 2024, aligned to FAOSTAT 2020) [V partly] | 0.0833° (~10 km) | Global | 2010 (GLW3); 2020 (GLW4) | https://www.fao.org/livestock-systems/global-distributions/en | GLW3 CC-BY 4.0 [†]; GLW4 **unverified** | R |
| N deposition | Ackerman et al. 2019 (GEOS-Chem) [V] | 2° × 2.5° | Global | 1984–86, 1994–96, 2004–06, 2014–16 [V] | UMN Data Repository doi:10.13020/D6KX2R, https://conservancy.umn.edu/handle/11299/197613 [V] | CC BY-ND 3.0 US [V] | R |
| N deposition | ISIMIP3a N deposition (Yang & Tian; NCAR CCMI regridded), doi:10.48364/ISIMIP.759077.4 [V] | 0.5°, monthly | Global | 1850–2021 (2015–2021 repeat 2014) [V] | https://www.isimip.org | CC0 / CC BY-SA 4.0 [V] | R |
| N deposition (assessment) | Vet et al. 2014 Atmos. Environ. 93:3, doi:10.1016/j.atmosenv.2013.10.060 (WMO-GAW + TF-HTAP ensemble) [V] | model ensemble | Global | 2001; 2000–07 obs | https://wdcpc.org/global-assessment-data ; zenodo 10.5281/zenodo.3981435 | — | R |
| Natural BNF | Davies-Barnard & Friedlingstein 2020 GBC 34, doi:10.1029/2019GB006387 [V] (median 88 Tg N/yr) | site/biome CSV, **not a raster** [V] | Global, **natural ecosystems only** | static | doi:10.24378/exe.2063 [V] | CC BY 4.0 [V] | R; not applicable to cropland |
| **Agricultural + natural BNF** | Reis Ely et al. 2025 Nature 643:705, doi:10.1038/s41586-025-09201-w [V]; one layer per niche, **incl. legume crops, forage legumes, rice** | 0.004° (~400 m) and 1° [V] | Global | ~present-day | USGS ScienceBase doi:10.5066/P13THKNR (no GEE) [V] | CC0 [V] | L (modelled from crop maps; check what drives the 400 m pattern before use) |
| Agricultural BNF proxy | Legume crop area: ICRISAT DLD (district); WorldCereal has no pulse layer, so build your own from S2 time series | district / 10 m | India | annual | — | — | R / F |
| Lightning | LIS/OTD gridded climatology v2.3.2015 (NASA GHRC), doi:10.5067/LIS/LIS-OTD/DATA311 (HRFC: DATA302); Cecil et al. 2014 Atmos. Res., doi:10.1016/j.atmosres.2012.06.028 [V] | 0.5° HRFC, 2.5° LRMTS [V] | Global | 4 May 1995 – 31 Dec 2014 [V] | https://ghrc.nsstc.nasa.gov (no GEE) | US public domain [V] | R (and agronomically negligible) |
| Dust / P deposition | Mahowald et al. 2008 model fields; Wang et al. 2015 | ~2° (**unverified**) | Global | climatology | on request (**unverified**) | — | R |
| Rainfall | CHIRPS v2.0, Funk et al. 2015 Sci Data 2:150066, doi:10.1038/sdata.2015.66 [V] | 0.05° (~5.5 km) | 50°S–50°N | 1981–present | GEE `UCSB-CHG/CHIRPS/DAILY` [V] | public domain [V] | L–R |
| Rainfall / temperature | IMD gridded rainfall, Pai et al. 2014 Mausam 65:1 [V]; IMD Tmax/Tmin, Srivastava et al. 2009 ASL 10:249, doi:10.1002/asl.232 [V] | rain 0.25°; temp 1.0° | India | rain 1901–2024; temp 1951–2024 [V] (temp after 2008 rests on ~180 stations) | https://www.imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html ; `imdlib` Python; not in GEE | **unverified** | R |
| Temperature, soil moisture, ET | ERA5-Land, Muñoz-Sabater et al. 2021 ESSD 13:4349, doi:10.5194/essd-13-4349-2021 [V] | 0.1° (~9 km) | Global | 1950–present | GEE `ECMWF/ERA5_LAND/HOURLY`, `ECMWF/ERA5_LAND/DAILY_AGGR` [V] | Copernicus C3S licence, attribution required [V] | R |
| ET, NDVI | MODIS MOD16A2GF ET (500 m, 2000–2025; plain `MOD16A2` in GEE only from 2021) and MOD13Q1 NDVI (250 m, 16-day, 2000–) [V] | 250–500 m | Global | 2000– | GEE `MODIS/061/MOD16A2GF`, `MODIS/061/MOD13Q1` | NASA open | L |
| Surface temperature | MODIS LST MOD11A2 / MOD11A1 v061 [V] | 1 km, 8-day / daily | Global | 2000– | GEE `MODIS/061/MOD11A2`, `MODIS/061/MOD11A1` [V] | NASA open [V] | L |
| Aridity | Global Aridity Index & PET v3, Zomer et al. 2022 Sci Data 9:409, doi:10.1038/s41597-022-01493-1 | 30″ (~1 km) | Global | 1970–2000 climatology [V] | figshare doi:10.6084/m9.figshare.7504448; community GEE https://gee-community-catalog.org/projects/ai0/ | CC-BY 4.0 (**unverified**) | R (smooth surface) |
| Irrigated area | GMIA v5 (Siebert et al. 2013, Univ. Bonn/FAO) [V] | 5′ (~10 km) | Global | ~2005 [V] | https://www.fao.org/aquastat/en/geospatial-information/global-maps-irrigated-areas/latest-version | **unverified** | R |
| Irrigated area (India) | Ambika, Wardlow & Mishra 2016 Sci Data 3:160118, doi:10.1038/sdata.2016.118 [V] (R² 0.95 vs statistics) | 250 m | India | 2000–2015 annual [V] | paper data link | CC-BY [†] | L |
| Irrigated vs rainfed | LGRIP30 v001 (USGS), Teluguntla et al. 2023, doi:10.5067/Community/LGRIP/LGRIP30.001 [V] | 30 m | Global | nominal 2015 (Landsat 2014–17) [V] | NASA LP DAAC | public | F |
| Crop type | ESA WorldCereal 2021, Van Tricht et al. 2023 ESSD 15:5491, doi:10.5194/essd-15-5491-2023 | 10 m | Global | 2021 (one season set) | https://esa-worldcereal.org ; GEE `ESA/WorldCereal/2021/MODELS/v100` [V]; zenodo doi:10.5281/zenodo.7875104 | CC-BY 4.0 [†] | F (temporary crops, maize, winter/spring cereals, irrigation, active cropland [V]; no rice or pulses layer) |
| Rice | National India 10 m rice maps 2018/2020/2022, 23 states, Sentinel-1/2 SPRI index, OA 84.4% — Remote Sens. 16(17):3180 (2024) [V abstract; authors **unverified**]; Singha et al. 2019 Sci Data, 10 m S1 paddy maps for NE India [V] | 10 m | India | 2018–2022 | https://www.mdpi.com/2072-4292/16/17/3180 | CC-BY (MDPI) | F |
| Cropland (India) | NRSC/NICES annual kharif/rabi/net-sown/fallow cropland from AWiFS [V] | 56 m | India | 2005-06 to 2015-16 | https://nices.nrsc.gov.in/docs/crop_land.pdf | GoI | F–L |
| Land cover | Dynamic World, Brown et al. 2022 Sci Data 9:251, doi:10.1038/s41597-022-01307-4 | 10 m, per scene | Global | 2015-06– [V] | GEE `GOOGLE/DYNAMICWORLD/V1` [V] | CC-BY 4.0 [V] | F |
| Land cover | ESA WorldCover v200 [V] | 10 m | Global | 2021 | GEE `ESA/WorldCover/v200` [V] | CC-BY 4.0 [V] | F |
| Land use (India) | NRSC Bhuvan LULC 50K | 1:50k | India | 2005-06, 2011-12, 2015-16 (**unverified** cycles) | https://bhuvan.nrsc.gov.in (WMS view; download restricted) [†] | GoI | F–L |
| Cropping intensity | Jain et al. 2013 RSE 134:210, doi:10.1016/j.rse.2013.02.029 — a methods comparison, **not** a national product [V]; build own from S2/Landsat NDVI seasons | 30 m | build | — | — | — | F |
| Fire / residue burning | GEE `FIRMS` = MODIS-only 1 km raster, 2000-11– [V]; MOD14A1 1 km daily [V]; MCD64A1 burned area 500 m monthly [V]; VIIRS 375 m points via FIRMS archive download (GEE VIIRS collections are NRT; archive depth **unverified**) | 375 m–1 km | Global | 2000/2012– | GEE `FIRMS`, `MODIS/061/MOD14A1`, `MODIS/061/MCD64A1`; https://firms.modaps.eosdis.nasa.gov | NASA open [V] | F–L |
| Groundwater level and quality | CGWB monitoring wells: about 23–25k wells, read 4× per year since 1969 (via an India Data Portal mirror) [V secondary]. Quality: 15,259 locations, including **K⁺, NO₃, EC, PO₄** (CGWB *Groundwater Quality of Shallow Aquifers 2024*, 2023 data) [V] | points | India | 1969– | https://indiawris.gov.in ; https://cgwb.gov.in/cgwbpnm/public/uploads/documents/17363272771910393216file.pdf | GoI (**unverified**) | L after interpolation |
| Water-table depth | Fan, Li & Miguez-Macho 2013 Science 339:940, doi:10.1126/science.1229881 [V] | 0.01° (~1 km) [V] | Global | equilibrium model | http://thredds-gfnl.usc.es/thredds/catalog/GLOWASIS/catalog.html | **unverified** | R (modelled, smooth) |
| Basins, rivers | HydroSHEDS / HydroBASINS / HydroATLAS, Linke et al. 2019 Sci Data 6:283, doi:10.1038/s41597-019-0300-6 | 15″ (~500 m) rivers; basin polygons | Global | static | GEE `WWF/HydroSHEDS/v1/Basins/hybas_12`, `WWF/HydroATLAS/v1/Basins/level12` [†] | free (HydroSHEDS licence) | L (distance-to-river: F) |
| Basins, canals (India) | India-WRIS basins, sub-basins, canal command areas | polygons | India | static | https://indiawris.gov.in [†] | GoI | L |
| Flood / ponding | JRC Global Surface Water v1.4, Pekel et al. 2016 Nature 540:418, doi:10.1038/nature20584 | 30 m | Global | 1984–2021 | GEE `JRC/GSW1_4/GlobalSurfaceWater` | free | F |
| SAR moisture / paddy | Sentinel-1 GRD | 10 m, 6–12 day | Global | 2014– | GEE `COPERNICUS/S1_GRD` | Copernicus free | F |
| Terrain | Copernicus GLO-30 (GEE `COPERNICUS/DEM/GLO30`, now `GLO30_2024_1`) [V]; MERIT DEM 90 m (`MERIT/DEM/v1_0_3`, CC BY-NC 4.0 or ODbL) [V]; Geomorpho90m (26 variables, 90/250 m, community GEE only), Amatulli et al. 2020 Sci Data 7:162, doi:10.1038/s41597-020-0479-6 [V] | 30–90 m | Global | static | GEE / OpenTopography | free (MERIT non-commercial) | F |
| Salinity / sodicity | Hassani, Azapagic & Shokri 2020 PNAS 117(52):33017 [V journal/pages], doi:10.1073/pnas.2013771117 (DOI string **unverified**); ECe and ESP | ~1 km [V] | Global | 1980–2018 [V] | https://pmc.ncbi.nlm.nih.gov/articles/PMC7776813 | — | R–L |
| Salinity (India) | NRSA 1997 state-wise salt-affected soils maps 1:250k (1986/87 Landsat); national total 6.73 Mha (Mandal et al. 2009) [V] | 1:250k | India | 1986–2009 | https://cssri.res.in ; on request (**unverified**) | — | L–R |
| Soil moisture | SMAP L4 (`NASA/SMAP/SPL4SMGP/008`) [V] | 9 km | Global | 2015– | GEE | NASA open | R |
| Population / settlement | WorldPop 100 m; GHSL built-up (JRC/GHSL/P2023A) 10–100 m; Google Open Buildings v3 (polygons) | 10–100 m | Global | 2000–2020/2030 | GEE `WorldPop/GP/100m/pop`, `JRC/GHSL/P2023A/GHS_BUILT_S`, `GOOGLE/Research/open-buildings/v3/polygons` | CC-BY | F |
| Night lights | VIIRS DNB annual V2.2 (EOG), Elvidge et al. 2021 Remote Sens. 13:922, doi:10.3390/rs13050922 [V] | ~464 m | Global | 2012–2024 [V] | GEE `NOAA/VIIRS/DNB/ANNUAL_V22` [V] | public domain [V] | L |
| Soil microbes | Delgado-Baquerizo et al. 2018 Science 359:320, doi:10.1126/science.aap9516 | 237 sites, 18 countries [V] (number of Indian sites **unverified**) | Global (very few Indian sites) | ~2010s | paper SI | — | R; not usable as a covariate |
| Soil microbes | Earth Microbiome Project, Thompson et al. 2017 Nature 551:457, doi:10.1038/nature24621 | 27,751 samples, 97 studies [V] | Global (sparse in India) | — | https://earthmicrobiome.org | open | points only; not usable |
| Microbial biomass | Xu, Thornton & Post 2013 GEB 22:737, doi:10.1111/geb.12029 — a **point compilation** (3,422 points, 315 papers) plus biome extrapolation; gridded resolution **unverified** [V] | points / biome | Global | static | ORNL DAAC doi:10.3334/ORNLDAAC/1264 [V] | open | R |
| Mycorrhiza | Soudzilovskaia et al. 2019 [V] | 10 arc-min (~18 km) [partly V] | Global | static | paper | — | R |
| Earthworms | Phillips et al. 2019 (6,928 sites, 57 countries) [V] | gridded prediction (resolution **unverified**) | Global | static | iDiv data portal [†] | — | R (sparse India) |
| Termites | **No India or global gridded termite map was found** | — | — | — | — | — | — |
| Rhizobium | **No population map exists** for India [V, search of ICAR, ICRISAT and global atlases]. Only point surveys exist, e.g. ICRISAT chickpea rhizobia: farmers' fields mostly <10 to 10³ cells/g, research stations 10³–10⁵/g (Soil Biol. Biochem. 19:247, 1987; https://oar.icrisat.org/8137) [V]. | points | — | 1987 | — | — | Use legume history or the Reis Ely 2025 legume-BNF layer |

---

## 4. Zoning frameworks and boundary files

Several portals (Bhukosh, NBSS Bhoomi, ICRISAT DLD) refused connections from the research sandbox, so "unverified" below often means "the portal could not be opened", not "the data do not exist".

| Framework | Units | Basis | Digitised boundary availability |
|---|---|---|---|
| **NBSS&LUP Agro-Ecological Regions (AER)**, Sehgal et al. 1990/1992 | 20 | Physiography, soils, bioclimate, length of growing period (LGP) | **Scanned raster only** (1:5M) in EU JRC ESDAC/EuDASM [V]: https://esdac.jrc.ec.europa.eu/public_path/shared_folder/eudasm/asia/lists/cin.htm. NBSS **Bhoomi geoportal** (http://nbsslup.in/bhoomi, linked from https://krishi.icar.gov.in/Geo_Portal.jsp) serves AER, AESR and the 1:1M soil map as **WMS for viewing**. Downloads may be restricted for security/IPR reasons [V, ACRS 2020 paper https://acrs-aars.org/proceeding/ACRS2020/1b7w2a.P.docx]. A free shapefile is **unverified and probably not offered**; request it from NBSS&LUP. A community vector exists: the IIT Delhi CoRE Stack pipeline used "NBSS&LUP AEZ vector boundaries", zones 2–19 [V thesis] (https://github.com/Singhratinder/Soil-Health-Mapping-PanIndia, no licence). |
| **NBSS&LUP Agro-Ecological Sub-Regions (AESR)** | 60 | AER subdivided by LGP, soil, physiography | ESDAC scanned map "Agro-Ecological Subregions", Sehgal, Mandal & Mandal 1996, 1:4.4M [V]. The book is usually cited as Velayutham et al. 1999 (**unverified**). FAO GAEZ lists "Agro-ecological subregions of India" sourced from NBSS&LUP: https://gaez.fao.org/datasets/agro-ecological-subregions-of-india (format and licence **unverified**; the most promising public vector source). Bhoomi WMS for viewing. |
| **NARP Agro-climatic Zones** (ICAR, 1979–) | 126 or 127 (secondary sources disagree) | Rainfall, soils, cropping; defined as lists of districts or tehsils | **No official public shapefile found** [V, search]. Rebuild by dissolving district or tehsil polygons from the zone lists. An Esri India hub layer "Agro Climatic Zones of India" exists (https://maps-cadoc.opendata.arcgis.com/maps/esriindia1::agro-climatic-zones-of-india/about), but which classification it uses is **unverified**. |
| **Planning Commission Agro-climatic Regions**, Khanna 1989 | 15 regions, 72 sub-zones | Physiography and climate, district-based | Documented in the NITI Aayog digital library: https://digitallibrary.niti.gov.in/handle/123456789/3964 [V]. OGD resource "Boundaries of Agro-climatic regions": https://karnataka.data.gov.in/resource/boundaries-agro-climatic-regions (format **unverified**; GODL-India licence). The India-WRIS Region module also carries it (**unverified**). Too coarse for the team's purpose. |
| Bhuvan (NRSC) thematic | — | LULC 1:50k (2005-06, 2011-12, 2015-16; 54 classes), wasteland, geomorphology/lineament, erosion, and salt-affected/waterlogging 1:50k (2005-06) [V, https://bhuvan-app1.nrsc.gov.in/2dresources/documents/2_Bhuvan_Geospatial_Content.pdf] | Mostly WMS view-only. Some products are downloadable via NOEDA. **Geomorphology and erosion 1:50k are useful within-district layers** if they can be obtained. |

**Recommendation for the team's "zones from causals" idea.** Building zones from causal covariates means unsupervised clustering of regional drivers into data-driven zones. Clustering inputs: aridity or LGP (Zomer AI, CHIRPS seasonality), lithology class (GSI 1:2M), dominant clay mineralogy proxy (SoilGrids clay plus a Vertisol mask from the NBSS soil map), and irrigation fraction (Ambika 250 m).

- Validate the zones against AESR-60 (agreement check) and use them **only for stratification and for spatial-CV folds**.
- Leave-one-zone-out CV is the honest test of transferability.
- Note: stratifying by zone does **not** add within-district skill. It can only reduce bias from pooling heterogeneous regions.
- The IIT Delhi pan-India pipeline reports mean test R² of N 0.67, P 0.46, K 0.45, OC 0.35 across 18 AEZs [V]. However, it used a **random 80/20 `train_test_split(test_size=0.2, random_state=42)`** [V, thesis appendix]. This is exactly the setup the team showed to be inflated (README §5 finding 5), so do not treat those numbers as a benchmark.

---

## 5. Gaps and caveats

1. **Location-proxy risk.** Every covariate in class R, and most in L (climate, deposition, DLD fertilizer, GLW, aridity, AESR membership, SoilGrids in data-sparse India), is spatially smooth. Under 50 km block CV it can only re-learn the regional mean, which district averages already give. Test each new covariate with the existing within-district R² metric (target minus district mean) and keep it only if within-district skill rises.
2. **Measurement validity.** Alkaline-KMnO4 N is an OC proxy (§2.0). Olsen and Bray P differ between labs and states. NH4OAc-K ignores the non-exchangeable reserve. When moving beyond Maharashtra, **lab ID / state** must be handled as a random effect, or harmonised. Otherwise state boundaries turn into fake "zones".
3. **Lab and sampling noise.** README §5 estimates that about half of the within-district variance is noise (best achievable within-district R² ≈ 0.39–0.52). Placeholder GPS points corrupt every field-scale covariate. Keep de-clustering.
4. **2023–24 snapshot.** Management covariates should describe the years *before* sampling (for example 2019–2023 crop history and fire counts). Static or later layers risk temporal mismatch. Fire and flood are event-driven.
5. **Composite sample support.** One SHC value is a V-cut composite over a 2.5–10 ha grid cell. Aggregate field-scale covariates to a matching window (roughly 100–300 m), not a single 10 m pixel.
6. **Rhizobium and microbial data.** None at a usable scale. Global microbe atlases rest on a handful of Indian sites.
7. **Lightning and deposition.** Physically small next to fertilizer, and at ~200 km resolution. Drop them as covariates.
8. **Access friction.** NBSS&LUP AER/AESR GIS, CSSRI salinity maps and Bhuvan downloads may require formal requests. GSI Bhukosh needs a login. ICRISAT DLD needs registration.
9. **Unverified items** (marked above): the primary FAI table for national fertilizer N, the per-source split in Fowler 2013, licences of GMIA, Bhukosh and NBSS, and whether the AESR (FAO GAEZ) and Esri NARP layers can be downloaded directly. Climate, land-cover, fire, terrain, irrigation, livestock and microbe datasets were verified on GEE catalog or producer pages.
10. **Dataset-specific traps:** Gilbert 2018 is GLW3 (2010), not GLW4. GEE `FIRMS` is MODIS-only at 1 km. `MOD16A2` in GEE starts only in 2021 (use `MOD16A2GF`). IMD temperature after 2008 rests on a sparse station network. The Zomer aridity index is a 1970–2000 climatology.

---

## 6. References (primary)

- Ackerman D., Millet D.B., Chen X. (2019) GBC 33:100–107. doi:10.1029/2018GB005990
- Abrol Y.P. et al. (eds) (2017) *The Indian Nitrogen Assessment*. Elsevier. ISBN 978-0-12-811836-8. https://shop.elsevier.com/books/the-indian-nitrogen-assessment/abrol/978-0-12-811836-8
- Amatulli G. et al. (2020) Geomorpho90m. Sci Data 7:162. doi:10.1038/s41597-020-0479-6
- Ambika A.K. et al. (2016) Sci Data 3:160118. doi:10.1038/sdata.2016.118
- Bhattacharyya T. et al. (2007) Curr. Sci. 93(12):1854–1863. https://oar.icrisat.org/2243
- Biswas H. et al. (2026) LRI for 14 watersheds of Maharashtra, NBSS&LUP Publ. 253. https://mhvslna.org/admin/LRI/9.pdf
- Brown C.F. et al. (2022) Dynamic World. Sci Data 9:251. doi:10.1038/s41597-022-01307-4
- Cecil D.J., Buechler D.E., Blakeslee R.J. (2014) Atmos. Res. 135–136:404–414. doi:10.1016/j.atmosres.2012.06.028
- Davies-Barnard T., Friedlingstein P. (2020) GBC 34. doi:10.1029/2019GB006387
- Reis Ely C. et al. (2025) Nature 643:705–711. doi:10.1038/s41586-025-09201-w ; data doi:10.5066/P13THKNR
- Naseem M., Kulshrestha U.C. (2021) J. Atmos. Chem. doi:10.1007/s10874-021-09425-w
- Vet R. et al. (2014) Atmos. Environ. 93:3–100. doi:10.1016/j.atmosenv.2013.10.060
- Brahney J. et al. (2015) GBC 29:1369.
- Delgado-Baquerizo M. et al. (2018) Science 359:320–325. doi:10.1126/science.aap9516
- Fan Y., Li H., Miguez-Macho G. (2013) Science 339:940–943. doi:10.1126/science.1229881
- Fowler D. et al. (2013) Phil Trans R Soc B 368:20130164. doi:10.1098/rstb.2013.0164
- Funk C. et al. (2015) CHIRPS. Sci Data 2:150066. doi:10.1038/sdata.2015.66
- Gilbert M. et al. (2018) GLW3. Sci Data 5:180227. doi:10.1038/sdata.2018.227
- Srivastava A.K., Rajeevan M., Kshirsagar S.R. (2009) Atmos. Sci. Lett. 10:249–254. doi:10.1002/asl.232
- Elvidge C.D. et al. (2021) Remote Sens. 13:922. doi:10.3390/rs13050922
- Hassani A., Azapagic A., Shokri N. (2020) PNAS 117(52):33017–33027. https://pmc.ncbi.nlm.nih.gov/articles/PMC7776813
- Teluguntla P. et al. (2023) LGRIP30 v001. doi:10.5067/Community/LGRIP/LGRIP30.001
- Herridge D.F., Peoples M.B., Boddey R.M. (2008) Plant Soil 311:1–18. doi:10.1007/s11104-008-9668-3
- Jain M. et al. (2013) RSE 134:210–223. doi:10.1016/j.rse.2013.02.029
- Jenny H., Raychaudhuri S.P. (1960) *Effect of climate and cultivation on nitrogen and organic matter reserves in Indian soils*. ICAR. https://catalog.hathitrust.org/Record/009080798
- Ladha J.K. et al. (2016) Sci Rep 6:19355. doi:10.1038/srep19355
- Linke S. et al. (2019) HydroATLAS. Sci Data 6:283. doi:10.1038/s41597-019-0300-6
- MacDonald G.K. et al. (2011) PNAS 108:3086–3091. doi:10.1073/pnas.1010808108
- Mahowald N. et al. (2008) GBC 22:GB4026. doi:10.1029/2008GB003240
- Muñoz-Sabater J. et al. (2021) ERA5-Land. ESSD 13:4349. doi:10.5194/essd-13-4349-2021
- Pai D.S. et al. (2014) Mausam 65(1):1–18.
- Pekel J.-F. et al. (2016) Nature 540:418–422. doi:10.1038/nature20584
- Phillips H.R.P. et al. (2019) Science 366:480–485. doi:10.1126/science.aax4851
- Poggio L. et al. (2021) SoilGrids 2.0. SOIL 7:217–240. doi:10.5194/soil-7-217-2021
- Roger P.A., Ladha J.K. (1992) Plant Soil 141:41–55. doi:10.1007/BF00011309
- Schumann U., Huntrieser H. (2007) ACP 7:3823–3907. doi:10.5194/acp-7-3823-2007
- Singh R.P. (2026) *Scalable Geospatial ML for Soil Health and Biomass Mapping*, MTech thesis, IIT Delhi. https://core-stack.org/wp-content/uploads/2026/07/ratinder-mtp2-thesis.pdf
- Soudzilovskaia N.A. et al. (2019) Nat Commun 10:5077. doi:10.1038/s41467-019-13019-2
- Thompson L.R. et al. (2017) Nature 551:457–463. doi:10.1038/nature24621
- Tittonell P. et al. (2005) AEE 110:149–165. doi:10.1016/j.agee.2005.04.001
- Van Tricht K. et al. (2023) WorldCereal. ESSD 15:5491. doi:10.5194/essd-15-5491-2023
- Wang R. et al. (2015) Nat Geosci 8:48–54. doi:10.1038/ngeo2324
- Wiesmeier M. et al. (2019) Geoderma 333:149–162. doi:10.1016/j.geoderma.2018.07.026
- Xu X., Thornton P.E., Post W.M. (2013) GEB 22:737–749. doi:10.1111/geb.12029
- Zomer R.J., Xu J., Trabucco A. (2022) Sci Data 9:409. doi:10.1038/s41597-022-01493-1
- Plant Soil Environ. (2013) 59:235–240, N availability indices on acidic Indian soils. doi:10.17221/675/2012-PSE
- Soil Health Card scheme guidelines (sampling grid). https://vikaspedia.in/agriculture/policies-and-schemes/crops-related/krishi-unnati-yojana/soil-health-card
