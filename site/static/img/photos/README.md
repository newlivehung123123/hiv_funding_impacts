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

The ten Commons and Unsplash rows were filed on 3 October 2026. Each place was checked
against the file's Commons categories, the GPS position or the place the photographer
recorded on Unsplash. Comoros, Equatorial Guinea and São Tomé and Príncipe still have no
photograph, so `country-com`, `country-gnq` and `country-stp` are drawn as plain metal.
No CC0, public domain or Unsplash photograph of Comoros or Equatorial Guinea passed the
place check, and the CC BY-SA candidates would need a credit line the site does not yet
carry.

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
| `rel-derived` | | | | |
| `rel-subset` | | | | |
| `rel-independent` | | | | |
| `panel-csv` | | | | |
| `panel-parquet` | | | | |
| `panel-sqlite` | | | | |
| `panel-recon-pairs` | | | | |
| `panel-recon-cells` | | | | |
| `panel-mou` | | | | |
