import streamlit as st
import streamlit.components.v1 as components
import requests
import py3Dmol
from predict_proteins import MC_NEST_gpt4o

# ESMFold prediction API
def predict_structure(sequence):
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=sequence, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Failed to predict structure: {response.status_code}")
        return None

def show_structure(pdb_data, name):
    st.subheader(f"{name}")
    view = py3Dmol.view(width=350, height=400)
    view.addModel(pdb_data, "pdb")
    view.setStyle({"cartoon": {"color": "spectrum"}})
    view.zoomTo()
    view.setBackgroundColor("white")
    html = view._make_html()
    components.html(html, height=400)

# Streamlit UI
st.title("Protein Structure Prediction with MC-NEST")
st.write("Enter a protein sequence (e.g., FOXM1) to predict and visualize its structure.")

default_sequence = "MARTKQTARKSTGGKAPRKQLASKAARKSAARAAAAGGGGGGG"
sequence_input = st.text_area("Protein Sequence", value=default_sequence, height=150)

if st.button("Predict & Visualize"):
    if sequence_input.strip():
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("Predicting structure for FOXM1...")
            pdb1 = predict_structure(sequence_input.strip())
            if pdb1:
                show_structure(pdb1, "FOXM1 Structure")
        with col2:
            # Placeholder in col2
            with st.spinner("Loading data in col2..."):
                sequence = sequence_input.strip()
                segments = {
                    "sv40_nls": sequence[0:10],      # MARTKQTARK
                    "spacer": sequence[10:35],       # STGGKAPRKQLASKAARKSAARAAAA
                    "gly_linker": sequence[35:]      # GGGGGGG
                }
                # Properly formatted background information string
                background_info = f"""
                The sequence {sequence} is a synthetic peptide widely utilized in molecular biology and biomedical research. The first segment, "{segments['sv40_nls']}," is derived from the simian virus 40 (SV40) large T-antigen and functions as a nuclear localization signal (NLS), directing the transport of proteins into the cell nucleus (Kalderon et al., 1984). The following segment, "{segments['spacer']}," acts as a spacer, providing flexibility and minimizing steric hindrance between protein domains when used in fusion proteins, a strategy often employed in protein engineering (Chatterjee et al., 2014). The final part, "{segments['gly_linker']}," consists of six glycine residues and serves as a flexible linker, allowing for free movement between adjacent protein domains (Strop et al., 2008). This peptide is particularly useful for studying nuclear processes, protein-protein interactions, and recombinant protein engineering (Fahmy et al., 2005). It enhances the solubility and functionality of fusion proteins and aids in targeting proteins to the nucleus (Caron et al., 2010). Researchers must consider the potential for non-specific interactions and the context-dependent behavior of synthetic peptides, ensuring the NLS and linker sequences function properly in the specific experimental context (Zhou et al., 2013). Overall, this peptide plays a crucial role in advancing our understanding of protein dynamics and interactions within cellular systems.
                """

                # Ensure you have the proper constants defined (use the original definitions from your code)
                IMPORTANCE_SAMPLING = 2  # Selection policy constant
                ZERO_SHOT = 1  # Initialization strategy constant

                # Assuming you have the MC_NEST_gpt4o class already defined
                mc_nest = MC_NEST_gpt4o(
                    background_information=background_info,
                    max_rollouts=2,  # Number of rollouts to perform
                    selection_policy=IMPORTANCE_SAMPLING,  # Selection policy (GREEDY, IMPORTANCE_SAMPLING, etc.)
                    initialize_strategy=ZERO_SHOT  # Initialization strategy (ZERO_SHOT or DUMMY_ANSWER)
                )

                # Run the Monte Carlo NEST algorithm
                best_hypothesis = mc_nest.run()
                
                # Protein sequences (replace these with your actual sequences)
                myc = mc_nest.protein_sequences['modified_sequence']
                protein_sequences = {
                    "FOXM1": f"{sequence}",
                    "MYC": myc
                }
                st.info("Predicting structure for MYC...")
                pdb2 = predict_structure(protein_sequences["MYC"])
                if pdb2:
                    show_structure(pdb2, "MYC Structure")
        st.success(best_hypothesis)
    else:
        st.warning("Please enter a valid protein sequence.")