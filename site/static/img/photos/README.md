# Photographs

One photograph sits behind each segment on the site: the eight regions on the home page
rack, the six data categories, the six downloads, the three source relationships on the
reconciliation page, and the countries of every live region.

These are the published copies. They are small WebP files written by
`scripts/make_photos.py` from the full-size originals in `assets/photos/`, which are
kept out of `site/static` so they are never served. Replace an original, run the script,
and the build picks the new copy up on its next run.

## How the build finds them

A file is looked up by the slug of the segment it belongs to:

    region-southeast-asia.webp        the rack on the home page
    domain-financing.webp             the data categories
    country-tha.webp                  the country cards, by ISO3
    rel-derived.webp                  the reconciliation cards
    panel-csv.webp                    the downloads

Every backdrop is optional by design. A segment with no file of its own is drawn on
plain metal, so photographs can be added or replaced one at a time without touching the
templates. The lookup is `photo()` in `scripts/build_site.py`.

## How they are prepared

The originals are bright: a white building against a clear sky, a market under lights.
Light text cannot be read over that however the stylesheet is arranged, so the
highlights are rolled off when the copy is written instead of covered up afterwards.
Everything above a threshold is compressed towards a ceiling, which takes the glare out
while leaving the detail and the shadows alone, and it puts every photograph in the same
tonal range so one setting in the stylesheet suits all of them. The thresholds are
`KNEE`, `CEIL` and `FLOOR` at the top of `scripts/make_photos.py`.

On the page each picture is part-desaturated, drawn at low opacity and carries its own
gradient wash, so it gives shape and tone, not detail. That is why the copies are
small: at the size and opacity they are drawn, a larger file buys nothing.

The rack used to draw a Natural Earth map over the photograph as well. The two competed
and the maps came out. `scripts/make_region_art.py` still generates them offline if a
region page ever wants one, where there is room for a map to be looked at and not just
read through.

## Before filing a photograph

Check what the picture actually shows, not what the download was called. One of these
was captioned for the wrong continent, which on a public academic page is a credibility
problem and not a cosmetic one.

A Pexels photo page usually records where the picture was taken, under the Share
button, and the description often names the town. Read both before filing. Of the 46
African downloads checked on 3 October 2026, 12 were recorded in a different country
from the one the download was saved for (three Yaoundé views saved for the Central
African Republic, Gabon and Guinea, for example). A 13th, recorded in Rwanda, shows
Burundian bank signs written in Kirundi. The Zambia download records no place and the
first Pexels tag on the Zambia download is Kruger National Park, in South Africa. Of
those 14 downloads only one is filed, as `country-mli`, because Pexels records the
download saved for Guinea-Bissau in Mali and the download saved for Mali in Nigeria.

## Source and licence

None of these files carry EXIF author or copyright fields, so the record has to be kept
by hand. Fill this in before the site is published.

The ten Commons and Unsplash rows were filed on 3 October 2026. Every place was checked
against the file's Commons categories, the GPS (Global Positioning System) position or the
place the photographer recorded on Unsplash.

The 78 Commons rows filed on 29 October 2026 cover the countries of South Asia, East Asia
and the Pacific, Latin America and the Caribbean, the Middle East and North Africa and
Eastern Europe and Central Asia, with Comoros, Equatorial Guinea and São Tomé and Príncipe.
Only files released under CC0 (Creative Commons Zero, a waiver of every right) or into the
public domain were taken, because the site carries no credit line. The licence was read from
the licence templates on the Commons file page as well as from the summary the Commons API
(application programming interface) returns, because the API reported public domain for a
Sudan candidate whose page carries `{{self|cc-by-sa-4.0}}`. The Sudan candidate was refused
and moved out of the downloads. Unsplash copies uploaded to Commons carry no licence template
and were refused too. A file under the Flickr Public Domain Mark was taken only where the
Flickr account which published the photograph applied the mark and a Commons review,
by a licence reviewer or by the FlickreviewR bot, recorded the mark as passed. A CC0 tag was
refused where the file page names a third-party website as the source and records no
permission, which ruled out a photograph of the Turkmenbaşy Bank in Aşgabat, and where a
`{{self}}` tag names an author other than the uploader with no transfer record, which ruled
out a street in Türkmenabat. Every place was checked against the Commons categories, the
title or the GPS position of the file, and every match was confirmed by eye, because a name
search also returns namesakes in other countries. The search for Malabo returned a file from
the Philippines, Kolonia a file from Warsaw, Moroni a file from Utah, Alexandria a file from
Virginia, Fort Zeelandia a file from Taiwan and Jamaica a file from Queens in New York, and
no file from a namesake was used. The originals are the 1920 px renditions Commons serves,
or the full upload where the upload is narrower (1440 px for Equatorial Guinea, 1600 px for
the Marshall Islands and 1618 px for Syria).

All 130 countries on the eight live region pages now have a photograph, and no country card
is drawn on plain metal.

| file | subject | source | licence | attribution required |
|---|---|---|---|---|
| `region-southeast-asia` | | | | |
| `region-south-asia` | | | | |
| `region-east-asia-and-the-pacific` | | | | |
| `region-eastern-and-southern-africa` | | | | |
| `region-western-and-central-africa` | | | | |
| `region-latin-america-and-the-caribbean` | | | | |
| `region-middle-east-and-north-africa` | | | | |
| `region-eastern-europe-and-central-asia` | | | | |
| `domain-financing` | | | | |
| `domain-cascade` | | | | |
| `domain-epi` | | | | |
| `domain-prevention` | | | | |
| `domain-service_access` | | | | |
| `domain-denominator` | | | | |
| `country-tha` | | | | |
| `country-vnm` | | | | |
| `country-idn` | | | | |
| `country-phl` | | | | |
| `country-mmr` | | | | |
| `country-khm` | | | | |
| `country-lao` | | | | |
| `country-mys` | | | | |
| `country-tls` | | | | |
| `country-bfa` | girl pushing a bicycle loaded with water cans, Ouagadougou | [Pexels 14887285](https://www.pexels.com/photo/14887285/), enkahramanmurat | Pexels licence | no |
| `country-cpv` | rocky beach below a palm-lined resort, no place recorded, first tag Cape Verde | [Pexels 14652598](https://www.pexels.com/photo/14652598/), ganajp | Pexels licence | no |
| `country-cmr` | woman in ceremonial dress at a traditional ceremony, Batoufam, West Region | [Pexels 12241227](https://www.pexels.com/photo/12241227/), messina | Pexels licence | no |
| `country-tcd` | coach stopped beside a roadside restaurant and a thatched hut | [Pexels 17527663](https://www.pexels.com/photo/17527663/), faruktokluoglu | Pexels licence | no |
| `country-cod` | villagers carrying water in basins and cans, near Kalemie | [Pexels 13428229](https://www.pexels.com/photo/13428229/), alain-nkingi | Pexels licence | no |
| `country-gmb` | river ferry carrying passengers and sacks of goods | [Pexels 12687030](https://www.pexels.com/photo/12687030/), timon-cornelissen | Pexels licence | no |
| `country-gha` | women and girls in kente cloth holding Ghanaian flags | [Pexels 31058593](https://www.pexels.com/photo/31058593/), zeal-creative-studios | Pexels licence | no |
| `country-lbr` | two fruit sellers carrying trays on their heads, Monrovia | [Pexels 29377386](https://www.pexels.com/photo/29377386/), b-aristotle-guweh-jr | Pexels licence | no |
| `country-mli` | shopfronts on a muddy street, recorded in Mali (downloaded as Guinea-Bissau) | [Pexels 17527657](https://www.pexels.com/photo/17527657/), faruktokluoglu | Pexels licence | no |
| `country-mrt` | man leading a camel through scrub desert, near Nouakchott | [Pexels 18030919](https://www.pexels.com/photo/18030919/), ben-khatry | Pexels licence | no |
| `country-nga` | National Youth Service Corps members raising flags, Kaduna | [Pexels 32562421](https://www.pexels.com/photo/32562421/), abdulrahman-abubakar | Pexels licence | no |
| `country-sen` | thatched huts in a village, Kolda | [Pexels 12522152](https://www.pexels.com/photo/12522152/), pros-pierre | Pexels licence | no |
| `country-sle` | four children in a Freetown neighbourhood | [Pexels 28988502](https://www.pexels.com/photo/28988502/), samuel-konika | Pexels licence | no |
| `country-tgo` | two women walking along a street wall, Lomé | [Pexels 37904065](https://www.pexels.com/photo/37904065/), evariste-houwadan | Pexels licence | no |
| `country-ben` | aerial view over the rooftops of Porto-Novo, place recorded as Porto-Novo, Bénin | [Unsplash kWPNxQyAT6M](https://unsplash.com/photos/aerial-view-of-city-buildings-under-cloudy-sky-during-daytime-kWPNxQyAT6M), Yanick Folly, 2400 px rendition | Unsplash licence | no |
| `country-caf` | the yellow colonial town hall, Bangui | [Commons, Hôtel de ville de Bangui.jpg](https://commons.wikimedia.org/wiki/File:H%C3%B4tel_de_ville_de_Bangui.jpg), unknown author | CC0 | no |
| `country-cog` | Basilique Sainte-Anne with a car in front, Brazzaville, GPS in Brazzaville | [Commons, Les endroits publics de Brazzaville, République du Congo 01.jpg](https://commons.wikimedia.org/wiki/File:Les_endroits_publics_de_Brazzaville%2C_R%C3%A9publique_du_Congo_01.jpg), Africany | CC0 | no |
| `country-civ` | the Plateau district of Abidjan, the lagoon and a bridge, seen from the Grand Hotel | [Commons, WikiConvFr23 à Abidjan … depuis Grand Hotel.jpg](https://commons.wikimedia.org/wiki/File:WikiConvFr23_%C3%A0_Abidjan_en_Cote_d%27Ivoire_vue_panoramique_de_la_ville_du_Plateau_depuis_Grand_Hotel.jpg), Adoscam | CC0 | no |
| `country-gab` | the LIBREVILLE letters sign among palm trees, one man standing at the edge | [Commons, Libreville, la ville libre.jpg](https://commons.wikimedia.org/wiki/File:Libreville%2C_la_ville_libre.jpg), ArnoBOUJIKA | CC0 | no |
| `country-gin` | the Bembéto overpass in Conakry with motorcyclists and pedestrians, 2025 | [Commons, Pont de Bembéto3 (cropped).jpg](https://commons.wikimedia.org/wiki/File:Pont_de_Bemb%C3%A9to3_%28cropped%29.jpg), Aboubacarkhoraa | CC0 | no |
| `country-gnb` | aerial view over rooftops, GPS in Bissau | [Commons, Vue du ciel de Bissau.jpg](https://commons.wikimedia.org/wiki/File:Vue_du_ciel_de_Bissau.jpg), Aboubacarkhoraa | CC0 | no |
| `country-ner` | the Niger River with Niamey behind, filed under Niamey | [Commons, Au bord du fleuve Niger7.jpg](https://commons.wikimedia.org/wiki/File:Au_bord_du_fleuve_Niger7.jpg), Ibrahimassoumane | CC0 | no |
| `country-ago` | three children looking up at the camera, Lumeje, Moxico | [Pexels 18333952](https://www.pexels.com/photo/18333952/), elisa-giaccaglia | Pexels licence | no |
| `country-bwa` | elephant on a river floodplain with zebra behind | [Pexels 39470507](https://www.pexels.com/photo/39470507/), rinoadamo | Pexels licence | no |
| `country-bdi` | drummers performing around a drum painted with the Burundian flag | [Pexels 18807623](https://www.pexels.com/photo/18807623/), audy-of-course | Pexels licence | no |
| `country-eri` | man beside a camel carrying logs, in front of a painted shopfront | [Pexels 13026996](https://www.pexels.com/photo/13026996/), awet-amine | Pexels licence | no |
| `country-swz` | man on a tractor beside a thatched building, Mbabane | [Pexels 32852494](https://www.pexels.com/photo/32852494/), proudlyswazi | Pexels licence | no |
| `country-eth` | men in white robes holding staffs at a ceremony | [Pexels 25849069](https://www.pexels.com/photo/25849069/), christian-alemu | Pexels licence | no |
| `country-ken` | Maasai man in a red checked cloth | [Pexels 12125842](https://www.pexels.com/photo/12125842/), sachin-saini | Pexels licence | no |
| `country-lso` | two thatched huts below a hill | [Pexels 20427051](https://www.pexels.com/photo/20427051/), elina-emeleeva | Pexels licence | no |
| `country-mdg` | red earth house in dry grassland, two children in the middle distance | [Pexels 7506103](https://www.pexels.com/photo/7506103/), megane-ssu | Pexels licence | no |
| `country-mwi` | group of seven children, Blantyre | [Pexels 14327955](https://www.pexels.com/photo/14327955/), 20secrets | Pexels licence | no |
| `country-mus` | Flic en Flac beach at sunset with Le Morne Brabant behind | [Pexels 34190261](https://www.pexels.com/photo/34190261/), damini-gokool | Pexels licence | no |
| `country-moz` | aerial view of Maputo towards the bay | [Pexels 30188142](https://www.pexels.com/photo/30188142/), sinalmultimedia | Pexels licence | no |
| `country-nam` | red dunes at Sossusvlei | [Pexels 35220465](https://www.pexels.com/photo/35220465/), hub-jacqu | Pexels licence | no |
| `country-som` | camel caravan crossing stony desert | [Pexels 37973322](https://www.pexels.com/photo/37973322/), mohamed-abdirisak-ali | Pexels licence | no |
| `country-zaf` | Cape Town at night below Table Mountain | [Pexels 33622083](https://www.pexels.com/photo/33622083/), kelly | Pexels licence | no |
| `country-ssd` | woman holding donated clothing at a distribution | [Pexels 34222337](https://www.pexels.com/photo/34222337/), speakmediauganda | Pexels licence | no |
| `country-tza` | wildebeest in the Serengeti | [Pexels 9185413](https://www.pexels.com/photo/9185413/), akos-helgert | Pexels licence | no |
| `country-uga` | two children on a bicycle carrying firewood, seen from behind, Bunjako | [Pexels 34162830](https://www.pexels.com/photo/34162830/), frostee-lens-ug | Pexels licence | no |
| `country-zwe` | motorcyclist on a dirt road | [Pexels 12661318](https://www.pexels.com/photo/12661318/), jhuneblue | Pexels licence | no |
| `country-rwa` | the Nyamirambo neighbourhood of Kigali across the hills, place recorded as Nyamirambo | [Unsplash K15V22xU1zs](https://unsplash.com/photos/a-view-of-a-city-with-a-lot-of-houses-K15V22xU1zs), Protais Benjamin Mugenzi, 2400 px rendition | Unsplash licence | no |
| `country-zmb` | a street lined with jacaranda trees, place recorded as Kitwe | [Unsplash KL_awSVEuFY](https://unsplash.com/photos/a-street-with-cars-parked-on-the-side-of-it-KL_awSVEuFY), Omoniyi David, 2400 px rendition | Unsplash licence | no |
| `country-afg` | the old city of Herat seen from the Citadel, filed under Views of Herat | [Commons, Herat in June 2011.jpg](https://commons.wikimedia.org/wiki/File:Herat_in_June_2011.jpg), S.K. Vemmer, US Department of State | public domain | no |
| `country-bgd` | tea bushes under shade trees, Malnicherra Tea Estate, GPS in Sylhet | [Commons, View of Malnicherra Tea Estate, Sylhet, Bangladesh 17.jpg](https://commons.wikimedia.org/wiki/File:View_of_Malnicherra_Tea_Estate%2C_Sylhet%2C_Bangladesh_17.jpg), Kryesmin | CC0 | no |
| `country-btn` | a dzong above a covered bridge, filed under Bhutan | [Commons, Bhutan 23 (635).jpg](https://commons.wikimedia.org/wiki/File:Bhutan_23_%28635%29.jpg), Mussi Katz | CC0 | no |
| `country-ind` | the ghats of Varanasi from the Ganges, filed under Ghats in Varanasi | [Commons, Banaras Ghats.jpg](https://commons.wikimedia.org/wiki/File:Banaras_Ghats.jpg), Storycraftmarketing | CC0 | no |
| `country-mdv` | a beach lined with trees, filed under Malé | [Commons, Maldives 2017.jpg](https://commons.wikimedia.org/wiki/File:Maldives_2017.jpg), Mickey Luigi Logitmark | CC0 | no |
| `country-npl` | a mustard field at dusk with snow peaks behind, Pokhara | [Commons, Chill evening from Mustard field Pokhara.jpg](https://commons.wikimedia.org/wiki/File:Chill_evening_from_Mustard_field_Pokhara.jpg), Chillionaire rohit | CC0 | no |
| `country-pak` | Lahore Junction railway station, GPS in Lahore | [Commons, Lahore Junction station 2024.jpg](https://commons.wikimedia.org/wiki/File:Lahore_Junction_station_2024.jpg), ほっきー | CC0 | no |
| `country-lka` | Diyathilaka Mandapa island on Kandy Lake | [Commons, Diyathilaka Mandapa Island.jpg](https://commons.wikimedia.org/wiki/File:Diyathilaka_Mandapa_Island.jpg), Bergentroll | CC0 | no |
| `country-chn` | the Pudong skyline across the Huangpu River, GPS in Shanghai | [Commons, Shanghai skyline waterfront pudong 5166168 69 70.jpg](https://commons.wikimedia.org/wiki/File:Shanghai_skyline_waterfront_pudong_5166168_69_70.jpg), Ermell | CC0 | no |
| `country-fji` | central Suva over Prouds Triangle and the post office | [Commons, Suva City 1 February 2015.jpg](https://commons.wikimedia.org/wiki/File:Suva_City_1_February_2015.jpg), Stemoc | CC0 | no |
| `country-kir` | the shore of Flint Island in the Line Islands, seen from a boat | [Commons, Flint Island AKK Profile.jpg](https://commons.wikimedia.org/wiki/File:Flint_Island_AKK_Profile.jpg), Angela K. Kepler | public domain | no |
| `country-mhl` | aerial view of an atoll town inside the reef, filed under the Marshall Islands | [Commons, U S Coast Guard deploys band … fety (9120349).jpg](https://commons.wikimedia.org/wiki/File:U_S_Coast_Guard_deploys_band_to_Republic_of_Marshall_Islands%2C_raises_awareness_of_boating_safety_%289120349%29.jpg), Lt. Anna Maria Vaccaro, US Coast Guard | public domain | no |
| `country-fsm` | the airstrip of Pingelap Island, Pohnpei State, from the air | [Commons, Pingelap airdrop.jpg](https://commons.wikimedia.org/wiki/File:Pingelap_airdrop.jpg), Senior Airman Carlin Leslie, US Air Force | public domain | no |
| `country-mng` | a street in Tsetserleg, Arkhangai Province, GPS in Tsetserleg | [Commons, Tsetserleg, Mongolia.jpg](https://commons.wikimedia.org/wiki/File:Tsetserleg%2C_Mongolia.jpg), Bernard Gagnon | CC0 | no |
| `country-prk` | the vaulted hall of Yŏnggwang station, Pyongyang Metro | [Commons, Pyongyang Metro September 2015 08.jpg](https://commons.wikimedia.org/wiki/File:Pyongyang_Metro_September_2015_08.jpg), Topolinochamp | CC0 | no |
| `country-png` | the ship Doulos Hope at the Port Moresby waterfront, GPS in Port Moresby | [Commons, Doulos Hope in Port Moresby, Papua New Guinea.jpg](https://commons.wikimedia.org/wiki/File:Doulos_Hope_in_Port_Moresby%2C_Papua_New_Guinea.jpg), Wai0004 | CC0 | no |
| `country-wsm` | the coast of O Le Pupu-Pu'e National Park from the air, filed under Upolu | [Commons, Aerial view of the O Le Pupu … BIOPAMA Photos.jpg](https://commons.wikimedia.org/wiki/File:Aerial_view_of_the_O_Le_Pupu_Pue_National_Park%2C_Samoa%2C_IUCN_BIOPAMA_Photos.jpg), BIOPAMA | public domain | no |
| `country-slb` | palms over the beach at Lavungu port on Rennell Island, filed under Beaches of the Solomon Islands | [Commons, Lavunguferryday.jpg](https://commons.wikimedia.org/wiki/File:Lavunguferryday.jpg), Phenss | public domain | no |
| `country-ton` | vegetable stalls in Talamahu Market, Nukuʻalofa | [Commons, Talamahu Market.jpg](https://commons.wikimedia.org/wiki/File:Talamahu_Market.jpg), Pilgrim81 | public domain | no |
| `country-tuv` | Funafuti International Airport on the atoll, from the air | [Commons, Funafuti International Airport.jpg](https://commons.wikimedia.org/wiki/File:Funafuti_International_Airport.jpg), Oetti42 | CC0 | no |
| `country-vut` | Port Vila harbour from the air, filed under Water in Vanuatu | [Commons, Port Vila, Vanuatu.jpg](https://commons.wikimedia.org/wiki/File:Port_Vila%2C_Vanuatu.jpg), Wyncliffe | CC0 | no |
| `country-com` | Lake Dzialandze in the hills of Anjouan | [Commons, Lac dzialandze.JPG](https://commons.wikimedia.org/wiki/File:Lac_dzialandze.JPG), Peioma | public domain | no |
| `country-gnq` | formal gardens with a domed building behind, Ciudad de la Paz, 2026 | [Commons, Ciudad de la Paz, Guinea Ecuatorial 2026.jpg](https://commons.wikimedia.org/wiki/File:Ciudad_de_la_Paz%2C_Guinea_Ecuatorial_2026.jpg), Juan Pedro Ndong Ondo | CC0 | no |
| `country-stp` | Pico Papagaio on Príncipe from the air, GPS on Príncipe | [Commons, Pico Papagaio from above.jpg](https://commons.wikimedia.org/wiki/File:Pico_Papagaio_from_above.jpg), Cgaffga | CC0 | no |
| `country-arg` | the Cabildo seen from Plaza de Mayo, Buenos Aires | [Commons, Cabildo Plaza de Mayo Buenos Aires 5 de Agosto 2023.jpg](https://commons.wikimedia.org/wiki/File:Cabildo_Plaza_de_Mayo_Buenos_Aires_5_de_Agosto_2023.jpg), Crazychubut | CC0 | no |
| `country-blz` | South Water Caye seen from the sea, GPS off the Belize coast | [Commons, South Water Caye, Belize, December 2021.jpg](https://commons.wikimedia.org/wiki/File:South_Water_Caye%2C_Belize%2C_December_2021.jpg), Jim McIntosh | CC0 | no |
| `country-bol` | office towers on Avenida Arce, La Paz | [Commons, Centro de La Paz sobre la Avenida Arce.jpg](https://commons.wikimedia.org/wiki/File:Centro_de_La_Paz_sobre_la_Avenida_Arce.jpg), EEJCC | CC0 | no |
| `country-bra` | Rio de Janeiro and the hills seen from Pão de Açúcar | [Commons, Rio de Janeiro city from Pão de Açúcar, Brazil.jpg](https://commons.wikimedia.org/wiki/File:Rio_de_Janeiro_city_from_P%C3%A3o_de_A%C3%A7%C3%BAcar%2C_Brazil.jpg), Wilfredor | CC0 | no |
| `country-col` | hillside houses of Comuna 13, San Javier, Medellín, Colombia | [Commons, Comuna 13 San Javier, Medellín, abril de 2017.jpg](https://commons.wikimedia.org/wiki/File:Comuna_13_San_Javier%2C_Medell%C3%ADn%2C_abril_de_2017.jpg), Sebastian Reategui | CC0 | no |
| `country-cri` | Parque Morazán in San José, with the Temple of Music | [Commons, San Jose Costa Rica Parque 2011.jpg](https://commons.wikimedia.org/wiki/File:San_Jose_Costa_Rica_Parque_2011.jpg), Dennis Sylvester Hurd | CC0 | no |
| `country-cub` | the historic centre of Trinidad from a museum rooftop, GPS in Trinidad | [Commons, Trinidad panorama from museo de bandidos.jpg](https://commons.wikimedia.org/wiki/File:Trinidad_panorama_from_museo_de_bandidos.jpg), Jan Pešula | CC0 | no |
| `country-dom` | high-rise blocks of Santo Domingo from above, filed under Views of Santo Domingo, Dominican Republic | [Commons, SantoDomingoedit.JPG](https://commons.wikimedia.org/wiki/File:SantoDomingoedit.JPG), Jose Juan C | public domain | no |
| `country-ecu` | central Quito with El Panecillo behind, filed under Panoramic views of Quito | [Commons, Quitopanoramica.jpg](https://commons.wikimedia.org/wiki/File:Quitopanoramica.jpg), Patricio Mena Vásconez | public domain | no |
| `country-slv` | a coast road running down to the sea at sunset, Surf City, published by the presidency of El Salvador | [Commons, Surf City II.jpg](https://commons.wikimedia.org/wiki/File:Surf_City_II.jpg), Casa Presidencial El Salvador | CC0 | no |
| `country-gtm` | the National Palace reflected in a wet square, Guatemala City | [Commons, Guatemala National Palace (reflection).jpg](https://commons.wikimedia.org/wiki/File:Guatemala_National_Palace_%28reflection%29.jpg), Gobierno de Guatemala | public domain | no |
| `country-guy` | the Kanuku Mountains near Lethem, filed under Lethem, Guyana | [Commons, Lethem Guyana Kunuku Mountains.jpg](https://commons.wikimedia.org/wiki/File:Lethem_Guyana_Kunuku_Mountains.jpg), Kevin Gabbert | public domain | no |
| `country-hti` | a market street in Jacmel with hills behind, filed under Jacmel | [Commons, Jacmel dans nos rêve.jpg](https://commons.wikimedia.org/wiki/File:Jacmel_dans_nos_r%C3%AAve.jpg), Jeanfrandy | CC0 | no |
| `country-hnd` | cumulus clouds over Tegucigalpa, GPS in Tegucigalpa | [Commons, Cumulus clouds over Tegucigalpa, Honduras.jpg](https://commons.wikimedia.org/wiki/File:Cumulus_clouds_over_Tegucigalpa%2C_Honduras.jpg), Straggles | CC0 | no |
| `country-jam` | the long beach at Negril, filed under Beaches of Negril | [Commons, Strand von Negril.JPG](https://commons.wikimedia.org/wiki/File:Strand_von_Negril.JPG), Alphakaya | public domain | no |
| `country-mex` | forested mountains near Hierve el Agua, GPS in Oaxaca | [Commons, Hierve el Agua nature.jpg](https://commons.wikimedia.org/wiki/File:Hierve_el_Agua_nature.jpg), Paumucito | CC0 | no |
| `country-nic` | boats at a jetty in Brig Bay, Big Corn Island | [Commons, Big Corn Island aka Great Corn island, Nicaragua 01.jpg](https://commons.wikimedia.org/wiki/File:Big_Corn_Island_aka_Great_Corn_island%2C_Nicaragua_01.jpg), Ridiculopathy | CC0 | no |
| `country-pan` | the Iglesia Nuestra Señora del Carmen on Vía España, Panama City | [Commons, Iglesia Nuestra Señora del Carmen (Vía España).jpg](https://commons.wikimedia.org/wiki/File:Iglesia_Nuestra_Se%C3%B1ora_del_Carmen_%28V%C3%ADa_Espa%C3%B1a%29.jpg), Virpana | CC0 | no |
| `country-pry` | towers of Asunción at sunset, GPS in Asunción | [Commons, Atardeceres desde mi ventana - Flickr - abel.maestro.jpg](https://commons.wikimedia.org/wiki/File:Atardeceres_desde_mi_ventana_-_Flickr_-_abel.maestro.jpg), Abel Maestro Garcia | public domain | no |
| `country-per` | the roofs of Cusco and the Plaza de Armas from above | [Commons, Cusco skyline - October 2025.jpg](https://commons.wikimedia.org/wiki/File:Cusco_skyline_-_October_2025.jpg), WMrapids | CC0 | no |
| `country-sur` | a colonial house at Zeelandiaweg 5, Paramaribo | [Commons, Monumentaal gebouw te Fort Zeelandia.jpg](https://commons.wikimedia.org/wiki/File:Monumentaal_gebouw_te_Fort_Zeelandia.jpg), Brakaise | CC0 | no |
| `country-tto` | Port of Spain and the harbour from the air | [Commons, POS SKYLINE 2024 BEAUTIFUL EVAN-P 2024 10-8.jpg](https://commons.wikimedia.org/wiki/File:POS_SKYLINE_2024_BEAUTIFUL_EVAN-P_2024_10-8.jpg), Itrydisrespxtsmtsep | CC0 | no |
| `country-ven` | El Ávila above the El Bosque district, Caracas | [Commons, Parque Nacional El Ávila desde El Bosque 01.jpg](https://commons.wikimedia.org/wiki/File:Parque_Nacional_El_%C3%81vila_desde_El_Bosque_01.jpg), Periodismodepaz | CC0 | no |
| `country-dza` | white apartment blocks of Algiers below the El Aurassi hotel, GPS in Algiers | [Commons, Alger - l'auressi الجزائر - الاوراسي.jpg](https://commons.wikimedia.org/wiki/File:Alger_-_l%27auressi_%D8%A7%D9%84%D8%AC%D8%B2%D8%A7%D8%A6%D8%B1_-_%D8%A7%D9%84%D8%A7%D9%88%D8%B1%D8%A7%D8%B3%D9%8A.jpg), habib kaki | public domain | no |
| `country-dji` | limestone chimneys on a lake shore, filed under Djibouti | [Commons, Trip to Djibouti3.jpg](https://commons.wikimedia.org/wiki/File:Trip_to_Djibouti3.jpg), Michael Fowler | public domain | no |
| `country-egy` | the colonnade and statues of Luxor Temple | [Commons, Luxor Temple, Luxor, Egypt (53723849499).jpg](https://commons.wikimedia.org/wiki/File:Luxor_Temple%2C_Luxor%2C_Egypt_%2853723849499%29.jpg), Mustang Joe | CC0 | no |
| `country-irn` | the rooftops and wind towers of Yazd, GPS in Yazd | [Commons, Historical context of Yazd.jpg](https://commons.wikimedia.org/wiki/File:Historical_context_of_Yazd.jpg), Baharak roshanbakhsh | CC0 | no |
| `country-irq` | a mosque in central Erbil, filed under Mosques in Arbil | [Commons, View of a mosque in the city … Region DSF5059.jpg](https://commons.wikimedia.org/wiki/File:View_of_a_mosque_in_the_city_center_of_Erbil%2C_the_Kurdistan_Region_DSF5059.jpg), Levi Meir Clancy | CC0 | no |
| `country-jor` | Ad Deir, the Monastery, at Petra, GPS at Petra | [Commons, Petra Jordan BW 36.JPG](https://commons.wikimedia.org/wiki/File:Petra_Jordan_BW_36.JPG), Berthold Werner | public domain | no |
| `country-lbn` | the old harbour of Byblos with a ruined tower | [Commons, Byblos 03.jpg](https://commons.wikimedia.org/wiki/File:Byblos_03.jpg), Patrice Bon | CC0 | no |
| `country-lby` | the Benghazi waterfront across the lagoon, with the Al Daawa al Islamiyah building | [Commons, Al Daawa alIslamiyah2.JPG](https://commons.wikimedia.org/wiki/File:Al_Daawa_alIslamiyah2.JPG), Maher A. A. Abdussalam | public domain | no |
| `country-mar` | the Jamaa El Fna square, Marrakesh | [Commons, Marrakesh 25.03.2011 15-23-09.2011 15-23-09.JPG](https://commons.wikimedia.org/wiki/File:Marrakesh_25.03.2011_15-23-09.2011_15-23-09.JPG), Rudko | CC0 | no |
| `country-sdn` | boats on the Nile below a bridge, the sun low in the haze, filed under Khartoum | [Commons, النيل، الخرطوم ،السودان.jpg](https://commons.wikimedia.org/wiki/File:%D8%A7%D9%84%D9%86%D9%8A%D9%84%D8%8C_%D8%A7%D9%84%D8%AE%D8%B1%D8%B7%D9%88%D9%85_%D8%8C%D8%A7%D9%84%D8%B3%D9%88%D8%AF%D8%A7%D9%86.jpg), سندس ادريس | CC0 | no |
| `country-syr` | the Roman theatre at Bosra, filed under Scaenae frons in Bosra theatre | [Commons, 014, Bosra, theater.JPG](https://commons.wikimedia.org/wiki/File:014%2C_Bosra%2C_theater.JPG), Huldra | CC0 | no |
| `country-tun` | Avenue Habib Bourguiba from above, looking towards the port, Tunis | [Commons, TunisAveHabibBourguiba.jpg](https://commons.wikimedia.org/wiki/File:TunisAveHabibBourguiba.jpg), Dacoslett | CC0 | no |
| `country-pse` | the hillside of Bethlehem, filed under Views of Bethlehem | [Commons, Bethlehem Overlooking.jpg](https://commons.wikimedia.org/wiki/File:Bethlehem_Overlooking.jpg), Maysa Al Shaer | public domain | no |
| `country-yem` | the old city of Sanaa with a minaret and the mountains, photographed in 1996 | [Commons, 1996-Yemen Sanna (29044386125).jpg](https://commons.wikimedia.org/wiki/File:1996-Yemen_Sanna_%2829044386125%29.jpg), Werner Bayer | CC0 | no |
| `country-alb` | Tirana from a rooftop with the mountains behind, GPS in Tirana | [Commons, Tirana from Above 2016.jpg](https://commons.wikimedia.org/wiki/File:Tirana_from_Above_2016.jpg), mikestuartwood | public domain | no |
| `country-arm` | central Yerevan with Mount Ararat behind | [Commons, Ararat och centrum 20260311 bild 1.jpg](https://commons.wikimedia.org/wiki/File:Ararat_och_centrum_20260311_bild_1.jpg), David Castor | CC0 | no |
| `country-aze` | the rooftops of Baku seen from the Maiden Tower | [Commons, VIEW FROM MAIDEN TOWER BAKU … ל העלמה באקו ב.jpg](https://commons.wikimedia.org/wiki/File:VIEW_FROM_MAIDEN_TOWER_BAKU_ROOF_B.%D7%AA%D7%A6%D7%A4%D7%99%D7%AA_%D7%9E%D7%A8%D7%90%D7%A9_%D7%9E%D7%92%D7%93%D7%9C_%D7%94%D7%A2%D7%9C%D7%9E%D7%94_%D7%91%D7%90%D7%A7%D7%95_%D7%91.jpg), Avisadehh | CC0 | no |
| `country-blr` | the Church of the Holy Spirit and the Basilian monastery, Minsk | [Commons, Царква Святога Духа і манастыр базыльян.jpg](https://commons.wikimedia.org/wiki/File:%D0%A6%D0%B0%D1%80%D0%BA%D0%B2%D0%B0_%D0%A1%D0%B2%D1%8F%D1%82%D0%BE%D0%B3%D0%B0_%D0%94%D1%83%D1%85%D0%B0_%D1%96_%D0%BC%D0%B0%D0%BD%D0%B0%D1%81%D1%82%D1%8B%D1%80_%D0%B1%D0%B0%D0%B7%D1%8B%D0%BB%D1%8C%D1%8F%D0%BD.jpg), DBatura | CC0 | no |
| `country-bih` | the Ottoman old town of Mostar from the Old Bridge at sunset | [Commons, Mostar old town at sunset.jpg](https://commons.wikimedia.org/wiki/File:Mostar_old_town_at_sunset.jpg), Duesseljan | CC0 | no |
| `country-geo` | the Abanotubani bath district below the old town, GPS in Tbilisi | [Commons, Tbilisi Love You- Urban Phot … tafa Meraji 23.jpg](https://commons.wikimedia.org/wiki/File:Tbilisi_Love_You-_Urban_Photos%2C_Canon_Photos%2C_Creative_Commons%2C_Mostafa_Meraji_23.jpg), Mostafameraji | CC0 | no |
| `country-kaz` | the domes of the Zenkov Cathedral, GPS in Almaty | [Commons, Zenkov Cathedral, Almaty.jpg](https://commons.wikimedia.org/wiki/File:Zenkov_Cathedral%2C_Almaty.jpg), Bgag | CC0 | no |
| `country-kgz` | Bishkek with snow-capped mountains behind, filed under Views of Bishkek | [Commons, 25 razgledi iz Biškeka (4).JPG](https://commons.wikimedia.org/wiki/File:25_razgledi_iz_Bi%C5%A1keka_%284%29.JPG), Ljuba brank | public domain | no |
| `country-mda` | the clock tower of the City Hall at sunset, GPS in Chișinău | [Commons, Мэрия, Кишинев, Республика М … (50714726236).jpg](https://commons.wikimedia.org/wiki/File:%D0%9C%D1%8D%D1%80%D0%B8%D1%8F%2C_%D0%9A%D0%B8%D1%88%D0%B8%D0%BD%D0%B5%D0%B2%2C_%D0%A0%D0%B5%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B0_%D0%9C%D0%BE%D0%BB%D0%B4%D0%BE%D0%B2%D0%B0_Primaria%2C_Chisinau%2C_Republica_Moldova_City_Hall%2C_Chisinau%2C_Republic_of_Moldova_%2850714726236%29.jpg), Photobank MD | CC0 | no |
| `country-mne` | rooftops of Podgorica with the mountains behind | [Commons, DSC 0123 podgorica july 2017.jpg](https://commons.wikimedia.org/wiki/File:DSC_0123_podgorica_july_2017.jpg), Rakoon | CC0 | no |
| `country-mkd` | the Church of Saints Clement and Pantaleon, GPS in Ohrid | [Commons, 20170718 153932 July 2017 in Macedonia.jpg](https://commons.wikimedia.org/wiki/File:20170718_153932_July_2017_in_Macedonia.jpg), Rakoon | CC0 | no |
| `country-srb` | the Sava and Danube confluence at sunset from Kalemegdan, Belgrade | [Commons, Belgrade – Kalemegdan (2021) 04.jpg](https://commons.wikimedia.org/wiki/File:Belgrade_%E2%80%93_Kalemegdan_%282021%29_04.jpg), Imeao | CC0 | no |
| `country-tjk` | Jizew Lake between rock walls, Gorno-Badakhshan | [Commons, Jizew Lake.jpg](https://commons.wikimedia.org/wiki/File:Jizew_Lake.jpg), Benoît Vicart | CC0 | no |
| `country-tkm` | the mound of the Bronze Age town of Altyndepe in the Ahal steppe, filed under Altyndepe | [Commons, Altyndepe, Turkmenistan.jpg](https://commons.wikimedia.org/wiki/File:Altyndepe%2C_Turkmenistan.jpg), Limin Huan | public domain | no |
| `country-tur` | Anadolu Hisarı and the waterside houses on the Bosphorus, Istanbul | [Commons, Metropolitian Istanbul - Landscapes of Turkey 11.jpg](https://commons.wikimedia.org/wiki/File:Metropolitian_Istanbul_-_Landscapes_of_Turkey_11.jpg), Mostafameraji | CC0 | no |
| `country-ukr` | St George's Cathedral and the Town Hall tower, GPS in Lviv | [Commons, Lviv Saint George Cathedral … beth Church 01.JPG](https://commons.wikimedia.org/wiki/File:Lviv_Saint_George_Cathedral_as_seen_from_Elizabeth_Church_01.JPG), Юрій Булка | CC0 | no |
| `country-uzb` | the Kalyan minaret and the Poi Kalyan square, GPS in Bukhara | [Commons, Historic Centre of Bukhara 2023.9.jpg](https://commons.wikimedia.org/wiki/File:Historic_Centre_of_Bukhara_2023.9.jpg), ほっきー | CC0 | no |
| `rel-derived` | | | | |
| `rel-subset` | | | | |
| `rel-independent` | | | | |
| `panel-csv` | | | | |
| `panel-parquet` | | | | |
| `panel-sqlite` | | | | |
| `panel-recon-pairs` | | | | |
| `panel-recon-cells` | | | | |
| `panel-mou` | | | | |
