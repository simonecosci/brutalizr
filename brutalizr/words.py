"""Vocabularies and vulgar name generator."""
from __future__ import annotations

import random
import re


def _g(gender: str, words: str) -> list[tuple[str, str]]:
    return [(w, gender) for w in words.split()]


def _o_to_a(adj: str, gender: str) -> str:
    return adj[:-1] + "a" if gender == "f" and adj.endswith("o") else adj


_FR_FEM = (("e", "e"), ("eux", "euse"), ("if", "ive"), ("on", "onne"), ("el", "elle"),
           ("ul", "ulle"), ("en", "enne"), ("er", "ere"), ("", "e"))


def _fr(adj: str, gender: str) -> str:
    if gender != "f":
        return adj
    for masc, fem in _FR_FEM:
        if adj.endswith(masc):
            return adj[:len(adj) - len(masc)] + fem


def _de(adj: str, gender: str) -> str:
    # strong declension (no article): -er / -e / -es
    ending = {"m": "er", "f": "e", "n": "es"}[gender]
    return adj + (ending[1:] if adj.endswith("e") else ending)


# nouns are (word, gender): 'm', 'f' or 'n'; adjectives are inflected to agree with the
# vocabulary's "inflect" (default: Italian-style o -> a). "masc/fem" gives both forms
# explicitly, for words the rule would get wrong.
VOCAB = {
    "it": {
        "order": "noun-adj",
        "nouns": _g("m", """
            cazzo stronzo culo coglione cesso bastardo pirla cazzone leccaculo
            paraculo rompipalle rompicoglioni testadicazzo sfigato belin cacchio
            sticazzi cacasotto cagone scorreggione cazzaro cazzeggio fesso babbeo
            cretino deficiente imbecille idiota somaro maiale maialone porco
            ciccione trippone scemo tamarro coatto burino cafone zotico buzzurro
            bifolco gonzo merdaiolo pidocchio scarafaggio verme lombrico sorcio
            sozzone porcellone stronzone culone cacone pisciatoio pisciasotto
            sputazzo catarro moccolo moccio brufolo foruncolo pustolone rutto peto
            pernacchio sputo lecchino ruffiano sfaticato fannullone scansafatiche
            perdigiorno beota allocco citrullo tonto rimbambito bamba bischero
            grullo coglioncione minchione pacco bidone schifo vomito letame
            liquame sterco pattume rudere catorcio rottame ciarpame accrocco
            pastrocchio troiaio casino bordello puttanaio merdaio porcile letamaio
            smerdone pisello uccello sedere deretano magnaccia cagacazzo
            rompicazzo puzzone mentecatto ciucciapalle bacucco rincoglionito
            sciroccato cialtrone pagliaccio buffone tanghero villano
        """) + _g("f", """
            minchia merda cagata puttanata stronzata cazzata scoreggia chiappa
            mona ciofeca schifezza porcata zozzeria fetecchia pippa minchiata
            belinata fregnaccia fregna sola cagnara caciara sbobba brodaglia
            poltiglia fogna latrina pisciata cacata pugnetta sega chiavica
            munnezza monnezza fregatura bufala boiata vaccata fesseria scemenza
            baggianata stupidata cazzimma rogna scabbia piattola zecca pulce
            blatta pantegana zanzara cozza befana carogna canaglia sanguisuga
            lagna palla menata rottura mazzetta puzza puzzetta loffa flatulenza
            diarrea cacarella emorroide pustola verruca forfora crosta muffa
            sozzura sporcizia lordura chiappona pernacchia sberla scorreggina
            capocchia stronzetta mezzasega testadura cacca pupu cagatina
        """),
        "adjs": """
            moscio lurido schifoso marcio fetente rincoglionito sfondato merdoso
            spompato sbronzo puzzolente sputtanato fottuto maledetto smerdato
            ammuffito sbroccato scazzato incazzato scoglionato sgangherato bollito
            flaccido rancido lercio sciancato rattoppato sbrindellato
            inchiappettato rintronato spernacchiato tarocco sfasciato cagato
            smidollato sbiadito rattrappito scassato scalcinato scombinato
            sbilenco storto sghembo zoppo sdentato spelacchiato pidocchioso
            pulcioso rognoso bavoso sbavato sudato unto bisunto appiccicoso
            viscido molliccio floscio sgonfio sfiatato sfinito rincitrullito
            rimbambito imbranato impedito incapace inutile scadente pezzente
            tirchio taccagno spilorcio schifato nauseabondo vomitevole disgustoso
            ripugnante stomachevole ignobile infame vigliacco becero zozzo sozzo
            sudicio incrostato ammaccato arrugginito tarlato bucato scoppiato
            fuso fulminato sballato strafatto ubriaco ciucco brillo stracotto
            scotto bruciato carbonizzato raffermo stantio avariato guasto scaduto
            fregato inculato sfottuto incasinato impestato smandrappato scrauso
            sciatto trasandato sbracato stravaccato spaparanzato svaccato stonato
            incazzoso cazzuto fetido maleodorante pestilenziale lebbroso
            scabbioso rachitico sbiellato sfigato stronzissimo sputacchiato
            pisciato cacato scorreggiato sbudellato spappolato squinternato
            sconclusionato raffazzonato abborracciato arrangiato posticcio
            taroccato sbattuto sfatto spiaccicato stropicciato sgualcito unticcio
            grasso lardoso panzuto chiattone tracagnotto mezzocotto sbollito
        """.split(),
    },
    "en": {
        "order": "adj-noun",
        "nouns": _g("m", """
            fuck shit crap ass arse bastard dick piss bollocks wanker turd douche
            bugger prick jerk dumbass shithead asshat dipshit knob bellend tosser
            scumbag buttface crapper fart clusterfuck fuckwit asshole jackass
            dickhead dumbfuck motherfucker shitstorm shitshow shitbag shitbird
            shitstain fuckup fuckface fucknut dickweed dickwad douchebag
            douchecanoe twat git pillock plonker numpty muppet nitwit dingbat dork
            dweeb moron idiot imbecile cretin halfwit nincompoop bonehead meathead
            knucklehead airhead butthead butthole buttmunch assclown asswipe
            assmonkey shitweasel turdburger craphole shithole dumpster garbage
            trash sleazebag slimeball scumbucket weasel rat cockroach maggot
            toerag scrote wazzock berk prat nob bawbag minger bullshit horseshit
            chickenshit crapfest snafu fubar dumpsterfire trainwreck pisshead
            sod arsehole arsewipe knobhead knobend dipstick jerkoff wankstain
            clown goober doofus dumbo schmuck putz klutz dumbbell pinhead fathead
            blockhead dunce booger snot loogie barf puke vomit dung manure sewage
            sludge gunk crud scuzz dreck swill slop stank stench burp belch
            hemorrhoid pimple wart scab fleabag dirtbag lowlife bozo buffoon
            jabroni chump sucker loser
        """),
        "adjs": """
            fucking shitty crappy bloody damn pissed sodding stinky lousy frigging
            rotten filthy halfassed crusty moldy smelly useless drunk wonky busted
            godawful piss_poor assbackwards fucked goddamn friggin effing freaking
            bleeding blasted cursed janky dodgy manky grotty scuzzy grimy greasy
            slimy sleazy sloppy soggy mushy flabby floppy limp saggy droopy funky
            rancid putrid fetid festering stinking reeking mouldy musty stale
            rusty rickety creaky wobbly lopsided crooked shoddy crummy cruddy
            trashy tacky cheap knockoff bootleg broken borked hosed fubared boned
            screwed wrecked trashed hammered wasted plastered sloshed tipsy
            smashed stoned baked fried toasted braindead clueless witless
            gormless daft dimwitted halfbaked harebrained lazy worthless
            pointless hopeless gutless spineless snotty cranky grumpy pissy whiny
            sweaty farty poopy barfy pukey gassy itchy scabby pimply warty hairy
            lumpy bloated constipated bonkers nutty batshit apeshit shitfaced
            motherfucking unholy ungodly wretched miserable pathetic lame sorry
            dumb dopey goofy derpy crapass bullshit shitass dickish
            assholish douchey bollocksed knackered buggered cocked_up gobsmacked
        """.split(),
    },
    "es": {
        "order": "noun-adj",
        "nouns": _g("m", """
            cabron gilipollas capullo pendejo culo carajo huevon mamon pedo
            soplapollas tontolculo mamarracho mojon pringado boludo pelotudo
            cabronazo mamonazo imbecil idiota tarado pajero pajillero comemierda
            lameculos chupapollas tocapelotas pelmazo pesado merluzo besugo
            atontado zoquete berzotas melon cenutrio mastuerzo cagon cagueta
            zurullo cerdo marrano puerco gusano piojo bicho engendro adefesio
            esperpento churro desastre bodrio pedorro eructo moco vomito pis
            meado petardo ladrillo rollo chorizo mangante sinverguenza caradura
            cantamananas pagafantas mequetrefe papanatas bobalicon pazguato
            majadero patan palurdo paleto cateto garrulo hortera cagadero
            estercolero vertedero chiquero muermo truno ojete orto forro sorete
            boludazo pelele payaso bufon gandul vago
        """) + _g("f", """
            mierda cagada chorrada cutrez chapuza meada pedorreta caca porqueria
            basura mamada pendejada gilipollez huevada boludez pelotudez cabronada
            putada jodienda marranada guarrada cochinada mierdecilla birria
            patata chinche cucaracha rata sabandija plasta piltrafa bazofia
            pocilga cloaca letrina diarrea cagalera ladilla garrapata pulga
            mugre cochambre peste pestilencia ventosidad almorrana verruga
            espinilla costra caspa tontada memez sandez burrada
            gansada paja zorrada
        """),
        "adjs": """
            podrido asqueroso cutre jodido cagado apestoso borracho chungo pocho
            guarro cochino mugriento acojonado puteado empanado zumbado
            putrefacto rancio pasado caducado mohoso oxidado roto escacharrado
            cascado tirado pringoso grasiento sudado sudoroso baboso mocoso
            piojoso sarnoso pulgoso cochambroso andrajoso harapiento desgraciado
            maldito condenado chapucero torpe tonto lelo memo bobo zopenco
            majara chalado pirado colgado fumado ciego mamado colocado flipado
            rayado quemado reventado petado fundido chafado abollado torcido
            cojo tuerto calvo feo gordo fofo blandengue flojo vago gandul inutil
            patetico lamentable penoso cansino pesado repugnante nauseabundo
            hediondo pestilente fetido mugroso marrano puerco sucio cagon
            meado vomitado eructado pedorro jodidisimo enmohecido agusanado
            apolillado carcomido desvencijado destartalado chungalo malparido
            pinche culero mamerto atontado alelado amuermado empalmado
        """.split(),
    },
    "fr": {
        "order": "noun-adj",
        "inflect": _fr,
        "nouns": _g("m", """
            con connard enfoire salaud salopard batard abruti cretin debile idiot
            imbecile cornichon couillon trouduc emmerdeur branleur glandeur minable
            naze pignouf plouc beauf bouffon guignol tocard ringard boulet blaireau
            cafard cancrelat morpion pou rat porc cochon goret veau ane dindon
            crapaud merdier bordel foutoir gachis bousin caca pipi pet rot prout
            crachat mollard vomi degueulis etron colombin furoncle bouton cul trou
            slip calecon fumier purin egout cloaque taudis bouge clebs cabot gland
            baltringue bouseux charlot zigoto nigaud benet dadais gugusse pitre
            sagouin malotru mufle goujat rustre butor lourdaud pochtron poivrot
            soulard ivrogne morveux
        """) + _g("f", """
            merde chiasse crotte bouse fiente pisse gerbe morve vomissure connerie
            couillonnade saloperie cochonnerie merdouille daube bouillie puree
            ordure raclure pourriture vermine charogne punaise blatte tique puce
            limace larve nouille andouille buse bourrique truie vache carne bique
            teigne peste plaie galere foirade bourde boulette gaffe bavure arnaque
            embrouille chierie poubelle fosse latrine chiotte tinette flaque crasse
            mouise deche poisse cata catastrophe bouffonnerie tache cruche gourde
            patate courge banane quiche tanche cloche
        """),
        "adjs": """
            pourri moisi rance crade cradingue degueulasse sale puant merdique
            foireux chiant emmerdant gonflant lourd nul foutu maudit damne/damnee
            satane/satanee bourre/bourree defonce/defoncee pete/petee crame/cramee
            cuit rassis/rassie gerbant ecoeurant immonde infect ignoble miteux
            pouilleux galeux teigneux crasseux poisseux gluant visqueux baveux
            merdeux boiteux bancal branlant tordu bossele/bosselee cabosse/cabossee
            rouille/rouillee ebreche/ebrechee fele/felee troue/trouee
            dechire/dechiree rapiece/rapiecee pathetique lamentable navrant bete
            stupide demeure/demeuree paume/paumee largue/larguee flasque laid moche
            affreux hideux difforme bossu chauve edente/edentee pele/pelee
            rachitique malade tare/taree timbre/timbree cingle/cinglee
            siphonne/siphonnee glauque louche vereux vicieux sournois fourbe lache
            feignant faineant mollasson grognon radin pingre pourave vaseux fumeux
            creve/crevee nique/niquee bousille/bousillee flingue/flinguee
            encule/enculee deglingue/deglinguee esquinte/esquintee amoche/amochee
            rabougri ratatine/ratatinee ramolli abime/abimee bouffi
            boursoufle/boursouflee merdouilleux putride fetide nauseabond
            faisande/faisandee avarie/avariee perime/perimee
        """.split(),
    },
    "de": {
        "order": "adj-noun",
        "inflect": _de,
        "nouns": _g("m", """
            arsch depp idiot trottel penner wichser vollidiot mistkerl bloedmann
            dreck mist schrott furz kackhaufen hosenscheisser schwachkopf dummkopf
            hohlkopf pisser saftsack sack lump schuft hornochse esel affe lappen
            pfosten honk lauch kasper clown spinner schmarotzer schleimer
            arschkriecher wurm kotzbrocken scheisskerl drecksack mistkaefer stinker
            muell pfusch rotz popel pickel schwanz pimmel grosskotz warmduscher
            dreckspatz schmutzfink stinkstiefel miesepeter korinthenkacker
            klugscheisser erbsenzaehler pfuscher stuemper versager nichtsnutz
            taugenichts faulpelz schnorrer furzknoten blindgaenger rohrkrepierer
            sauhaufen saustall misthaufen schweinestall scheisshaufen
        """) + _g("f", """
            scheisse kacke sau drecksau pisse kotze kackwurst nervensaege pfeife
            flasche niete kroete ratte wanze zecke laus kakerlake pest seuche
            pfuscherei sauerei schweinerei schande gurke kruecke bruchbude absteige
            muellhalde kloake jauche bruehe schmiere flitzpiepe dumpfbacke
            arschgeige pissnelke hackfresse furzkanone schnapsdrossel kloschuessel
            schnarchnase transuse heulsuse labertasche quasselstrippe tranfunzel
            schlafmuetze pottsau kackbratze
        """) + _g("n", """
            arschloch miststueck dreckstueck ekel schwein rindvieh ferkel kamel
            loch klo scheisshaus pissoir wrack elend desaster chaos weichei gesocks
            pack gesindel mistvieh stinktier faultier dreckloch arschgesicht
            sackgesicht schlitzohr grossmaul plappermaul schandmaul luder aas biest
            scheusal pissbecken rattenloch drecksnest kaff
        """),
        "adjs": """
            bloed doof dumm bescheuert beknackt behaemmert bekloppt verbloedet
            versifft verkackt verschissen beschissen verpisst vermurkst verhunzt
            versaut verlaust verlottert verranzt ranzig vergammelt verschimmelt
            schimmelig stinkig stinkend eklig widerlich ekelhaft dreckig schmierig
            schleimig klebrig verdammt verflucht verfickt mies lausig schaebig
            marode morsch rostig wackelig schief krumm lahm faul traege nutzlos
            sinnlos hirnlos ahnungslos planlos kopflos besoffen breit zugedroehnt
            bekifft verkatert verpeilt verwirrt verstrahlt durchgeknallt irre
            gestoert krank uebel fies gemein hinterhaeltig mickrig popelig
            labberig schlapp schlaff fett speckig verfilzt zottelig lumpig
            abgefuckt abgewrackt abgenutzt ausgeleiert verbeult zerknittert
            zerfleddert muffig modrig faulig verrottet verkommen verdorben oede
            kaputt zerbrochen verbogen verkorkst vergurkt versemmelt verbockt
            vergeigt angeschimmelt abgestanden versumpft verschnarcht verpennt
            verlogen verpfuscht schrottreif peinlich erbaermlich jaemmerlich
            armselig klaeglich laecherlich schwachsinnig saudumm strunzdumm
            stockbesoffen
        """.split(),
    },
    "nap": {
        "order": "noun-adj",
        "nouns": _g("m", """
            strunzo cesso scemo fesso cafone mammalucco uallarone cacasotto
            chiachiello piezzemmerda pallista pereto paccaro scugnizzo guaglione
            pernacchio scazzamauriello lazzaro mariuolo cetrulo babbasone ciuccio
            puorco scarrafone suriciello perucchio chiattillo cuorno curnuto guappo
            pulecenella cazzaro nciucio casino jettatore tamarro
        """) + _g("f", """
            loffa cacata zella munnezza uallera cazzimma sfaccimma fessaria
            strunzata pucchiacca chiavica ammuina papocchia ciofeca pettola mappina
            fetenzia schifezza zuzzimma mazzata cofecchia jella cucuzza capatosta
            mmerda nzogna puzza
        """),
        "adjs": """
            fetente zuzzuso/zuzzosa nzevuso/nzevosa stunato chiatto
            stuorto/storta cecato scurnacchiato cazzimmuso/cazzimmosa sfasulato
            scassato sfrantummato ammaccato smerzato scuncecato scumbinato
            sciancato zelluso/zellosa muccuso/muccosa rugnuso/rugnosa
            spuorco/sporca pezzente malamente mbriaco nfame
            abbuffato ntussecato nguaiato ncazzato sfastidiato allummato sfunnato
            stracquato arraggiato ammusciato ammuffuto scurdato scamazzato spennato
            nzallanuto ntrunato sfurtunato lurdo/lorda cuotto/cotta muorto/morta
            sguarrato
        """.split(),
    },
}

_SPLIT = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")


def split_words(name: str) -> list[str]:
    parts: list[str] = []
    for chunk in name.split("_"):
        parts.extend(_SPLIT.findall(chunk))
    return parts or [name]


def detect_style(core: str) -> str:
    letters = [c for c in core if c.isalpha()]
    if len(letters) > 1 and all(c.isupper() for c in letters):
        return "UPPER"
    if "_" in core.strip("_"):
        return "snake"
    if core[:1].isupper():
        return "Pascal"
    if any(c.isupper() for c in core):
        return "camel"
    return "lower"


def apply_style(words: list[str], style: str, lower_default: str) -> str:
    # words may contain "_" (e.g. piss_poor): split them
    flat: list[str] = []
    for w in words:
        flat.extend(p for p in w.split("_") if p)
    if style == "lower":
        style = lower_default
    if style == "UPPER":
        return "_".join(w.upper() for w in flat)
    if style == "snake":
        return "_".join(w.lower() for w in flat)
    if style == "Pascal":
        return "".join(w.capitalize() for w in flat)
    return flat[0].lower() + "".join(w.capitalize() for w in flat[1:])


class NameForge:
    """Generates unique vulgar names, preserving the style of the original name."""

    def __init__(self, lang: str = "it", seed: int | None = None, reserved: set[str] | None = None):
        if lang == "mix":
            self.vocabs = list(VOCAB.values())
        else:
            self.vocabs = [VOCAB[lang]]
        self.rng = random.Random(seed)
        self.used: set[str] = set(reserved or ())

    def _phrase(self, n_words: int) -> list[str]:
        v = self.rng.choice(self.vocabs)
        noun, gender = self.rng.choice(v["nouns"])
        pool = [a for a in v["adjs"] if a.split("/")[0] != noun]   # no "sfigatoSfigato"
        adjs = self.rng.sample(pool, k=max(1, n_words - 1))
        inflect = v.get("inflect", _o_to_a)
        adjs = [(a.split("/")[gender == "f"] if "/" in a else inflect(a, gender))
                for a in adjs]
        return [noun, *adjs] if v["order"] == "noun-adj" else [*adjs, noun]

    def forge(self, original: str, lower_default: str = "camel") -> str:
        m = re.match(r"^(_*)(.*?)(_*)$", original)
        pre, core, post = m.group(1), m.group(2), m.group(3)
        style = detect_style(core or original)
        n_words = min(3, max(2, len(split_words(core))))
        for attempt in range(200):
            # when short combinations run out, make the phrase longer
            extra = 0 if attempt < 40 else 1 if attempt < 120 else 2
            words = self._phrase(n_words + extra)
            candidate = pre + apply_style(words, style, lower_default) + post
            if candidate not in self.used:
                self.used.add(candidate)
                return candidate
        i = 2
        base = pre + apply_style(self._phrase(n_words), style, lower_default) + post
        while f"{base}{i}" in self.used:
            i += 1
        self.used.add(f"{base}{i}")
        return f"{base}{i}"
