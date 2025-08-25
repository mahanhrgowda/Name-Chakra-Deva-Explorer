import streamlit as st
import pandas as pd
import plotly.express as px
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re

# Parser function to extract base consonants and vowels from ITRANS string
def extract_phonemes(itrans_name):
    base_consonants = ['kSh', 'Ng', 'Nj', 'Ch', 'Th', 'Dh', 'Sh', 'kh', 'gh', 'ch', 'jh', 'Th', 'Dh', 'ph', 'bh', 'sh', 'ph', 'bh', 'k', 'g', 'c', 'j', 'T', 'D', 't', 'd', 'p', 'b', 'm', 'y', 'r', 'l', 'v', 's', 'h', 'N']
    vowels_list = ['RRi', 'RRI', 'LLi', 'LLI', 'AI', 'AU', 'A', 'I', 'U', 'E', 'O', 'a', 'i', 'u', 'e', 'ai', 'au', 'o', 'M', 'H']
    consonants_found = []
    vowels_found = []
    i = 0
    while i < len(itrans_name):
        matched = False
        # Match longest consonant first
        for clen in range(3, 0, -1):  # Max length like 'kSh' = 3
            if i + clen <= len(itrans_name):
                sub = itrans_name[i:i + clen]
                if sub in base_consonants:
                    consonants_found.append(sub)
                    i += clen
                    matched = True
                    break
        if matched:
            # Check for following vowel (matra)
            vmatched = False
            for vlen in range(4, 0, -1):  # Max length like 'RRi' = 3
                if i + vlen <= len(itrans_name):
                    sub = itrans_name[i:i + vlen]
                    if sub in vowels_list:
                        vowels_found.append(sub)
                        i += vlen
                        vmatched = True
                        break
            if not vmatched:
                # Implicit 'a' if no vowel, but don't add to vowels (since not explicit)
                pass
            continue
        # If no consonant, match vowel
        for vlen in range(4, 0, -1):
            if i + vlen <= len(itrans_name):
                sub = itrans_name[i:i + vlen]
                if sub in vowels_list:
                    vowels_found.append(sub)
                    i += vlen
                    matched = True
                    break
        if not matched:
            i += 1  # Skip invalid chars
    return consonants_found, vowels_found

# Transliteration scheme mapping
scheme_map = {
    "ITRANS": sanscript.ITRANS,
    "Harvard-Kyoto": sanscript.HK,
    "SLP1": sanscript.SLP1,
    "Velthuis": sanscript.VELTHUIS,
    "WX": sanscript.WX
}
# Chakra mappings based on ITRANS transliterated consonants
chakra_mappings = {
    'ka': 'Anahata', 'kha': 'Anahata', 'ga': 'Anahata', 'gha': 'Anahata', 'Nga': 'Anahata',
    'cha': 'Anahata', 'Cha': 'Anahata', 'ja': 'Anahata', 'jha': 'Anahata', 'Nja': 'Anahata',
    'Ta': 'Anahata', 'Tha': 'Anahata',
    'Da': 'Manipura', 'Dha': 'Manipura', 'Na': 'Manipura', 'ta': 'Manipura', 'tha': 'Manipura',
    'da': 'Manipura', 'dha': 'Manipura', 'na': 'Manipura', 'pa': 'Manipura', 'pha': 'Manipura',
    'ba': 'Svadhisthana', 'bha': 'Svadhisthana', 'ma': 'Svadhisthana', 'ya': 'Svadhisthana',
    'ra': 'Svadhisthana', 'la': 'Svadhisthana',
    'va': 'Muladhara', 'sha': 'Muladhara', 'Sha': 'Muladhara', 'sa': 'Muladhara',
    'ha': 'Ajna', 'kSha': 'Ajna'
}
# Vowels for Vishuddha chakra in ITRANS
vowels = ['a', 'aa', 'i', 'ii', 'u', 'uu', 'RRi', 'RRI', 'LLi', 'LLI', 'e', 'ai', 'o', 'au', 'aM', 'aH']
# Bhava and Rasa mappings
bhava_rasa_mappings = {
    'Muladhara': {'bhava': 'Bhaya (Fear)', 'rasa': 'Bhayanaka (Fearful)', 'bhava_emoji': '😨', 'rasa_emoji': '😨', 'description': 'resonates with grounding and survival, evoking caution and alertness', 'emoji': '🔴', 'element': 'Earth'},
    'Svadhisthana': {'bhava': 'Rati (Love)', 'rasa': 'Shringara (Romantic)', 'bhava_emoji': '❤️', 'rasa_emoji': '❤️', 'description': 'flows with creativity and passion, igniting love and beauty', 'emoji': '🧡', 'element': 'Water'},
    'Manipura': {'bhava': 'Utsaha (Energy)', 'rasa': 'Veera (Heroic)', 'bhava_emoji': '💪', 'rasa_emoji': '💪', 'description': 'radiates confidence and power, inspiring courage and heroism', 'emoji': '🟡', 'element': 'Fire'},
    'Anahata': {'bhava': 'Rati (Love)', 'rasa': 'Shringara (Compassionate)', 'bhava_emoji': '❤️', 'rasa_emoji': '❤️', 'description': 'pulses with love and empathy, fostering deep connections', 'emoji': '💚', 'element': 'Air'},
    'Vishuddha': {'bhava': 'Hasya (Mirth)', 'rasa': 'Hasya (Comic)', 'bhava_emoji': '😂', 'rasa_emoji': '😂', 'description': 'vibrates with expression and joy, sparking laughter and communication', 'emoji': '🟦', 'element': 'Ether'},
    'Ajna': {'bhava': 'Vismaya (Astonishment)', 'rasa': 'Adbhuta (Wonder)', 'bhava_emoji': '😲', 'rasa_emoji': '😲', 'description': 'illuminates intuition and insight, evoking wonder and awe', 'emoji': '🟣', 'element': 'Light'}
}
# Chakra colors
chakra_colors = {
    'Muladhara': 'red',
    'Svadhisthana': 'orange',
    'Manipura': 'yellow',
    'Anahata': 'green',
    'Vishuddha': 'blue',
    'Ajna': 'indigo',
    'Vishuddha (Vowels)': 'blue'
}
# Deva dataset
deva_data = [
    {"Deva": "🌊 Varuṇa", "Type": "☀️ Āditya", "Chakra": "🟦 Viśuddha", "Element": "💧 Water", "Vāhana": "🐊 Makara", "Bīja": "🕉️ Om Vam Varuṇāya Namaḥ", "Description": "Guardian of cosmic order, ruling the vast oceans with truth", "Vahana_Symbolism": "Symbolizes mastery over water and emotions"},
    {"Deva": "🌞 Mitra", "Type": "☀️ Āditya", "Chakra": "💚 Anāhata", "Element": "🔆 Solar", "Vāhana": "🐎 Horse", "Bīja": "-", "Description": "Embodiment of friendship and harmony, shining with solar warmth", "Vahana_Symbolism": "Represents speed, freedom, and nobility"},
    {"Deva": "🛡️ Āryaman", "Type": "☀️ Āditya", "Chakra": "🟡 Maṇipūra", "Element": "🌞 Solar Dignity", "Vāhana": "-", "Bīja": "-", "Description": "Upholder of honor and nobility, radiating dignified energy", "Vahana_Symbolism": "No specific Vahana"},
    {"Deva": "💰 Bhaga", "Type": "☀️ Āditya", "Chakra": "🧡 Svādhiṣṭhāna", "Element": "🪙 Abundance", "Vāhana": "🦁 Lion", "Bīja": "🕉️ Om Bhagāya Namaḥ", "Description": "Bestower of prosperity, symbolizing wealth and strength", "Vahana_Symbolism": "Symbolizes strength and courage"},
    {"Deva": "🌗 Aṃśa", "Type": "☀️ Āditya", "Chakra": "🟣 Ājñā", "Element": "🥛 Soma-share", "Vāhana": "-", "Bīja": "-", "Description": "Distributor of divine nectar, fostering spiritual insight", "Vahana_Symbolism": "No specific Vahana"},
    {"Deva": "🛠️ Tvaṣṭṛ", "Type": "☀️ Āditya", "Chakra": "🔴 Mūlādhāra", "Element": "🧱 Creation", "Vāhana": "🐘 Elephant", "Bīja": "🕉️ Om Tvaṣṭre Namaḥ", "Description": "Divine craftsman, shaping creation with grounded wisdom", "Vahana_Symbolism": "Represents wisdom, power, and stability"},
    {"Deva": "☀️ Savitṛ", "Type": "☀️ Āditya", "Chakra": "⚪ Sahasrāra", "Element": "🌅 Solar Radiance", "Vāhana": "🌟 Golden Chariot", "Bīja": "🕉️ Tat Savitur Vareṇyam...", "Description": "Inspirer of enlightenment, radiating divine light", "Vahana_Symbolism": "Symbolizes the journey toward enlightenment"},
    {"Deva": "🧭 Pūṣan", "Type": "☀️ Āditya", "Chakra": "🟣 Ājñā", "Element": "🛤️ Guidance", "Vāhana": "🐐 Goat", "Bīja": "🕉️ Om Pūṣṇe Namaḥ", "Description": "Guide of travelers, illuminating paths with intuition", "Vahana_Symbolism": "Represents sure-footedness and guidance"},
    {"Deva": "📏 Dakṣa", "Type": "☀️ Āditya", "Chakra": "🟣 Ājñā", "Element": "📐 Order", "Vāhana": "🦁 Lion", "Bīja": "🕉️ Om Dakṣāya Namaḥ", "Description": "Master of cosmic order, ensuring balance and clarity", "Vahana_Symbolism": "Symbolizes strength and courage"},
    {"Deva": "☀️ Vivasvān", "Type": "☀️ Āditya", "Chakra": "⚪ Sahasrāra", "Element": "🔆 Light", "Vāhana": "🐎 Seven-Horse Chariot", "Bīja": "🕉️ Om Sūryāya Namaḥ", "Description": "Source of universal light, driving spiritual awakening", "Vahana_Symbolism": "Represents life-giving energy and movement"},
    {"Deva": "⚡ Indra", "Type": "☀️ Āditya", "Chakra": "🟡 Maṇipūra", "Element": "🔥 Energy", "Vāhana": "🐘 Airāvata", "Bīja": "🕉️ Om Indrāya Namaḥ", "Description": "King of gods, wielding thunderous energy and courage", "Vahana_Symbolism": "Represents wisdom, power, and royalty"},
    {"Deva": "🛡️ Viṣṇu", "Type": "☀️ Āditya", "Chakra": "🌈 All", "Element": "🛡️ Preserver", "Vāhana": "🦅 Garuḍa", "Bīja": "🕉️ Om Namo Nārāyaṇāya", "Description": "Preserver of the universe, harmonizing all energies", "Vahana_Symbolism": "Symbolizes speed and martial prowess"},
    {"Deva": "🔱 Śiva", "Type": "🌪️ Rudra", "Chakra": "🟣 Ājñā", "Element": "🌀 Destruction/Transformation", "Vāhana": "🐂 Bull (Nandi)", "Bīja": "🕉️ Om Namaḥ Śivāya", "Description": "Transformer of existence, guiding profound change", "Vahana_Symbolism": "Represents strength, fertility, and dharma"},
    {"Deva": "🔥 Manyu", "Type": "🌪️ Rudra", "Chakra": "🟡 Maṇipūra", "Element": "😠 Anger", "Vāhana": "🦁 Lion", "Bīja": "🕉️ Om Manyave Namaḥ", "Description": "Embodiment of fierce resolve, channeling intense energy", "Vahana_Symbolism": "Symbolizes strength and courage"},
    {"Deva": "🐯 Ugra", "Type": "🌪️ Rudra", "Chakra": "🔴 Mūlādhāra", "Element": "💪 Fierce Will", "Vāhana": "🐅 Tiger", "Bīja": "🕉️ Om Ugrāya Namaḥ", "Description": "Fierce warrior, grounding strength with determination", "Vahana_Symbolism": "Represents ferocity and power"},
    {"Deva": "📣 Bhīma", "Type": "🌪️ Rudra", "Chakra": "🟦 Viśuddha", "Element": "📢 Roar", "Vāhana": "🐘 Elephant", "Bīja": "-", "Description": "Resonator of mighty voice, amplifying expression", "Vahana_Symbolism": "Represents wisdom, power, and stability"},
    {"Deva": "🌀 Kapardī", "Type": "🌪️ Rudra", "Chakra": "⚪ Sahasrāra", "Element": "🔥 Tapas", "Vāhana": "🐂 Bull", "Bīja": "-", "Description": "Ascetic of divine focus, igniting spiritual fire", "Vahana_Symbolism": "Represents strength, fertility, and dharma"},
    {"Deva": "🌟 Raivata", "Type": "🌪️ Rudra", "Chakra": "🟣 Ājñā", "Element": "✨ Radiance", "Vāhana": "🦌 Deer", "Bīja": "-", "Description": "Bearer of radiant insight, illuminating wisdom", "Vahana_Symbolism": "Represents gentleness and swiftness"},
    {"Deva": "🐍 Sarpī", "Type": "🌪️ Rudra", "Chakra": "🔴 Mūlādhāra", "Element": "🐉 Kundalinī", "Vāhana": "🐍 Serpent", "Bīja": "🕉️ Saṃ", "Description": "Awakener of kundalini, rooted in primal energy", "Vahana_Symbolism": "Symbolizes transformation and healing"},
    {"Deva": "⚡ Vijra", "Type": "🌪️ Rudra", "Chakra": "🟣 Ājñā", "Element": "🎯 Focus", "Vāhana": "🦅 Lightning Bird", "Bīja": "-", "Description": "Sharpened focus, striking with divine precision", "Vahana_Symbolism": "Symbolizes speed and power"},
    {"Deva": "🌩️ Āśani", "Type": "🌪️ Rudra", "Chakra": "🟣 Ājñā", "Element": "⚡ Thunderbolt", "Vāhana": "☁️ Thundercloud", "Bīja": "-", "Description": "Wielder of thunder, sparking transformative insight", "Vahana_Symbolism": "Symbolizes storm energy and transformation"},
    {"Deva": "🌌 Mahān", "Type": "🌪️ Rudra", "Chakra": "⚪ Sahasrāra", "Element": "🌠 Greatness", "Vāhana": "🌠 Cosmic Mount", "Bīja": "-", "Description": "Embodiment of cosmic greatness, transcending limits", "Vahana_Symbolism": "Symbolizes transcendence and universality"},
    {"Deva": "🌿 Ṛtudhvaja", "Type": "🌪️ Rudra", "Chakra": "🧡 Svādhiṣṭhāna", "Element": "🌸 Cycle/Season", "Vāhana": "🛞 Chariot of Seasons", "Bīja": "-", "Description": "Ruler of seasonal cycles, flowing with nature’s rhythm", "Vahana_Symbolism": "Symbolizes cyclical time and harmony"},
    {"Deva": "🌊 Āpaḥ", "Type": "🪨 Vasu", "Chakra": "🧡 Svādhiṣṭhāna", "Element": "💧 Water", "Vāhana": "🐢 Turtle", "Bīja": "🕉️ Om Āpaḥ Svaḥ", "Description": "Essence of life-giving water, nurturing fluidity", "Vahana_Symbolism": "Represents longevity and stability"},
    {"Deva": "🧭 Dhruva", "Type": "🪨 Vasu", "Chakra": "⚪ Sahasrāra", "Element": "🧘 Stillness", "Vāhana": "🌌 Pole Star", "Bīja": "🪷 Dhruva Stuti", "Description": "Symbol of unwavering stillness, guiding eternal focus", "Vahana_Symbolism": "Represents steadfastness and guidance"},
    {"Deva": "🌙 Soma", "Type": "🪨 Vasu", "Chakra": "🟣 Ājñā", "Element": "🥛 Moon Nectar", "Vāhana": "🦌 Deer", "Bīja": "🕉️ Om Somāya Namaḥ", "Description": "Bearer of divine nectar, soothing with lunar calm", "Vahana_Symbolism": "Represents gentleness and swiftness"},
    {"Deva": "🌍 Dhara", "Type": "🪨 Vasu", "Chakra": "🔴 Mūlādhāra", "Element": "🌎 Earth", "Vāhana": "🐘 Elephant", "Bīja": "🕉️ Om Dhārayantyai Namaḥ", "Description": "Sustainer of earth, grounding with steadfast support", "Vahana_Symbolism": "Represents wisdom, power, and stability"},
    {"Deva": "💨 Anila", "Type": "🪨 Vasu", "Chakra": "💚 Anāhata", "Element": "🌬️ Air", "Vāhana": "🦌 Deer", "Bīja": "🕉️ Om Anilāya Namaḥ", "Description": "Breath of life, moving with airy grace", "Vahana_Symbolism": "Represents gentleness and swiftness"},
    {"Deva": "🔥 Anala", "Type": "🪨 Vasu", "Chakra": "🟡 Maṇipūra", "Element": "🔥 Fire", "Vāhana": "🐏 Ram", "Bīja": "🕉️ Om Agnaye Namaḥ", "Description": "Flame of transformation, burning with inner power", "Vahana_Symbolism": "Represents leadership and sacrifice"},
    {"Deva": "🌅 Pratyūṣa", "Type": "🪨 Vasu", "Chakra": "🟦 Viśuddha", "Element": "🌄 Dawn", "Vāhana": "🐎 Golden Horse", "Bīja": "-", "Description": "Herald of dawn, awakening vibrant expression", "Vahana_Symbolism": "Represents new beginnings and vitality"},
    {"Deva": "💡 Prabhāsa", "Type": "🪨 Vasu", "Chakra": "⚪ Sahasrāra", "Element": "💫 Radiance", "Vāhana": "🦚 Peacock", "Bīja": "-", "Description": "Source of radiant brilliance, illuminating divinity", "Vahana_Symbolism": "Symbolizes beauty and immortality"},
    {"Deva": "🌬️ Nāṣatya", "Type": "👬 Aśvin", "Chakra": "🌀 Iḍā", "Element": "🌬️ Breath (Left)", "Vāhana": "🐎 Horse", "Bīja": "🕉️ Om Nāsatye Namaḥ", "Description": "Healer of lunar breath, restoring balance", "Vahana_Symbolism": "Represents speed, freedom, and nobility"},
    {"Deva": "💪 Dasra", "Type": "👬 Aśvin", "Chakra": "🔥 Piṅgalā", "Element": "🔋 Vitality (Right)", "Vāhana": "🐎 Horse", "Bīja": "🕉️ Om Dasrāya Namaḥ", "Description": "Energizer of solar vitality, igniting strength", "Vahana_Symbolism": "Represents speed, freedom, and nobility"}
]
# Standardize chakra names
chakra_name_map = {
    'Mūlādhāra': 'Muladhara',
    'Svādhiṣṭhāna': 'Svadhisthana',
    'Maṇipūra': 'Manipura',
    'Anāhata': 'Anahata',
    'Viśuddha': 'Vishuddha',
    'Ājñā': 'Ajna',
    'Sahasrāra': 'Sahasrara',
    'Iḍā': 'Ida',
    'Piṅgalā': 'Pingala',
    'All': 'All'
}
devas_df = pd.DataFrame(deva_data)
devas_df['Chakra_Name'] = devas_df['Chakra'].apply(lambda x: chakra_name_map.get(x.split()[-1], x.split()[-1]))
# Page configuration
st.set_page_config(page_title="Name-Chakra-Deva Explorer", layout="wide")
st.title("🧘 Name-Chakra-Deva Explorer")
st.markdown("Discover how your name or phrase resonates with chakras, emotions (bhavas), aesthetic feelings (rasas), and Vedic Devas. Enter in English Latin script or Devanagari, or try an example like 'Om' or 'Gayatri Mantra'.")
# Tabs for navigation
tabs = st.tabs(["Name Analysis", "Deva Explorer", "Chakras", "Bhavas and Rasas", "Vedic Devas", "How It Works"])
# Name Analysis Tab
with tabs[0]:
    st.header("Name Analysis")
    examples = ["", "Rama", "Krishna", "Om", "Gayatri Mantra"]
    selected_example = st.selectbox("Try an Example", examples, help="Select an example to see its analysis.")
    input_method = st.radio("Input Method", ["Transliteration", "Devanagari"])
   
    if input_method == "Transliteration":
        transliteration_scheme = st.selectbox("Select Transliteration Scheme", list(scheme_map.keys()), help="Choose how your name is converted to Sanskrit. For example, in ITRANS, use 'rAma' for राम. See [Transliteration Guide](https://en.wikipedia.org/wiki/ITRANS).")
        name_input = st.text_input("Enter Name or Phrase in English Latin Script", value=selected_example if selected_example else "", placeholder="e.g., 'rAma' or 'Om Namah Shivaya'")
       
        if name_input:
            try:
                devanagari_name = transliterate(name_input, scheme_map[transliteration_scheme], sanscript.DEVANAGARI)
                # Transliterate to ITRANS for phoneme matching
                itrans_name = transliterate(name_input, scheme_map[transliteration_scheme], sanscript.ITRANS)
                st.write(f"Name/Phrase in Devanagari: {devanagari_name}")
               
                # Extract consonants and vowels in ITRANS using parser
                cons, vows = extract_phonemes(itrans_name)
                consonants_with_chakras = []
                for con in cons:
                    key = con + 'a'
                    if key in chakra_mappings:
                        consonants_with_chakras.append((key, chakra_mappings[key]))
                    else:
                        # Try lowercase/uppercase adjustment if not found (rare)
                        key_lower = con.lower() + 'a'
                        if key_lower in chakra_mappings:
                            consonants_with_chakras.append((key_lower, chakra_mappings[key_lower]))
                vowel_count = len([v for v in vows if v in vowels])
               
                if not consonants_with_chakras and not vowel_count:
                    st.error("No valid Sanskrit phonemes found. Try a different spelling or scheme.")
                else:
                    # Count chakra frequencies
                    chakra_counts = {'Muladhara': 0, 'Svadhisthana': 0, 'Manipura': 0, 'Anahata': 0, 'Vishuddha': 0, 'Ajna': 0}
                    for _, chakra in consonants_with_chakras:
                        chakra_counts[chakra] += 1
                   
                    # Find dominant chakra(s)
                    max_count = max(chakra_counts.values())
                    if max_count == 0 and vowel_count == 0:
                        st.error("No valid consonants or vowels to determine chakra.")
                    else:
                        dominant_chakras = [chakra for chakra, count in chakra_counts.items() if count == max_count and count > 0]
                        dominant_chakra = dominant_chakras[0] if dominant_chakras else 'Vishuddha' if vowel_count > 0 else None
                       
                        # Generate dynamic prose
                        prose = []
                        if max_count > 0:
                            dominant_letters = [char for char, chakra in consonants_with_chakras if chakra == dominant_chakra]
                            prose.append(f"For the name or phrase **{devanagari_name}**, the dominant chakra is **{dominant_chakra}** {bhava_rasa_mappings[dominant_chakra]['emoji']}, activated by the letters {', '.join(dominant_letters)}, which {bhava_rasa_mappings[dominant_chakra]['description']}.")
                            if len(dominant_chakras) > 1:
                                other_chakras = dominant_chakras[1:]
                                other_texts = [f"{chakra} {bhava_rasa_mappings[chakra]['emoji']} (letters {', '.join([char for char, chakra_ in consonants_with_chakras if chakra_ == chakra])})" for chakra in other_chakras]
                                prose.append(f"Additionally, the chakras {', '.join(other_texts)} are equally prominent, bringing their unique energies.")
                            prose.append(f"The dominant emotion is **{bhava_rasa_mappings[dominant_chakra]['bhava']}** {bhava_rasa_mappings[dominant_chakra]['bhava_emoji']}, evoking the **{bhava_rasa_mappings[dominant_chakra]['rasa']}** feeling {bhava_rasa_mappings[dominant_chakra]['rasa_emoji']}, embodying its essence.")
                            prose.append(f"This vibrant energy aligns with the element **{bhava_rasa_mappings[dominant_chakra]['element']}**, symbolizing its core qualities.")
                           
                            # Add Deva descriptions
                            associated_devas = devas_df[(devas_df['Chakra_Name'] == dominant_chakra) | (devas_df['Chakra_Name'] == 'All')].head(2)
                            if not associated_devas.empty:
                                deva_texts = [f"{row['Deva']}, {row['Description'].lower()}, whose {row['Vāhana'].lower()} vahana {row['Vahana_Symbolism'].lower()}" for _, row in associated_devas.iterrows()]
                                prose.append(f"It resonates with Devas like {', and '.join(deva_texts)}.")
                        if vowel_count > 0:
                            prose.append(f"Moreover, the {vowel_count} vowel{'s' if vowel_count > 1 else ''} activate the **Vishuddha** chakra {bhava_rasa_mappings['Vishuddha']['emoji']}, enhancing communication and self-expression.")
                        if max_count == 0 and vowel_count > 0:
                            prose = [f"The name or phrase **{devanagari_name}** consists only of vowels, primarily activating the **Vishuddha** chakra {bhava_rasa_mappings['Vishuddha']['emoji']}, which {bhava_rasa_mappings['Vishuddha']['description']}. The dominant emotion is **{bhava_rasa_mappings['Vishuddha']['bhava']}** {bhava_rasa_mappings['Vishuddha']['bhava_emoji']}, evoking the **{bhava_rasa_mappings['Vishuddha']['rasa']}** feeling {bhava_rasa_mappings['Vishuddha']['rasa_emoji']}, embodying its essence."]
                       
                        st.markdown(" ".join(prose))
                       
                        # Display associated Devas
                        if dominant_chakra:
                            st.subheader("Associated Vedic Devas")
                            associated_devas = devas_df[(devas_df['Chakra_Name'] == dominant_chakra) | (devas_df['Chakra_Name'] == 'All')]
                            if not associated_devas.empty:
                                for _, row in associated_devas.iterrows():
                                    with st.expander(f"{row['Deva']} ({row['Type']})"):
                                        st.markdown(f"""
                                        - **Chakra**: {row['Chakra']}
                                        - **Element**: {row['Element']}
                                        - **Vāhana**: {row['Vāhana']}
                                        - **Bīja Mantra**: {row['Bīja']}
                                        - **Description**: {row['Description']}
                                        - **Vahana Symbolism**: {row['Vahana_Symbolism']}
                                        """)
                            else:
                                st.write("No specific Devas are directly associated with this chakra.")
                       
                        # Bar chart for chakra distribution
                        st.subheader("Chakra Distribution")
                        chakra_df = pd.DataFrame(list(chakra_counts.items()), columns=['Chakra', 'Frequency'])
                        if vowel_count > 0:
                            chakra_df.loc[len(chakra_df)] = ['Vishuddha (Vowels)', vowel_count]
                        fig = px.bar(chakra_df, x='Chakra', y='Frequency', title='Chakra Distribution in Name', color='Chakra', color_discrete_map=chakra_colors)
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error processing name: {str(e)}. Ensure correct format for the selected scheme, e.g., 'rAma' for ITRANS. See [Transliteration Guide](https://en.wikipedia.org/wiki/ITRANS).")
    else:
        devanagari_name = st.text_input("Enter Name or Phrase in Devanagari", value=selected_example if selected_example and selected_example not in ["Rama", "Krishna", "Om", "Gayatri Mantra"] else "", placeholder="e.g., राम")
       
        if devanagari_name:
            try:
                # Validate Devanagari input
                if not any('\u0900' <= char <= '\u097F' for char in devanagari_name):
                    st.error("Please enter a valid Devanagari name or phrase.")
                else:
                    st.write(f"Name/Phrase in Devanagari: {devanagari_name}")
                    # Transliterate Devanagari to ITRANS for phoneme matching
                    itrans_name = transliterate(devanagari_name, sanscript.DEVANAGARI, sanscript.ITRANS)
                   
                    # Extract consonants and vowels in ITRANS using parser
                    cons, vows = extract_phonemes(itrans_name)
                    consonants_with_chakras = []
                    for con in cons:
                        key = con + 'a'
                        if key in chakra_mappings:
                            consonants_with_chakras.append((key, chakra_mappings[key]))
                        else:
                            key_lower = con.lower() + 'a'
                            if key_lower in chakra_mappings:
                                consonants_with_chakras.append((key_lower, chakra_mappings[key_lower]))
                    vowel_count = len([v for v in vows if v in vowels])
                   
                    if not consonants_with_chakras and not vowel_count:
                        st.error("No valid Sanskrit phonemes found in the name.")
                    else:
                        # Count chakra frequencies
                        chakra_counts = {'Muladhara': 0, 'Svadhisthana': 0, 'Manipura': 0, 'Anahata': 0, 'Vishuddha': 0, 'Ajna': 0}
                        for _, chakra in consonants_with_chakras:
                            chakra_counts[chakra] += 1
                       
                        # Find dominant chakra(s)
                        max_count = max(chakra_counts.values())
                        if max_count == 0 and vowel_count == 0:
                            st.error("No valid consonants or vowels to determine chakra.")
                        else:
                            dominant_chakras = [chakra for chakra, count in chakra_counts.items() if count == max_count and count > 0]
                            dominant_chakra = dominant_chakras[0] if dominant_chakras else 'Vishuddha' if vowel_count > 0 else None
                           
                            # Generate dynamic prose
                            prose = []
                            if max_count > 0:
                                dominant_letters = [char for char, chakra in consonants_with_chakras if chakra == dominant_chakra]
                                prose.append(f"For the name or phrase **{devanagari_name}**, the dominant chakra is **{dominant_chakra}** {bhava_rasa_mappings[dominant_chakra]['emoji']}, activated by the letters {', '.join(dominant_letters)}, which {bhava_rasa_mappings[dominant_chakra]['description']}.")
                                if len(dominant_chakras) > 1:
                                    other_chakras = dominant_chakras[1:]
                                    other_texts = [f"{chakra} {bhava_rasa_mappings[chakra]['emoji']} (letters {', '.join([char for char, chakra_ in consonants_with_chakras if chakra_ == chakra])})" for chakra in other_chakras]
                                    prose.append(f"Additionally, the chakras {', '.join(other_texts)} are equally prominent, bringing their unique energies.")
                                prose.append(f"The dominant emotion is **{bhava_rasa_mappings[dominant_chakra]['bhava']}** {bhava_rasa_mappings[dominant_chakra]['bhava_emoji']}, evoking the **{bhava_rasa_mappings[dominant_chakra]['rasa']}** feeling {bhava_rasa_mappings[dominant_chakra]['rasa_emoji']}, embodying its essence.")
                                prose.append(f"This vibrant energy aligns with the element **{bhava_rasa_mappings[dominant_chakra]['element']}**, symbolizing its core qualities.")
                               
                                # Add Deva descriptions
                                associated_devas = devas_df[(devas_df['Chakra_Name'] == dominant_chakra) | (devas_df['Chakra_Name'] == 'All')].head(2)
                                if not associated_devas.empty:
                                    deva_texts = [f"{row['Deva']}, {row['Description'].lower()}, whose {row['Vāhana'].lower()} vahana {row['Vahana_Symbolism'].lower()}" for _, row in associated_devas.iterrows()]
                                    prose.append(f"It resonates with Devas like {', and '.join(deva_texts)}.")
                            if vowel_count > 0:
                                prose.append(f"Moreover, the {vowel_count} vowel{'s' if vowel_count > 1 else ''} activate the **Vishuddha** chakra {bhava_rasa_mappings['Vishuddha']['emoji']}, enhancing communication and self-expression.")
                            if max_count == 0 and vowel_count > 0:
                                prose = [f"The name or phrase **{devanagari_name}** consists only of vowels, primarily activating the **Vishuddha** chakra {bhava_rasa_mappings['Vishuddha']['emoji']}, which {bhava_rasa_mappings['Vishuddha']['description']}. The dominant emotion is **{bhava_rasa_mappings['Vishuddha']['bhava']}** {bhava_rasa_mappings['Vishuddha']['bhava_emoji']}, evoking the **{bhava_rasa_mappings['Vishuddha']['rasa']}** feeling {bhava_rasa_mappings['Vishuddha']['rasa_emoji']}, embodying its essence."]
                           
                            st.markdown(" ".join(prose))
                           
                            # Display associated Devas
                            if dominant_chakra:
                                st.subheader("Associated Vedic Devas")
                                associated_devas = devas_df[(devas_df['Chakra_Name'] == dominant_chakra) | (devas_df['Chakra_Name'] == 'All')]
                                if not associated_devas.empty:
                                    for _, row in associated_devas.iterrows():
                                        with st.expander(f"{row['Deva']} ({row['Type']})"):
                                            st.markdown(f"""
                                            - **Chakra**: {row['Chakra']}
                                            - **Element**: {row['Element']}
                                            - **Vāhana**: {row['Vāhana']}
                                            - **Bīja Mantra**: {row['Bīja']}
                                            - **Description**: {row['Description']}
                                            - **Vahana Symbolism**: {row['Vahana_Symbolism']}
                                            """)
                                else:
                                    st.write("No specific Devas are directly associated with this chakra.")
                           
                            # Bar chart for chakra distribution
                            st.subheader("Chakra Distribution")
                            chakra_df = pd.DataFrame(list(chakra_counts.items()), columns=['Chakra', 'Frequency'])
                            if vowel_count > 0:
                                chakra_df.loc[len(chakra_df)] = ['Vishuddha (Vowels)', vowel_count]
                            fig = px.bar(chakra_df, x='Chakra', y='Frequency', title='Chakra Distribution in Name', color='Chakra', color_discrete_map=chakra_colors)
                            st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error processing name: {str(e)}. Ensure the name contains valid Devanagari characters.")
# Deva Explorer Tab
with tabs[1]:
    st.header("Deva Explorer")
    st.markdown("Explore the 33 Vedic Devas, their associated chakras, elements, vāhanas, and mantras.")
   
    for _, row in devas_df.iterrows():
        with st.expander(f"{row['Deva']} ({row['Type']})"):
            st.markdown(f"""
            - **Chakra**: {row['Chakra']}
            - **Element**: {row['Element']}
            - **Vāhana**: {row['Vāhana']}
            - **Bīja Mantra**: {row['Bīja']}
            - **Description**: {row['Description']}
            - **Vahana Symbolism**: {row['Vahana_Symbolism']}
            """)
# Chakras Tab
with tabs[2]:
    st.header("Chakras")
    st.markdown("Chakras are energy centers in the body, each linked to specific Sanskrit phonemes and qualities. Learn more at [Sanskrit and Chakras](https://www.ruhgu.com/sanskrit-and-chakras/).")
   
    chakras = [
        {"Name": "Muladhara", "Emoji": "🔴", "Description": "Resonates with grounding and survival, evoking caution and alertness", "Letters": "va, sha, Sha, sa", "Element": "Earth"},
        {"Name": "Svadhisthana", "Emoji": "🧡", "Description": "Flows with creativity and passion, igniting love and beauty", "Letters": "ba, bha, ma, ya, ra, la", "Element": "Water"},
        {"Name": "Manipura", "Emoji": "🟡", "Description": "Radiates confidence and power, inspiring courage and heroism", "Letters": "Da, Dha, Na, ta, tha, da, dha, na, pa, pha", "Element": "Fire"},
        {"Name": "Anahata", "Emoji": "💚", "Description": "Pulses with love and empathy, fostering deep connections", "Letters": "ka, kha, ga, gha, Nga, cha, Cha, ja, jha, Nja, Ta, Tha", "Element": "Air"},
        {"Name": "Vishuddha", "Emoji": "🟦", "Description": "Vibrates with expression and joy, sparking laughter and communication", "Letters": "a, aa, i, ii, u, uu, RRi, RRI, LLi, LLI, e, ai, o, au, aM, aH", "Element": "Ether"},
        {"Name": "Ajna", "Emoji": "🟣", "Description": "Illuminates intuition and insight, evoking wonder and awe", "Letters": "ha, kSha", "Element": "Light"}
    ]
   
    for chakra in chakras:
        st.subheader(f"{chakra['Emoji']} {chakra['Name']}")
        st.markdown(f"""
        - **Description**: {chakra['Description']}.
        - **Element**: {chakra['Element']}
        - **Associated Phonemes**: {chakra['Letters']}
        """)
# Bhavas and Rasas Tab
with tabs[3]:
    st.header("Bhavas and Rasas")
    st.markdown("Bhavas are emotive states, and rasas are aesthetic emotions from Indian classical arts, as described in the Natyashastra. The connections to chakras are modern interpretations, not traditional facts. Learn more at [Rasa Aesthetics](https://en.wikipedia.org/wiki/Rasa_(aesthetics)).")
   
    for chakra, info in bhava_rasa_mappings.items():
        st.subheader(f"{info['emoji']} {chakra}")
        st.markdown(f"""
        - **Bhava (Emotion)**: {info['bhava']} {info['bhava_emoji']}
        - **Rasa (Aesthetic Feeling)**: {info['rasa']} {info['rasa_emoji']}
        - **Description**: {info['description'].capitalize()}.
        - **Element**: {info['element']}
        """)
# Vedic Devas Tab
with tabs[4]:
    st.header("Vedic Devas")
    st.markdown("The 33 Vedic Devas are divine forces in Hinduism, including 12 Ādityas, 11 Rudras, 8 Vasus, and 2 Aśvins. Each is associated with specific energies and qualities. Learn more at [Hindu Deities](https://en.wikipedia.org/wiki/Hindu_deities).")
    st.write("Explore the Devas in the 'Deva Explorer' tab to learn about their chakras, elements, vāhanas, and mantras.")
# How It Works Tab
with tabs[5]:
    st.header("How It Works")
    st.markdown("""
    This app analyzes your name or phrase by converting it to Sanskrit (Devanagari) script. Each consonant is mapped to a chakra based on traditional Sanskrit petal associations, using English transliterations (ITRANS scheme), and vowels activate the Vishuddha chakra. The chakra with the most phonemes is considered dominant, with ties noted as significant influences. Emotions (bhavas) and aesthetic feelings (rasas) are assigned based on the dominant chakra, creating a personalized story. The narrative includes connections to Vedic Devas, describing their roles and vahana symbolisms. The mappings are interpretive, blending traditional phonetics with modern creativity. For more on Sanskrit and chakras, visit [Sanskrit and Chakras](https://www.ruhgu.com/sanskrit-and-chakras/).
   
    **Input Options**:
    - **Transliteration**: Enter in English Latin script using a scheme like ITRANS ('rAma' for राम). Choose a scheme from the dropdown. See [Transliteration Schemes](https://en.wikipedia.org/wiki/ITRANS).
    - **Devanagari**: Type directly in Sanskrit script (e.g., राम) if you have a Devanagari keyboard.
    """)
