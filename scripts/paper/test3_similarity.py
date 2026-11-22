"""Highest text similarity between test set 3's records and every training and development dossier record: character
3-to-5-gram TF-IDF cosine over the excerpts. Prints the overall maximum, the distribution of each test record's nearest
neighbour, and the closest pairs, for the paper's leakage statement.

Usage: uv run --with scikit-learn python scripts/paper/test3_similarity.py
"""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOSSIER = Path('data/dossier')


def scopes(name: str) -> set[str]:
    cases = json.loads((DOSSIER / name).read_text())
    listed = cases if isinstance(cases, list) else cases.get('cases', cases)
    rows = listed if isinstance(listed, list) else list(listed.values())
    return {case['scope'] for case in rows}


def main() -> None:
    records = json.loads((DOSSIER / 'evidence.json').read_text())['records']
    test, other = scopes('cases_heldout3.json'), scopes('cases.json')
    test_records = [r for r in records if r['scope'] in test]
    other_records = [r for r in records if r['scope'] in other]
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True)
    vectorizer.fit([r['excerpt'] for r in test_records + other_records])
    similarity = cosine_similarity(vectorizer.transform([r['excerpt'] for r in test_records]), vectorizer.transform([r['excerpt'] for r in other_records]))
    nearest = similarity.max(axis=1)
    order = nearest.argsort()[::-1]
    quantiles = {q: float(sorted(nearest)[int(q * (len(nearest) - 1))]) for q in (0.5, 0.9, 0.99)}
    print(json.dumps({'test_records': len(test_records), 'other_records': len(other_records), 'max': float(nearest.max()), 'nearest_quantiles': quantiles}))
    for i in order[:5]:
        j = similarity[i].argmax()
        print(
            f'{nearest[i]:.3f} {test_records[i]["id"]} <-> {other_records[j]["id"]}: {test_records[i]["excerpt"][:90]!r} | {other_records[j]["excerpt"][:90]!r}'
        )


if __name__ == '__main__':
    main()
