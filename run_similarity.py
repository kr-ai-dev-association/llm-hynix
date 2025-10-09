import re
from typing import List, Tuple

from korean_similarity_evaluator import KoreanSimilarityEvaluator


def parse_table_lines(md_text: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    lines = [ln.strip() for ln in md_text.splitlines()]
    # 마크다운 테이블에서 "| 번호 | 문장1 | 문장2 |" 형태의 행을 찾습니다
    for ln in lines:
        if ln.startswith("|") and ln.endswith("|"):
            cells = [c.strip() for c in ln.split("|")][1:-1]
            if len(cells) >= 3 and cells[0].isdigit():
                sent1 = cells[1]
                sent2 = cells[2]
                pairs.append((sent1, sent2))
    return pairs


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
    pairs = parse_table_lines(text)

    evaluator = KoreanSimilarityEvaluator(device=args.device)

    rows: List[str] = []
    rows.append("| 번호 | BLEU | ROUGE-L | METEOR | BERTScore(F1) | 조화평균 |")
    rows.append("| :--- | :---: | :---: | :---: | :---: | :---: |")

    for idx, (s1, s2) in enumerate(pairs, start=1):
        result = evaluator.evaluate_pair(s1, s2)
        rows.append(
            f"| {idx} | {result['bleu']:.4f} | {result['rouge_l']:.4f} | {result['meteor']:.4f} | {result['bertscore_f1']:.4f} | {result['harmonic_mean']:.4f} |"
        )

    # 각 쌍별 상세 점수와 원문을 함께 기록합니다
    details: List[str] = []
    details.append("## 입력 문장 쌍과 점수")
    for idx, (s1, s2) in enumerate(pairs, start=1):
        result = evaluator.evaluate_pair(s1, s2)
        details.append(f"### 케이스 {idx}")
        details.append(f"- 문장 1: {s1}")
        details.append(f"- 문장 2: {s2}")
        details.append(
            f"- 점수: BLEU={result['bleu']:.4f}, ROUGE-L={result['rouge_l']:.4f}, METEOR={result['meteor']:.4f}, BERTScore(F1)={result['bertscore_f1']:.4f}, 조화평균={result['harmonic_mean']:.4f}"
        )

    content = []
    content.append("# 한국어 문장 유사도 평가 결과")
    content.append("")
    content.extend(rows)
    content.append("")
    content.extend(details)

    output_path.write_text("\n".join(content), encoding="utf-8")


if __name__ == "__main__":
    main()


