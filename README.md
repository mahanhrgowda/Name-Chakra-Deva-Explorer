# PLC Streamlit Tool

A lightweight **Streamlit WebApp** that combines **Phonetics, Grammar**, and **Clustering** into one educational and interactive tool.

### 🔍 Features

- 🧠 **Phoneme Extraction** — Break down any English sentence into its constituent phonemes.
- 🧾 **Grammar Tagging** — Apply Part-of-Speech (POS) tagging using NLTK.
- 📊 **Clustering Visualization** — Visualize semantic sentence differences using PCA and t-SNE projections.
- 🧰 **Plug-and-Play** — Ready for use in classrooms, workshops, or NLP playgrounds.

---

### 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/plc-streamlit-tool.git
cd plc-streamlit-tool

# 2. Set up your environment
pip install -r requirements.txt

# 3. Run the app
streamlit run plc_streamlit_tool/app.py
```

---

### 📁 Project Structure

```
plc_streamlit_tool/
├── app.py                      ← Streamlit main interface
├── plc_phonetics.py           ← Extract basic phonemes
├── plc_grammar.py             ← NLTK POS tagging logic
├── plc_clustering.py          ← PCA/t-SNE clustering plots
├── plc_utils.py               ← File loader utilities
├── requirements.txt           ← Dependencies
├── assets/
│   ├── phoneme_map.json       ← Sample phoneme type mapping
│   └── sample_sentences.txt   ← Example inputs
└── .streamlit/
    └── config.toml            ← Streamlit config
```

---

### 📚 Future Ideas

- 🌐 Add IPA or Sanskrit phoneme mapping
- 🎨 Live color-coded waveform visualization
- 🤖 Trainable Bhāva/Intent model
- 📦 Export to QR, audio, or vector space

---

Made with ❤️ using Streamlit.