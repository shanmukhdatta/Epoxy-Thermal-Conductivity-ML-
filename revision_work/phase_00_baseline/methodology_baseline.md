# Original-method baseline — not an endorsement

The research materials specify four ML algorithms in each of three temperature regimes: Extra Trees, Gradient Boosting, Random Forest, XGBoost (12 notebooks). In the archived model records the predictor fields include `Base TC`, `Filler TC`, `Vol`, and (for cryogenic/high-temperature datasets) `Temp`; `Composite TC` is the target. Room-temperature files do not have a `Temp` column. See original Excel and notebook files for exact schema and behavior.

A separate notebook `336 Data Augmentation.ipynb` generates proportional Gaussian noise. Its active call reportedly uses `noise_level=0.03`, while the three saved augmented file names specify 1% noise. **Do not change either in P0.**

The prior `revision_work/reports/original_pipeline_audit.md` claims augmentation preceded random train/test splitting and that performance estimates were contaminated by leakage. This is a pre-existing audit claim preserved in the frozen baseline, not a fresh independent validation in P0.

This baseline records historical artifacts; scientific corrections to data leakage, modeling, statistical validity and experimental comparisons belong to P1–P10.
