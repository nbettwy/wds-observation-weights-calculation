# wds-observation-weights-calculation
Computes observation weights for WDS binary star historical data files following Hartkopf et al. (2001).

## Description
This program reads a WDS historical data file for a single binary star system and computes an individual relative weight for each observation according to the following formula: W = W_technique * W_separation * sqrt(n) * W_quality

This program also computes mean weights by technique code group, which can be used as input values to orbital fitting software (e.g., Speckle Toolbox).

## Usage
1. Download your WDS historical data file.
2. Update the file path in the code.
3. Update any outlier exclusions in the code.
4. Run the script.
5. Check the output CSV file containing all computed weights.

## References
United States Naval Observatory, Sixth Catalog of Orbits of Visual Binary Stars, adopted from Hartkopf, et al., 2001 AJ 122, 3472, https://crf.usno.navy.mil/wds-orb6.
Washington Double Star Catalog. 2026. United States Naval Observatory, http://www.astro.gsu.edu/wds/.
