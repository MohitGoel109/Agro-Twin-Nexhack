"""Question bank and owner-form schema (English + Hindi). Hindi text needs review by a native speaker."""

SYSTEMS = {
    "engine": ("Engine", "इंजन"),
    "cooling": ("Cooling system", "कूलिंग सिस्टम"),
    "brakes": ("Brakes", "ब्रेक"),
    "hydraulics": ("Hydraulics", "हाइड्रोलिक"),
    "drivetrain": ("Gearbox / clutch / bearings", "गियरबॉक्स / क्लच / बेयरिंग"),
    "electrical": ("Battery / electrical", "बैटरी / बिजली"),
    "tyres": ("Tyres / steering", "टायर / स्टीयरिंग"),
    "fuel": ("Fuel system", "ईंधन प्रणाली"),
}

GROUPS = [
    ("sound", "What it sounds like", "आवाज़"),
    ("smell", "Smell and smoke", "गंध और धुआं"),
    ("look", "What you can see", "जो आप देख सकते हैं"),
    ("feel", "How it feels to drive", "चलाने पर कैसा लगता है"),
    ("trend", "How long and how fast", "कब से और कितना बढ़ रहा है"),
]


def O(oid, en, hi, w=0, systems=()):
    return {"id": oid, "en": en, "hi": hi, "weight": w, "systems": list(systems)}


def Q(qid, group, qtype, en, hi, options):
    opts = list(options) + [O("unsure", "Not sure", "पता नहीं")]
    return {"id": qid, "group": group, "type": qtype, "text_en": en, "text_hi": hi, "options": opts}


NONE = lambda: O("none", "None / normal", "कुछ नहीं / सामान्य")

QUESTION_BANK = [
    Q("sound", "sound", "multi", "What sound is the machine making?", "मशीन कैसी आवाज़ कर रही है?", [
        O("knocking", "Knocking or hammering", "ठक-ठक / हथौड़े जैसी", 3, ["engine"]),
        O("grinding", "Grinding or crunching", "घिसने / कड़कड़ाने की", 3, ["drivetrain"]),
        O("squealing", "Squealing or screeching", "चीं-चीं / तेज़ चीख", 2, ["engine", "brakes"]),
        O("whining", "Whining (hydraulics / pump)", "सीटी जैसी (हाइड्रोलिक / पंप)", 2, ["hydraulics"]),
        O("rattling", "Rattling or loose parts", "खड़खड़ाहट", 1, ["drivetrain", "tyres"]),
        O("clicking", "Clicking when starting", "स्टार्ट करते समय क्लिक", 2, ["electrical"]),
        NONE()]),
    Q("sound_when", "sound", "multi", "When does the sound happen?", "आवाज़ कब आती है?", [
        O("when_start", "When starting", "स्टार्ट करते समय"),
        O("when_load", "Under load / working", "काम करते समय"),
        O("when_turn", "While turning", "मोड़ते समय"),
        O("when_brake", "While braking", "ब्रेक लगाते समय"),
        O("when_always", "All the time", "हर समय")]),
    Q("smell", "smell", "multi", "Do you notice any smell?", "क्या कोई गंध आ रही है?", [
        O("smell_rubber", "Burning rubber / clutch", "जलते रबर / क्लच की", 3, ["drivetrain"]),
        O("smell_oil", "Burnt oil", "जले तेल की", 2, ["engine"]),
        O("smell_diesel", "Diesel / fuel", "डीज़ल / ईंधन की", 2, ["fuel"]),
        O("smell_coolant", "Sweet coolant smell", "मीठी कूलेंट गंध", 2, ["cooling"]),
        O("smell_elec", "Electrical burning", "बिजली के तार जलने की", 3, ["electrical"]),
        NONE()]),
    Q("smoke", "smell", "single", "What colour is the exhaust smoke?", "धुएं का रंग कैसा है?", [
        O("smoke_black", "Black", "काला", 2, ["fuel", "engine"]),
        O("smoke_white", "White", "सफेद", 2, ["cooling"]),
        O("smoke_blue", "Blue", "नीला", 2, ["engine"]),
        O("smoke_none", "No smoke", "धुआं नहीं")]),
    Q("leaks", "look", "multi", "Any leak or wet patch under the machine?", "मशीन के नीचे कोई रिसाव या गीलापन?", [
        O("leak_engine_oil", "Engine oil", "इंजन ऑयल", 2, ["engine"]),
        O("leak_coolant", "Coolant (green/pink water)", "कूलेंट (हरा/गुलाबी पानी)", 2, ["cooling"]),
        O("leak_hydraulic", "Hydraulic oil", "हाइड्रोलिक ऑयल", 2, ["hydraulics"]),
        O("leak_diesel", "Diesel", "डीज़ल", 2, ["fuel"]),
        O("leak_brake", "Brake fluid near wheels", "पहियों के पास ब्रेक फ्लूइड", 3, ["brakes"]),
        NONE()]),
    Q("coolant_low", "look", "single", "Is the coolant level low (check ONLY when the engine is cold)?", "कूलेंट कम है? (सिर्फ ठंडे इंजन पर देखें)", [
        O("coolant_low_yes", "Yes, low", "हाँ, कम है", 2, ["cooling"]),
        O("coolant_low_no", "No, normal", "नहीं, सामान्य")]),
    Q("oil_state", "look", "single", "What does the engine oil look like on the dipstick?", "डिपस्टिक पर इंजन ऑयल कैसा दिखता है?", [
        O("oil_milky", "Milky / creamy", "दूधिया / मलाई जैसा", 3, ["engine", "cooling"]),
        O("oil_black", "Very black or gritty", "बहुत काला या किरकिरा", 1, ["engine"]),
        O("oil_normal", "Normal / clean", "सामान्य / साफ़")]),
    Q("wear", "look", "multi", "Do you see cracks or low pressure?", "क्या दरारें या कम हवा दिखती है?", [
        O("belt_cracked", "Cracked or frayed belt", "फटी / घिसी बेल्ट", 2, ["engine"]),
        O("tyre_damage", "Cracked or bulging tyre", "फटा / उभरा टायर", 2, ["tyres"]),
        O("tyre_low", "Low tyre pressure", "टायर में हवा कम", 1, ["tyres"]),
        NONE()]),
    Q("wires", "look", "multi", "Rust or damaged wires?", "जंग या खराब तार?", [
        O("rust", "Heavy rust", "ज़्यादा जंग", 1, ["electrical"]),
        O("wires_chewed", "Chewed or loose wires (rats)", "कुतरे / ढीले तार (चूहे)", 3, ["electrical"]),
        NONE()]),
    Q("warning_light", "look", "single", "Which dashboard warning light is on?", "डैशबोर्ड पर कौन सी चेतावनी लाइट जल रही है?", [
        O("wl_oil", "Oil pressure", "ऑयल प्रेशर", 3, ["engine"]),
        O("wl_temp", "Temperature", "तापमान", 3, ["cooling"]),
        O("wl_battery", "Battery / charging", "बैटरी / चार्जिंग", 2, ["electrical"]),
        O("wl_brake", "Brake", "ब्रेक", 3, ["brakes"]),
        O("wl_other", "Some other light", "कोई और लाइट", 1),
        O("wl_none", "No warning light", "कोई लाइट नहीं")]),
    Q("steam", "look", "single", "Is steam coming from the radiator or bonnet?", "रेडिएटर या बोनट से भाप निकल रही है?", [
        O("steam_yes", "Yes", "हाँ", 3, ["cooling"]),
        O("steam_no", "No", "नहीं")]),
    Q("vibration", "feel", "single", "Is the machine vibrating?", "क्या मशीन कांप रही है?", [
        O("vib_mild", "A little more than usual", "सामान्य से थोड़ा ज़्यादा", 1, ["drivetrain"]),
        O("vib_strong", "Strongly (seat / steering shakes)", "तेज़ (सीट / स्टीयरिंग हिलता है)", 3, ["drivetrain"]),
        O("vib_none", "Normal", "सामान्य")]),
    Q("steering", "feel", "single", "How does the steering feel?", "स्टीयरिंग कैसा लग रहा है?", [
        O("steer_heavy", "Heavy / hard to turn", "भारी / घुमाने में कठिन", 2, ["hydraulics"]),
        O("steer_loose", "Loose / too much play", "ढीला / ज़्यादा खेल", 2, ["tyres"]),
        O("steer_normal", "Normal", "सामान्य")]),
    Q("brake_feel", "feel", "single", "How does the brake pedal feel?", "ब्रेक पैडल कैसा लग रहा है?", [
        O("brake_spongy", "Soft or spongy", "नरम / स्पंजी", 3, ["brakes"]),
        O("brake_long", "Goes down too far", "बहुत नीचे तक जाता है", 2, ["brakes"]),
        O("brake_pull", "Machine pulls to one side", "मशीन एक तरफ खिंचती है", 2, ["brakes", "tyres"]),
        O("brake_normal", "Normal", "सामान्य")]),
    Q("gears", "feel", "multi", "Clutch or gear problems?", "क्लच या गियर की समस्या?", [
        O("clutch_slip", "Clutch slipping", "क्लच फिसल रहा है", 2, ["drivetrain"]),
        O("gear_hard", "Hard to change gears", "गियर बदलना कठिन", 2, ["drivetrain"]),
        NONE()]),
    Q("starting", "feel", "multi", "How is starting?", "स्टार्ट करना कैसा है?", [
        O("start_hard", "Hard to start", "स्टार्ट होने में दिक्कत", 2, ["engine", "fuel"]),
        O("start_slow", "Slow cranking", "धीमा क्रैंकिंग", 2, ["electrical"]),
        O("lights_dim", "Lights are dim", "लाइट मद्धम", 1, ["electrical"]),
        NONE()]),
    Q("power", "feel", "single", "Is there loss of power?", "क्या ताकत कम हुई है?", [
        O("power_loss", "Yes, weak under load", "हाँ, लोड में कमज़ोर", 2, ["engine", "fuel"]),
        O("power_ok", "No", "नहीं")]),
    Q("temp_gauge", "feel", "single", "What does the temperature gauge show?", "तापमान गेज क्या दिखा रहा है?", [
        O("temp_high", "Higher than usual", "सामान्य से ज़्यादा", 2, ["cooling"]),
        O("temp_red", "In the red zone", "लाल निशान में", 3, ["cooling"]),
        O("temp_normal", "Normal", "सामान्य")]),
    Q("lift", "feel", "single", "How does the hydraulic lift work?", "हाइड्रोलिक लिफ्ट कैसे काम कर रही है?", [
        O("lift_slow", "Slow or jerky", "धीमी या झटके वाली", 2, ["hydraulics"]),
        O("lift_normal", "Normal", "सामान्य")]),
    Q("started", "trend", "single", "When did the problem start?", "समस्या कब शुरू हुई?", [
        O("started_today", "Today", "आज"),
        O("started_week", "This week", "इस हफ्ते"),
        O("started_month", "This month", "इस महीने"),
        O("started_long", "A long time ago", "काफी पहले")]),
    Q("worse", "trend", "single", "Is it getting worse?", "क्या यह बढ़ रही है?", [
        O("worse_yes", "Yes, getting worse", "हाँ, बढ़ रही है"),
        O("worse_same", "About the same", "लगभग वैसी ही"),
        O("worse_no", "Getting better", "ठीक हो रही है")]),
]

# Owner form schema (rendered generically by the page; validated in scoring.py)
OWNER_FIELDS = [
    {"id": "ownership_status", "type": "select", "en": "Ownership", "hi": "मालिकाना स्थिति",
     "options": [["purchased", "Owned / purchased", "अपनी / खरीदी हुई"], ["rented", "Rented", "किराये की"]]},
    {"id": "year", "type": "number", "min": 1980, "max": 2100, "en": "Year of purchase", "hi": "खरीद का वर्ष",
     "show_when": {"ownership_status": "purchased"}},
    {"id": "rental_duration_months", "type": "number", "min": 0, "max": 600,
     "en": "How many months has it been rented?", "hi": "कितने महीनों से किराये पर है?",
     "show_when": {"ownership_status": "rented"}},
    {"id": "warranty", "type": "select", "en": "Warranty status", "hi": "वारंटी की स्थिति",
     "options": [["under", "Under warranty", "वारंटी में"], ["ended", "Warranty ended", "वारंटी खत्म"], ["unsure", "Not sure", "पता नहीं"]]},
    {"id": "hours_total", "type": "number", "min": 0, "max": 60000, "en": "Engine hours on the hour meter", "hi": "आवर मीटर पर इंजन घंटे"},
    {"id": "hours_since_service", "type": "number", "min": 0, "max": 20000, "en": "Engine hours since last service", "hi": "पिछली सर्विस के बाद इंजन घंटे"},
    {"id": "hours_this_week", "type": "number", "min": 0, "max": 168, "en": "Hours used this week", "hi": "इस हफ्ते चले घंटे"},
    {"id": "hours_this_season", "type": "number", "min": 0, "max": 3000, "en": "Hours used this season", "hi": "इस सीज़न में चले घंटे"},
    {"id": "work_type", "type": "select", "en": "Main type of work", "hi": "मुख्य काम",
     "options": [["heavy", "Heavy ploughing", "भारी जुताई"], ["light", "Light work", "हल्का काम"], ["road", "Road transport", "सड़क पर ढुलाई"], ["harvest", "Harvesting", "कटाई"]]},
    {"id": "days_idle_30", "type": "number", "min": 0, "max": 30, "en": "Days NOT used in the last 30 days", "hi": "पिछले 30 दिनों में कितने दिन नहीं चली"},
    {"id": "storage", "type": "select", "en": "How is it stored?", "hi": "कहाँ रखी जाती है?",
     "options": [["indoors", "Indoors / shed", "शेड के अंदर"], ["outdoors", "Outdoors", "खुले में"], ["rain", "Outdoors, rain-exposed", "खुले में, बारिश में"]]},
    {"id": "last_service_date", "type": "date", "en": "Date of last service", "hi": "पिछली सर्विस की तारीख"},
    {"id": "service_done", "type": "multi", "en": "What was done at the last service?", "hi": "पिछली सर्विस में क्या हुआ?",
     "options": [["oil", "Engine oil", "इंजन ऑयल"], ["filters", "Filters", "फ़िल्टर"], ["coolant", "Coolant", "कूलेंट"], ["brakes", "Brakes", "ब्रेक"], ["hydraulics", "Hydraulics", "हाइड्रोलिक"], ["none", "Nothing / not sure", "कुछ नहीं / पता नहीं"]]},
    {"id": "fuel_age_months", "type": "number", "min": 0, "max": 36, "en": "How old is the fuel in the tank (months)?", "hi": "टंकी में ईंधन कितना पुराना है (महीने)?"},
]
