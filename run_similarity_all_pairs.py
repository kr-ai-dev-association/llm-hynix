import re
from typing import List, Tuple

from korean_similarity_evaluator import KoreanSimilarityEvaluator


def parse_sentence_columns(md_text: str) -> Tuple[List[str], List[str]]:
    """Parses a markdown table to extract two columns of sentences."""
    sentences1: List[str] = []
    sentences2: List[str] = []
    lines = [ln.strip() for ln in md_text.splitlines()]
    # 마크다운 테이블에서 "| 번호 | 문장1 | 문장2 |" 형태의 행을 찾습니다
    for ln in lines:
        if ln.startswith("|") and ln.endswith("|"):
            cells = [c.strip() for c in ln.split("|")][1:-1]
            if len(cells) >= 3 and cells[0].isdigit():
                sent1 = cells[1]
                sent2 = cells[2]
                sentences1.append(sent1)
                sentences2.append(sent2)
    return sentences1, sentences2


def main():
    import argparse
    import pathlib
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="testcase.md")
    parser.add_argument("--output", default="testresult.md")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    text = input_path.read_text(encoding="utf-8")
    sentences1, sentences2 = parse_sentence_columns(text)

    evaluator = KoreanSimilarityEvaluator(device=args.device)

    # Prepare markdown table output
    header = ["| 입력문장1 \\ 입력문장2 |"] + [f" {i+1} |" for i in range(len(sentences2))]
    align = ["| :--- |"] + [":---:|" for _ in range(len(sentences2))]

    rows: List[str] = ["".join(header), "".join(align)]

    for i, s1 in enumerate(sentences1):
        row = [f"| **{i+1}** |"]
        for j, s2 in enumerate(sentences2):
            result = evaluator.evaluate_pair(s1, s2)
            harmonic_mean = result["harmonic_mean"]
            row.append(f" {harmonic_mean:.4f} |")
        rows.append("".join(row))

    content = [
        "# 한국어 문장 유사도 평가 결과 (All-Pairs)",
        "",
        *rows,
    ]

    output_path.write_text("\n".join(content), encoding="utf-8")
    print(f"All-pairs similarity matrix saved to {output_path}")


if __name__ == "__main__":
    main()
