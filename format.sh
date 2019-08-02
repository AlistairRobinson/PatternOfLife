python3 formatter.py -f testset.csv -i 1 > fingerprint.csv
python3 formatter.py -f testset.csv -i 0 > combined.csv
python3 formatter.py -f fingerprint.csv -i 0 -p > fingerprint_pivot.csv
python3 formatter.py -f combined.csv -i 0 -p > combined_pivot.csv