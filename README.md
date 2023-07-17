# Biosynthetic Gene Cluster (BGC) activity prediction

Microorganisms produce a variety of secondary metabolites whose functions can be understood by studying their molecular structure, biosynthesis, and biological activity. Bioinformatics analysis of microbial genomes can reveal the genetic instructions for producing these Biosynthetic Gene Clusters (BGCs). antiSMASH is a popular tool that uses a rule-based method to predict BGCs in a given microbial genome. 

This app uses the genomic sequences of these BGCs to predict their potential biological activities using a machine-learning classifier. The features used in the classifier are derived from annotations of these BGCs (such as Pfam domains, smCOG annotations, etc.) together with information about resistomes predicted using the Resistance Gene Identifier (RGI). In this app, we specifically focus on antibiotic activity.

## BGC activity prediction

The BGC activity prediction workflow is illustrated below:
![Workflow](https://github.com/dileep-kishore/antibiotic-prediction/blob/main/assets/workflow.jpg?raw=true)

The BGC activity prediction app accepts a microbial genome in fasta format as input and processes it using antiSMASH and RGI to extract features. These features are used to predict the BGC function.

Features that are used for prediction:
- PFAM (from antiSMASH)
- CDS motif (from antiSMASH)
- smCOG (from antiSMASH)
- polyketide and non-ribosomal peptide monomer prediction annotations (from antiSMASH)
- Sequence Similarity Network of PFAM domains (from antiSMASH)
- Resistance gene markers (from RGI)

The classifiers used in this app are based on those published in Walker et al. 2021. They are trained using BGCs from the MiBIG (v1.4) database. Only those BGCs that has known antibiotic activities (types listed below), based on evidence in literature, were used for training the classifier. The workflow currently supports the prediction of four antibiotic activities:
1. Antibacterial
2. Antifungal
3. Antigrampositive
4. Antigramnegative

## Pipeline

The BGC activity prediction pipeline can be found at: https://github.com/dileep-kishore/antibiotic-prediction

It contains the following main modules:
1. `train_classifiers.sh` - Script that trains the classifiers for BGC activity prediction (antibacterial, antifungal, etc.)
2. `predict_function.sh` - Script that predict the activity of BGCs for a given genome
3. `multiple_predict_function.py` - Script that runs antismash and rgi and predicts the activity of a list of genomes

Example command to run the workflow:
```bash
python multiple_predict_function.py path/genome1 path/genome2 --output_dir outputs --no_SSN True
```

Supported classifiers (and roadmap):
1. Tree - `ExtraTreesClassifier` from scikit-learn
2. Support vector machine - `SVC` from scikit-learn (in progress)
3. Logistic regression - `SGDClassifier` from scikit-learn (in progress)

## References

- Medema, M. H. et al. antiSMASH: rapid identification, annotation and analysis of secondary metabolite biosynthesis gene clusters in bacterial and fungal genome sequences. Nucleic Acids Research 39, W339–W346 (2011).
- Alcock, B. P. et al. CARD 2023: expanded curation, support for machine learning, and resistome prediction at the Comprehensive Antibiotic Resistance Database. Nucleic Acids Res 51, D690–D699 (2023).
- Terlouw, B. R. et al. MIBiG 3.0: a community-driven effort to annotate experimentally validated biosynthetic gene clusters. Nucleic Acids Research 51, D603–D610 (2023).
- Walker, A. S. & Clardy, J. A Machine Learning Bioinformatics Method to Predict Biological Activity from Biosynthetic Gene Clusters. J. Chem. Inf. Model. 61, 2560–2571 (2021).
