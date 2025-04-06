# 🧬 Volcano Plot Explorer 

A snappy interactive dashboard for visualizing gene expression data.

## Interactive Plot 🌋

- **Volcano plot** showing logFC vs p-values (with adjustable significance cutoff)
- **One-click exploration**: Tap any gene to see:
  - Expression boxplots (Young vs Old groups)
  - Relevant PubMed articles (fetched from  MyGene.info)

## Quick Start 🚀

1. Make sure you have the required files:
   - `data.csv`
   - `values.csv`

2. Install requirements:
   ```bash
   pip install dash plotly pandas numpy requests flask
   ```
3. Run the app using python connect to `127.0.0.1:5000` through your browser