import re
from typing import List, Dict, Tuple


def parse_sentence_columns(md_text: str) -> Tuple[List[str], List[str]]:
    """Parses a markdown table to extract two columns of sentences."""
    sentences1: List[str] = []
    sentences2: List[str] = []
    lines = [ln.strip() for ln in md_text.splitlines() if ln.strip().startswith("|")]
    for ln in lines:
        cells = [c.strip() for c in ln.split("|")][1:-1]
        if len(cells) >= 3 and cells[0].replace("**", "").isdigit():
            sent1 = cells[1]
            sent2 = cells[2]
            sentences1.append(sent1)
            sentences2.append(sent2)
    return sentences1, sentences2


def parse_results_matrix(md_text: str) -> List[List[float]]:
    """Parses the all-pairs results matrix."""
    matrix: List[List[float]] = []
    lines = [ln.strip() for ln in md_text.splitlines() if ln.strip().startswith("| **")]
    for ln in lines:
        cells = [c.strip() for c in ln.split("|")][2:-1]  # Skip row header
        scores = [float(c) for c in cells]
        matrix.append(scores)
    return matrix


def main():
    import argparse
    import pathlib

    parser = argparse.ArgumentParser()
    parser.add_argument("--results_file", default="testresult.md")
    parser.add_argument("--testcase_file", default="testcase.md")
    parser.add_argument("--output_file", default="ranked_testresult.md")
    args = parser.parse_args()

    results_path = pathlib.Path(args.results_file)
    testcase_path = pathlib.Path(args.testcase_file)
    output_path = pathlib.Path(args.output_file)

    # Read source files
    results_text = results_path.read_text(encoding="utf-8")
    testcase_text = testcase_path.read_text(encoding="utf-8")

    # Parse data
    sentences1, sentences2 = parse_sentence_columns(testcase_text)
    score_matrix = parse_results_matrix(results_text)

    # Combine into a flat list of scored pairs
    scored_pairs: List[Dict] = []
    for i, s1 in enumerate(sentences1):
        for j, s2 in enumerate(sentences2):
            score = score_matrix[i][j]
            scored_pairs.append({"s1": s1, "s2": s2, "score": score, "idx1": i + 1, "idx2": j + 1})

    # Sort by score, descending
    scored_pairs.sort(key=lambda x: x["score"], reverse=True)

    # Format output
    output_lines = [
        "# 문장 유사도 점수 순위",
        ""
    ]
    for rank, item in enumerate(scored_pairs, start=1):
        output_lines.append(f"## 순위 {rank}")
        output_lines.append(f"**점수: {item['score']:.4f}** (입력문장1-{item['idx1']} vs 입력문장2-{item['idx2']})")
        output_lines.append(f"- **입력문장 1:** {item['s1']}")
        output_lines.append(f"- **입력문장 2:** {item['s2']}")
        output_lines.append("")

    output_path.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"Ranked results saved to {output_path}")


if __name__ == "__main__":
    main()
